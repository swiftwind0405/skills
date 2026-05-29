#!/usr/bin/env python3
"""
查询钉钉 AI 表格中分配给你的 AI 需求任务

用法:
    ai-tasks.py              # 显示所有分配给你的任务
    ai-tasks.py --p0         # 只显示 P0 优先级
    ai-tasks.py --p1         # 只显示 P1 优先级
    ai-tasks.py --p2         # 只显示 P2 优先级
    ai-tasks.py --todo       # 只显示未开始/开发中的任务
    ai-tasks.py --testing    # 只显示待测试的任务
    ai-tasks.py --mine       # 只显示你负责的任务（默认）
    ai-tasks.py --all        # 显示所有 AI 任务（不只是你的）
"""

import subprocess
import json
import sys
import argparse
import os
from datetime import datetime

# 配置
BASE_ID = "bva6QBXJwaj5lgqzHo1QEn7oWn4qY5Pr"
TABLE_ID = "hERWDMS"
MY_USER_ID = "0568460913-1915884507"
DWS_CLI = os.path.expanduser("~/bin/dws")

# AI 需求视图的过滤条件
AI_FILTER = '{"operator":"and","operands":[{"operator":"any_of","operands":["m0Ut7no",["VXEIYQWovF"]]},{"operator":"none_of","operands":["4pbE3Wq",["A5gMBTncli","XTZdol4AI6","n2KV6H7hdQ","HuDkOiSShA","Igw0iip29K","S2sr8pY9ie","EfFB5NjStj","pmrfI7zruk"]]}]}'

def fetch_records():
    """从钉钉 AI 表格获取记录"""
    cmd = [
        DWS_CLI, "aitable", "record", "query",
        "--base-id", BASE_ID,
        "--table-id", TABLE_ID,
        "--filters", AI_FILTER,
        "--limit", "100",
        "--format", "json"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, shell=False)
    if result.returncode != 0:
        print(f"❌ 查询失败: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    
    return json.loads(result.stdout)

def parse_tasks(data, my_user_id=None):
    """解析任务数据"""
    records = data['data']['records']
    tasks = []
    
    for record in records:
        cells = record['cells']
        task_desc = cells.get('01ZM8y7', '')
        status_obj = cells.get('4pbE3Wq', {})
        status = status_obj.get('name', '未知') if isinstance(status_obj, dict) else '未知'
        priority_obj = cells.get('9XFXz5d', {})
        priority = priority_obj.get('name', '无') if isinstance(priority_obj, dict) else '无'
        
        # 获取负责人信息
        backend_devs = cells.get('N4FSW5T', []) or []
        frontend_devs = cells.get('NAirB4G', []) or []
        pm_devs = cells.get('S7EHHD4', []) or []
        
        backend_names = [d.get('userId', '') for d in backend_devs]
        frontend_names = [d.get('userId', '') for d in frontend_devs]
        pm_names = [d.get('userId', '') for d in pm_devs]
        
        is_mine = False
        roles = []
        
        if my_user_id:
            if my_user_id in backend_names:
                is_mine = True
                roles.append('后端')
            if my_user_id in frontend_names:
                is_mine = True
                roles.append('前端')
            if my_user_id in pm_names:
                is_mine = True
                roles.append('产品')
        
        tasks.append({
            'recordId': record['recordId'],
            'description': task_desc,
            'status': status,
            'priority': priority,
            'roles': roles,
            'is_mine': is_mine,
            'backend': backend_names,
            'frontend': frontend_names,
            'pm': pm_names
        })
    
    return tasks

def filter_tasks(tasks, args):
    """根据命令行参数筛选任务"""
    filtered = tasks
    
    # 按优先级筛选
    if args.p0:
        filtered = [t for t in filtered if t['priority'] == 'P0']
    elif args.p1:
        filtered = [t for t in filtered if t['priority'] == 'P1']
    elif args.p2:
        filtered = [t for t in filtered if t['priority'] == 'P2']
    
    # 按状态筛选
    if args.todo:
        filtered = [t for t in filtered if t['status'] in ['未开始', '开发中']]
    elif args.testing:
        filtered = [t for t in filtered if t['status'] == '待测试']
    
    # 按负责人筛选
    if not args.all:
        filtered = [t for t in filtered if t['is_mine']]
    
    return filtered

def print_tasks(tasks):
    """打印任务列表"""
    if not tasks:
        print("没有找到匹配的任务")
        return
    
    # 按优先级排序
    priority_order = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3, '无': 4}
    tasks.sort(key=lambda x: (priority_order.get(x['priority'], 5), x['status']))
    
    # 统计
    total = len(tasks)
    mine_count = len([t for t in tasks if t['is_mine']])
    
    print(f"\n{'='*80}")
    print(f"📋 AI 需求任务列表 ({total} 条)")
    if not args.all:
        print(f"👤 其中分配给你的: {mine_count} 条")
    print(f"{'='*80}\n")
    
    # 按优先级分组显示
    current_priority = None
    for task in tasks:
        if task['priority'] != current_priority:
            current_priority = task['priority']
            priority_emoji = {'P0': '🔥', 'P1': '📌', 'P2': '📝', 'P3': '💡', '无': '⚪'}
            print(f"\n{priority_emoji.get(current_priority, '⚪')} {current_priority} 优先级")
            print("-" * 80)
        
        # 截断描述
        desc = task['description'][:55] + '...' if len(task['description']) > 55 else task['description']
        
        # 角色标记
        role_str = '/'.join(task['roles']) if task['roles'] else '-'
        mine_mark = '👤' if task['is_mine'] else '  '
        
        # 状态颜色标记
        status_mark = {
            '未开始': '⬜',
            '开发中': '🔄',
            '待测试': '✅',
            '已完成': '✔️'
        }.get(task['status'], '❓')
        
        print(f"{mine_mark} [{status_mark} {task['status']:<6}] [{role_str:<8}] {desc}")
    
    print(f"\n{'='*80}")
    print(f"总计: {total} 条任务")
    print(f"{'='*80}\n")

def main():
    global args
    parser = argparse.ArgumentParser(description='查询 AI 需求任务')
    parser.add_argument('--p0', action='store_true', help='只显示 P0 优先级')
    parser.add_argument('--p1', action='store_true', help='只显示 P1 优先级')
    parser.add_argument('--p2', action='store_true', help='只显示 P2 优先级')
    parser.add_argument('--todo', action='store_true', help='只显示未开始/开发中的任务')
    parser.add_argument('--testing', action='store_true', help='只显示待测试的任务')
    parser.add_argument('--mine', action='store_true', help='只显示分配给你的任务（默认）')
    parser.add_argument('--all', action='store_true', help='显示所有 AI 任务')
    
    args = parser.parse_args()
    
    print("🔄 正在查询 AI 需求任务...")
    
    try:
        data = fetch_records()
        tasks = parse_tasks(data, MY_USER_ID if not args.all else None)
        filtered = filter_tasks(tasks, args)
        print_tasks(filtered)
    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
