#!/usr/bin/env python3
"""
将 GitLab issues 导入到 Jira DEV 项目

用法:
    # 方式1: 使用 GitLab API Token 自动获取
    python3 import-gitlab-issues.py --gitlab-token <token>
    
    # 方式2: 从 JSON 文件导入（手动导出）
    python3 import-gitlab-issues.py --from-file issues.json
    
    # 方式3: 从 CSV 文件导入
    python3 import-gitlab-issues.py --from-csv issues.csv

环境变量:
    JIRA_TOKEN: Jira API Token（从 macOS Keychain 自动获取）
    GITLAB_TOKEN: GitLab API Token
"""

import argparse
import json
import subprocess
import sys
import re
from typing import List, Dict, Optional

# 配置
GITLAB_URL = "https://gitee.52emp.com"
PROJECT_PATH = "caidao-web-project/aida"
JIRA_URL = "http://jira.caidaocloud.com:8080"
JIRA_PROJECT = "DEV"
JIRA_COMPONENT_ID = "10805"  # "2.0" 组件
JIRA_BOARD_ID = "45"


def get_jira_token() -> str:
    """从 macOS Keychain 获取 Jira token"""
    # 先获取用户名
    result = subprocess.run(
        ["jira", "me"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("❌ 无法获取 Jira 用户，请确保 jira-cli 已配置", file=sys.stderr)
        sys.exit(1)
    jira_user = result.stdout.strip()
    
    # 从 keychain 获取 token
    result = subprocess.run(
        ["security", "find-generic-password", "-s", "jira-cli", "-a", jira_user, "-w"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("❌ 无法获取 Jira token，请确保已配置 jira-cli", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def get_jira_user() -> str:
    """获取当前 Jira 用户"""
    result = subprocess.run(
        ["jira", "me"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("❌ 无法获取 Jira 用户，请确保 jira-cli 已配置", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def get_next_sprint_id(token: str, user: str) -> Optional[str]:
    """获取下一个 Sprint ID"""
    cmd = [
        "curl", "-s", "-X", "GET",
        "-u", f"{user}:{token}",
        f"{JIRA_URL}/rest/agile/1.0/board/{JIRA_BOARD_ID}/sprint?state=future"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    
    try:
        data = json.loads(result.stdout)
        if data.get("values"):
            return data["values"][0]["id"]
    except json.JSONDecodeError:
        pass
    return None


def fetch_gitlab_issues(gitlab_token: str) -> List[Dict]:
    """从 GitLab API 获取 issues"""
    import urllib.parse
    
    project_encoded = urllib.parse.quote(PROJECT_PATH, safe="")
    url = f"{GITLAB_URL}/api/v4/projects/{project_encoded}/issues?state=all&per_page=100"
    
    cmd = [
        "curl", "-s", "-L",
        "-H", f"PRIVATE-TOKEN: {gitlab_token}",
        url
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 获取 GitLab issues 失败: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    
    try:
        issues = json.loads(result.stdout)
        if isinstance(issues, list):
            return issues
        elif isinstance(issues, dict) and "message" in issues:
            print(f"❌ GitLab API 错误: {issues['message']}", file=sys.stderr)
            sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ 解析 GitLab 响应失败: {e}", file=sys.stderr)
        sys.exit(1)
    
    return []


def load_issues_from_file(filepath: str) -> List[Dict]:
    """从 JSON 文件加载 issues"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and "issues" in data:
        return data["issues"]
    else:
        return [data]


def load_issues_from_csv(filepath: str) -> List[Dict]:
    """从 CSV 文件加载 issues"""
    import csv
    
    issues = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            issue = {
                "title": row.get("title", ""),
                "description": row.get("description", ""),
                "state": row.get("state", "opened"),
                "labels": row.get("labels", "").split(",") if row.get("labels") else []
            }
            issues.append(issue)
    return issues


def create_jira_issue(issue: Dict, token: str, user: str) -> Optional[str]:
    """在 Jira 创建 issue，返回 issue key"""
    
    # 提取标题和描述
    title = issue.get("title", "")
    description = issue.get("description", "")
    
    # 清理标题（移除 GitLab issue 编号前缀如 #123）
    title = re.sub(r'^#\d+\s*', '', title)
    
    # 添加 GitLab 来源标记
    gitlab_url = issue.get("web_url", "")
    if gitlab_url:
        description = f"*GitLab Issue:* {gitlab_url}\n\n{description}"
    
    # 确定优先级
    labels = issue.get("labels", [])
    priority = "Medium"
    if "P0" in labels or "priority::P0" in labels:
        priority = "Highest"
    elif "P1" in labels or "priority::P1" in labels:
        priority = "High"
    elif "P2" in labels or "priority::P2" in labels:
        priority = "Medium"
    
    # 构建请求体
    payload = {
        "fields": {
            "project": {"key": JIRA_PROJECT},
            "summary": title,
            "description": description,
            "issuetype": {"name": "故事"},
            "priority": {"name": priority},
            "components": [{"id": JIRA_COMPONENT_ID}]
        }
    }
    
    # 创建 issue
    cmd = [
        "curl", "-s", "-X", "POST",
        "-u", f"{user}:{token}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload, ensure_ascii=False),
        f"{JIRA_URL}/rest/api/2/issue"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    try:
        response = json.loads(result.stdout)
        if "key" in response:
            return response["key"]
        elif "errorMessages" in response:
            print(f"❌ 创建失败: {response['errorMessages']}", file=sys.stderr)
            return None
    except json.JSONDecodeError:
        print(f"❌ 解析响应失败: {result.stdout}", file=sys.stderr)
        return None
    
    return None


def add_to_sprint(issue_key: str, sprint_id: str, token: str, user: str) -> bool:
    """将 issue 添加到 Sprint"""
    cmd = [
        "curl", "-s", "-X", "POST",
        "-u", f"{user}:{token}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"issues": [issue_key]}),
        f"{JIRA_URL}/rest/agile/1.0/sprint/{sprint_id}/issue"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def assign_issue(issue_key: str, user: str, token: str) -> bool:
    """分配 issue 给当前用户"""
    cmd = [
        "curl", "-s", "-X", "PUT",
        "-u", f"{user}:{token}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"fields": {"assignee": {"name": user}}}),
        f"{JIRA_URL}/rest/api/2/issue/{issue_key}"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="将 GitLab issues 导入到 Jira")
    parser.add_argument("--gitlab-token", help="GitLab API Token")
    parser.add_argument("--from-file", help="从 JSON 文件导入")
    parser.add_argument("--from-csv", help="从 CSV 文件导入")
    parser.add_argument("--dry-run", action="store_true", help="试运行，不实际创建")
    parser.add_argument("--skip-sprint", action="store_true", help="跳过添加到 Sprint")
    
    args = parser.parse_args()
    
    # 获取 Jira 认证信息
    print("🔐 获取 Jira 认证信息...")
    jira_user = get_jira_user()
    jira_token = get_jira_token()
    print(f"✅ Jira 用户: {jira_user}")
    
    # 获取 issues
    if args.gitlab_token:
        print("📥 从 GitLab API 获取 issues...")
        issues = fetch_gitlab_issues(args.gitlab_token)
    elif args.from_file:
        print(f"📂 从文件加载 issues: {args.from_file}")
        issues = load_issues_from_file(args.from_file)
    elif args.from_csv:
        print(f"📂 从 CSV 加载 issues: {args.from_csv}")
        issues = load_issues_from_csv(args.from_csv)
    else:
        print("❌ 请提供 --gitlab-token、--from-file 或 --from-csv", file=sys.stderr)
        sys.exit(1)
    
    print(f"📋 找到 {len(issues)} 个 issues")
    
    if not issues:
        print("⚠️ 没有 issues 需要导入")
        return
    
    # 获取 Sprint ID
    sprint_id = None
    if not args.skip_sprint:
        sprint_id = get_next_sprint_id(jira_token, jira_user)
        if sprint_id:
            print(f"📅 目标 Sprint ID: {sprint_id}")
        else:
            print("⚠️ 无法获取 Sprint ID，将跳过添加到 Sprint")
    
    # 预览模式
    if args.dry_run:
        print("\n🔍 试运行模式，以下 issues 将被创建:\n")
        for i, issue in enumerate(issues[:10], 1):
            title = issue.get("title", "")
            print(f"{i}. {title[:80]}")
        if len(issues) > 10:
            print(f"... 还有 {len(issues) - 10} 个")
        return
    
    # 确认
    print(f"\n⚠️ 将创建 {len(issues)} 个 Jira issues")
    print("组件: 2.0 (AI)")
    if sprint_id:
        print(f"Sprint: {sprint_id}")
    print("\n确认导入? (y/N): ", end="")
    
    try:
        response = input().strip().lower()
        if response not in ("y", "yes"):
            print("❌ 已取消")
            return
    except EOFError:
        print("\n❌ 需要交互式确认")
        return
    
    # 创建 issues
    print("\n🚀 开始导入...\n")
    created = []
    failed = []
    
    for i, issue in enumerate(issues, 1):
        title = issue.get("title", "")[:60]
        print(f"[{i}/{len(issues)}] {title}...", end=" ")
        
        issue_key = create_jira_issue(issue, jira_token, jira_user)
        if issue_key:
            print(f"✅ {issue_key}")
            created.append(issue_key)
            
            # 添加到 Sprint
            if sprint_id:
                if add_to_sprint(issue_key, sprint_id, jira_token, jira_user):
                    print(f"   📅 已添加到 Sprint")
                else:
                    print(f"   ⚠️ 添加到 Sprint 失败")
            
            # 分配给自己
            if assign_issue(issue_key, jira_user, jira_token):
                print(f"   👤 已分配")
        else:
            print("❌ 失败")
            failed.append(title)
    
    # 总结
    print(f"\n{'='*60}")
    print(f"✅ 成功创建: {len(created)} 个")
    if failed:
        print(f"❌ 失败: {len(failed)} 个")
    print(f"{'='*60}")
    
    if created:
        print("\n创建的 issues:")
        for key in created:
            print(f"  - {JIRA_URL}/browse/{key}")


if __name__ == "__main__":
    main()
