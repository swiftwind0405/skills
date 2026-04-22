---
name: project-dev-guide
description: 本机项目开发指引。当用户提到项目名称（如 admin、h5、ats）或要求进行编码开发、调试、部署时自动激活。提供项目路径映射、工程规范、交付检查清单和代码质量标准。
version: 1.0.0
author: Stanley
license: MIT
metadata:
  hermes:
    tags: [development, workflow, coding, project, delivery]
    related_skills: [jenkins-job-trigger, software-development/plan, software-development/subagent-driven-development]
---

# 项目开发指引

当用户要求进行编码开发任务时，遵循本指引。

---

## 1. 项目路径映射

先确认目标项目，按别名解析到绝对路径。**所有文件操作和终端命令必须基于正确的绝对路径。**

### 本机私有覆盖（优先）

如果 `references/path-aliases.local.json` 存在，**必须先读取它，并以其中的路径映射作为本机真实 source of truth**。

- 该文件用于保存当前机器/私有环境的真实项目路径
- 它应被 `.gitignore` 忽略，不进入公开仓库
- 公开 `SKILL.md` 里的路径表示例仅作为结构说明 / fallback，不代表当前机器一定存在这些目录

建议的读取顺序：
1. `~/.hermes/skills/project-dev-guide/references/path-aliases.local.json`
2. 若仓库里存在 `references/path-aliases.example.json`，可将其复制为 `.local.json` 后按本机情况填写
3. 若本地覆盖不存在，再退回到下面这张公开示例表

| 别名 | 公开示例路径 | 技术栈 |
|------|---------|--------|
| `admin` / `pc` / `后台管理` | `~/Workspace/projects/web-suite/apps/admin` | React 前端 |
| `h5` / `前端h5` | `~/Workspace/projects/web-suite/apps/h5` | React H5 |
| `onboarding-h5` / `onboarding` | `~/Workspace/projects/web-suite/apps/onboarding-h5` | React H5 |
| `ats` / `后端ats` / `backend` | `~/Workspace/projects/backend/ats` | 后端服务 |

### 消歧规则

- 若 `references/path-aliases.local.json` 中存在默认映射，优先使用本机私有配置
- 用户说「ats」且未指定前后端 → 默认 **后端** `~/Workspace/projects/backend/ats`
- 用户说「前端 ats」→ 需要确认具体指 admin 还是 h5
- 相同名称出现在多个位置时，主动确认

### monorepo 注意

`web-suite` 是 monorepo，共享 `packages/` 目录。修改共享包时注意影响范围：

```
web-suite/
├── apps/
│   ├── admin/      ← 后台管理 PC 端
│   ├── h5/         ← 移动端 H5
│   └── onboarding-h5/
├── packages/       ← 共享包，修改需评估对所有 apps 的影响
└── ...
```

---

## 2. 开发工作流

### 2.1 接到任务时

1. **确认项目** — 解析别名，`cd` 到正确路径
2. **了解现状** — `git status`、`git branch`、`git log -5 --oneline`
3. **理解需求** — 如果需求模糊，先问清楚再动手

### 2.2 编码策略

**先跑通，再完善：**

1. 先实现 happy path，确保核心逻辑可运行
2. 补充边界条件处理和错误处理
3. 最后补测试（如有测试框架）

**代码质量标准：**

- 使用 ES modules，正确排序 import
- 优先使用 `function` 声明而非箭头函数（顶层）
- 顶层函数需要显式返回类型注解（TypeScript）
- React 组件使用显式 Props 类型定义
- 避免嵌套三元运算符，用 `switch` 或 `if/else`
- 清晰优先于简洁 — 不要为了少写几行牺牲可读性
- 变量/函数名应自解释，避免无意义命名

### 2.3 代码自检（提交前）

写完代码后，逐条过：

1. 功能是否完整实现？跑过 happy path 了吗？
2. 边界条件处理了吗？（空值、异常输入、并发）
3. 有没有引入不必要的复杂度？能否简化？
4. 命名是否清晰？他人能否一眼理解？
5. 是否遵循项目已有的编码风格和模式？
6. 修改共享包时，是否评估了对其他 app 的影响？

---

## 3. 交付检查清单

**每次交付必须包含以下内容，缺一不可：**

### 必须交付项

- [ ] **运行命令** — 如何启动 / 如何验证功能正常
- [ ] **测试命令** — 如何跑测试（如适用）
- [ ] **验收点** — 明确列出功能验收标准，便于用户验证

### 视情况交付项

- [ ] **回滚方案** — 如果出问题怎么回退（涉及数据变更或部署时必须）
- [ ] **迁移说明** — 数据库变更、配置变更等（如适用）
- [ ] **影响范围** — 修改了共享包/公共模块时，说明影响了哪些应用

### 交付格式示例

```
## 运行验证
pnpm dev              # 启动开发服务器
访问 http://localhost:3000/xxx 查看新功能

## 测试
pnpm test -- --filter=xxx

## 验收点
1. 点击 xxx 按钮，应显示 xxx 弹窗
2. 输入 xxx 后提交，列表应新增一条记录
3. 刷新页面，数据应持久化

## 回滚
git revert HEAD       # 如需回退
```

---

## 4. Git 规范

### 提交信息格式

```
<type>: <简要描述>

type 可选值：
- feat:     新功能
- fix:      修复 bug
- refactor: 重构（不改变功能）
- style:    格式调整
- docs:     文档
- test:     测试
- chore:    构建/工具链
```

### 分支操作

- 开始开发前确认当前分支
- 不要直接在 main/master 上开发
- 提交前 `git diff` 复查变更

---

## 5. 安全约束

- `trash` > `rm` — 可恢复优先于永久删除
- 不在代码或日志中暴露密钥、token、密码
- 破坏性操作（删文件、改数据库、强推）必须先确认
- 不确定的事情，问用户

---

## 6. 常见场景速查

| 场景 | 做法 |
|------|------|
| 用户说「改一下 admin 的 xxx」 | → 进入 `~/Workspace/projects/web-suite/apps/admin`，找到相关文件修改 |
| 用户说「ats 加个接口」 | → 进入 `~/Workspace/projects/backend/ats`，按后端规范添加 |
| 用户说「这个组件在哪」 | → 先在对应项目里 grep 搜索，再定位 |
| 用户说「跑一下」 | → 根据项目类型执行对应的 dev server 启动命令 |
| 用户说「部署」 | → 使用 `jenkins-job-trigger` skill 触发对应 Jenkins job |
| 涉及共享包修改 | → 先评估影响范围，告知用户可能影响哪些 app |
