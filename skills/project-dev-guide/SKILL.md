---
name: project-dev-guide
description: 本地项目编码开发指引。当用户提到项目名称、仓库名称、目录位置，或要求进行写代码、改代码、调试时激活。核心目标是先把项目别名解析到本机真实仓库绝对路径，再继续后续开发动作。
---

# Project Dev Guide

当用户要求在本机项目里写代码、排查问题、调试时，优先执行“仓库定位”，不要直接假设目录。

## 核心原则

- 先定位仓库，再读代码，再改代码
- 所有命令和文件操作都基于绝对路径
- `path-aliases.local.json` 是当前机器的真实 source of truth
- 公开 `SKILL.md` 和 `path-aliases.example.json` 只描述规则与格式，不代表任何机器的真实路径
- 如果项目名可能对应多个仓库，先消歧，不要猜
- 如果本机映射不存在，就用本机搜索兜底，再向用户说明最终使用的路径

## 必做动作

收到开发类请求后，默认按这个顺序执行：

1. 提取用户提到的项目别名、仓库名、子系统名
2. 解析到本机绝对路径
3. 明确回报：本次操作对应的仓库路径是什么
4. 进入该目录后再执行 `git status`、搜索代码、修改文件、调试

如果第 2 步还没完成，不要开始写代码。

## 路径解析顺序

### 1. 优先读取本机私有映射

优先读取 skill 目录下的：

`references/path-aliases.local.json`

如果这个文件存在，必须优先使用其中的映射。

用途：

- 保存当前机器真实仓库路径
- 支持一个项目多个别名
- 支持默认目录、monorepo 根目录和具体子项目目录

### 2. 本机映射不存在时，参考公开示例结构

可参考：

`references/path-aliases.example.json`

注意：

- 这是结构示例，不保证当前机器目录真实存在
- 不能把示例路径当成事实
- 示例的作用是帮助理解字段结构，而不是提供默认路径

### 3. 无法命中映射时，执行本机搜索

优先用仓库名、目录名、业务名搜索真实路径。常用方式：

```bash
find <search-root> -maxdepth 4 -type d -name "<repo-or-app-name>"
find <search-root> -maxdepth 5 -type d \( -name "<alias-1>" -o -name "<alias-2>" \)
rg -n "\"<alias>\"" references/path-aliases.local.json
```

说明：

- `<search-root>` 应按当前机器的常见代码目录替换，比如 `~/Workspace`、`~/code`、`~/projects`
- 如果用户已提供父目录，优先在该目录下搜索

如果找到了多个候选路径：

- 优先选和用户语义最接近的目录
- 如果仍有歧义，先向用户确认

如果一个都找不到：

- 明确告诉用户当前机器未找到对应仓库
- 列出你搜索过的关键词或目录范围
- 不要编造路径

## 路径映射格式

推荐 `path-aliases.local.json` 结构：

```json
{
  "backend_root": "/absolute/path/to/backend",
  "frontend_monorepo_name": "web-monorepo",
  "frontend_monorepo_root": "/absolute/path/to/frontend",
  "ai_root": "/absolute/path/to/ai",
  "defaults": {
    "backend": "/absolute/path/to/backend",
    "frontend": "/absolute/path/to/frontend",
    "ai": "/absolute/path/to/ai",
    "ats": "/absolute/path/to/backend/ats"
  },
  "entries": [
    {
      "aliases": ["admin", "pc", "后台管理"],
      "path": "/absolute/path/to/frontend/apps/admin",
      "stack": "React 前端"
    }
  ]
}
```

解析规则：

- 先查 `entries[].aliases`
- 再查 `defaults`
- 命中后统一转换成绝对路径再使用
- 如果目录不存在，视为失效映射，继续搜索，不要硬用

## 建议的映射方式

- 用 `defaults` 放常见根目录或高频项目
- 用 `entries` 放具体仓库、monorepo app、共享包目录
- 同一个项目可以配置多个别名，但别名不要过度重叠
- 容易冲突的词应显式区分，例如把前后端同名项目拆成不同别名
- 如果是 monorepo，既要有根目录别名，也要有常用 app 或 packages 别名

## 消歧规则

- 用户只说业务名，但该业务对应多个仓库时，先确认，不要硬猜
- 用户只说 `frontend`、`backend`、`ai` 这类大类名时，默认进入该类根目录，不直接猜具体子项目
- 用户说某个 app 名或服务名时，优先映射到对应子目录
- 相同别名对应多个目录时，先说明候选路径再确认

## Monorepo 处理

如果命中 monorepo 内子项目：

- 默认进入子项目目录开展工作
- 只有在明确涉及共享代码时，才进入 monorepo 根目录或共享包目录
- 修改共享包前，必须评估对其他 app 的影响

## 仓库定位后的标准动作

进入正确目录后再继续：

1. `git status`
2. `git branch --show-current`
3. `git log -5 --oneline`
4. 搜索相关代码
5. 修改、验证、总结

如果用户只是问“仓库在哪”“这个项目目录是什么”，做到第 2 步即可，不要额外跑开发命令。

## 开发约束

- 先实现核心路径，再补边界处理
- 代码风格优先遵循仓库现状，不要把 skill 里的偏好压过项目现有规范
- 涉及共享模块、配置、数据变更时，要说明影响范围
- 破坏性操作前先确认

## 对用户的回报格式

每次命中仓库后，优先给出这一句：

`已定位到仓库：<absolute-path>`

如果是 monorepo 子项目，建议补一句：

`本次操作目录：<absolute-path>`

如果需要说明原因，可再补：

- 用户提到的别名是什么
- 该别名如何映射到当前目录
- 是否使用了本机私有映射或搜索兜底

## 常见场景

| 用户表达                | 处理方式                                        |
| ----------------------- | ----------------------------------------------- |
| “改一下 admin 的登录页” | 先定位 `admin` 对应仓库绝对路径，再搜索相关代码 |
| “ats 加个接口”          | 先根据本机映射判断 `ats` 指向哪个后端项目       |
| “前端 ats 在哪改”       | 先判断本机映射里是否有独立的前端 `ats` 别名     |
| “这个项目仓库在哪”      | 只做路径解析并回报绝对路径                      |
| “改一下前端公共组件”    | 先定位 monorepo 的共享包目录或组件包目录        |

## 失败处理

出现以下情况时，不要继续盲改：

- 别名未命中
- 映射文件存在但路径无效
- 搜索结果有多个高相似候选
- 用户说的是业务名，不是仓库名，且当前无法唯一映射

此时应明确说明：

- 你未能唯一定位仓库
- 你已经检查了哪些映射或目录
- 还需要用户补充什么信息
