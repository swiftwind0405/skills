---
name: create-skill-with-symlink
description: 在项目中创建 Skill 并通过软链接连接到 Hermes skills 目录的标准流程
version: 1.0.0
author: hermes
---

# 创建 Skill 并软链接到 Hermes

在项目中创建 Skill，然后通过软链接连接到 `~/.hermes/skills/` 的标准流程。

## 目录结构规范

```
/Users/admin/Workspace/projects/skills/skills/     # 项目 Skill 目录（源文件）
└── <skill-name>/                                  # Skill 目录，直接放在 skills/ 下
    ├── SKILL.md                                   # Skill 文档
    └── scripts/                                   # 可选：脚本目录
        └── <script>.py

~/.hermes/skills/                                  # Hermes Skill 目录（软链接）
└── <skill-name> -> /Users/admin/Workspace/projects/skills/skills/<skill-name>  # 软链接
```

**注意：** Skill 直接放在 `skills/` 下，**不加分类目录**（如 productivity/、software-development/ 等）。

## 创建流程

### 1. 创建 Skill 目录和文件

```bash
# 创建目录结构
mkdir -p /Users/admin/Workspace/projects/skills/skills/<skill-name>/scripts

# 创建 SKILL.md
cat > /Users/admin/Workspace/projects/skills/skills/<skill-name>/SKILL.md << 'EOF'
---
name: <skill-name>
description: <Skill 描述>
version: 1.0.0
author: hermes
---

# <Skill 标题>

<Skill 文档内容>
EOF

# 创建脚本（可选）
cat > /Users/admin/Workspace/projects/skills/skills/<skill-name>/scripts/<script>.py << 'EOF'
#!/usr/bin/env python3
# 脚本内容
EOF

chmod +x /Users/admin/Workspace/projects/skills/skills/<skill-name>/scripts/<script>.py
```

### 2. 删除旧 Skill（如果存在）并创建软链接

```bash
# 删除 Hermes 中已存在的同名 Skill（如果是普通目录）
rm -rf ~/.hermes/skills/<skill-name>

# 创建软链接
ln -s /Users/admin/Workspace/projects/skills/skills/<skill-name> ~/.hermes/skills/<skill-name>

# 验证软链接
ls -la ~/.hermes/skills/ | grep <skill-name>
```

### 3. 验证 Skill 可用

```bash
# 测试 Skill 是否正常工作
skill_view <skill-name>

# 或运行脚本
python3 ~/.hermes/skills/<skill-name>/scripts/<script>.py
```

## 示例：创建 dingtalk-ai-tasks Skill

```bash
# 1. 创建目录和文件
mkdir -p /Users/admin/Workspace/projects/skills/skills/dingtalk-ai-tasks/scripts

# 2. 写入 SKILL.md
cat > /Users/admin/Workspace/projects/skills/skills/dingtalk-ai-tasks/SKILL.md << 'EOF'
---
name: dingtalk-ai-tasks
description: 查询钉钉 AI 表格中分配给你的 AI 需求任务
version: 1.0.0
author: hermes
---

# 钉钉 AI 任务查询
...
EOF

# 3. 写入脚本
cat > /Users/admin/Workspace/projects/skills/skills/dingtalk-ai-tasks/scripts/ai-tasks.py << 'EOF'
#!/usr/bin/env python3
# 脚本内容
EOF
chmod +x /Users/admin/Workspace/projects/skills/skills/dingtalk-ai-tasks/scripts/ai-tasks.py

# 4. 创建软链接
rm -rf ~/.hermes/skills/dingtalk-ai-tasks
ln -s /Users/admin/Workspace/projects/skills/skills/dingtalk-ai-tasks ~/.hermes/skills/dingtalk-ai-tasks

# 5. 验证
skill_view dingtalk-ai-tasks
```

## 更新 Skill

由于使用了软链接，直接在项目目录修改文件即可，Hermes 会自动使用最新版本：

```bash
# 编辑项目中的源文件
vim /Users/admin/Workspace/projects/skills/skills/<skill-name>/SKILL.md

# 修改立即生效，无需重新创建软链接
```

## 删除 Skill

```bash
# 删除软链接（不影响源文件）
rm ~/.hermes/skills/<skill-name>

# 如需彻底删除，同时删除源文件
rm -rf /Users/admin/Workspace/projects/skills/skills/<skill-name>
```

## 注意事项

1. **不要加分类目录**：Skill 直接放在 `skills/` 下，不要创建 `productivity/`、`software-development/` 等子目录
2. **先删除再链接**：如果 `~/.hermes/skills/<skill-name>` 已存在且是普通目录，必须先删除才能创建软链接
3. **使用绝对路径**：软链接建议使用绝对路径，避免相对路径解析问题
4. **验证**：创建后务必验证 Skill 可以正常加载
