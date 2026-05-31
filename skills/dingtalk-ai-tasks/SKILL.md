---
title: 钉钉 AI 任务查询
name: dingtalk-ai-tasks
description: 查询钉钉 AI 表格中分配给你的 AI 需求任务，支持按优先级、状态筛选
version: 1.0.0
author: hermes
requirements:
  - dws CLI 已安装并配置
  - Python 3.7+
---

# 钉钉 AI 任务查询

查询钉钉 AI 表格（"才到：产品整体任务清单"）中"AI 需求"视图的任务，支持按优先级、状态、负责人筛选。

## 使用方法

### 直接运行脚本

```bash
# 显示所有分配给你的 AI 任务
python3 ~/.hermes/skills/dingtalk-ai-tasks/scripts/ai-tasks.py

# 只显示 P0 优先级任务
python3 ~/.hermes/skills/dingtalk-ai-tasks/scripts/ai-tasks.py --p0

# 只显示 P1 优先级任务
python3 ~/.hermes/skills/dingtalk-ai-tasks/scripts/ai-tasks.py --p1

# 只显示 P2 优先级任务
python3 ~/.hermes/skills/dingtalk-ai-tasks/scripts/ai-tasks.py --p2

# 只显示未开始/开发中的任务
python3 ~/.hermes/skills/dingtalk-ai-tasks/scripts/ai-tasks.py --todo

# 只显示待测试的任务
python3 ~/.hermes/skills/dingtalk-ai-tasks/scripts/ai-tasks.py --testing

# 显示所有 AI 任务（不只是你的）
python3 ~/.hermes/skills/dingtalk-ai-tasks/scripts/ai-tasks.py --all
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `--p0` | 只显示 P0 优先级任务 |
| `--p1` | 只显示 P1 优先级任务 |
| `--p2` | 只显示 P2 优先级任务 |
| `--todo` | 只显示未开始/开发中的任务 |
| `--testing` | 只显示待测试的任务 |
| `--all` | 显示所有 AI 任务（默认只显示分配给你的）|

## 输出说明

- `👤` - 标记分配给你的任务
- `🔥 P0` / `📌 P1` / `📝 P2` - 优先级
- `⬜ 未开始` / `🔄 开发中` / `✅ 待测试` / `✔️ 已完成` - 任务状态
- `[后端/前端/产品]` - 你的角色

## 配置

如需修改查询的表格或用户 ID，编辑脚本中的配置部分：

```python
BASE_ID = "bva6QBXJwaj5lgqzHo1QEn7oWn4qY5Pr"  # 表格 Base ID
TABLE_ID = "hERWDMS"                           # 产品大盘表 ID
MY_USER_ID = "0568460913-1915884507"           # 你的钉钉用户 ID
```

## 依赖

- `dws` CLI 工具（钉钉 AI 表格命令行工具）
- Python 3.7+

## 安装 dws CLI

```bash
# 下载最新版本
curl -L https://github.com/chrishubert/dws/releases/latest/download/dws-$(uname -s)-$(uname -m) -o ~/bin/dws
chmod +x ~/bin/dws

# 登录
dws auth login
```
