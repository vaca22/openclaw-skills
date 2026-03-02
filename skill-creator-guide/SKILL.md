---
name: skill-creator-guide
description: >-
  OpenClaw Skill 创建指南。记录从零创建本地 Skill 的完整流程、目录结构、
  必需文件和常见问题解决方案。适用于创建自定义工具集成。
examples:
  - "如何创建一个新的 skill"
  - "skill 目录结构是什么样的"
  - "为什么我的 skill 不显示在列表中"
  - "创建 skill 需要哪些文件"
---

# OpenClaw Skill 创建指南

本指南记录从零创建本地 Skill 的完整流程，避免踩坑。

## 📁 完整目录结构

```
~/.openclaw/workspace/skills/<skill-name>/
├── SKILL.md              # 必需：技能文档（含 YAML front matter）
├── _meta.json            # 必需：元数据文件
├── .clawhub/             # 推荐：ClawHub 标记目录
│   └── origin.json       # ClawHub 来源标记
├── scripts/              # 可选：脚本目录
│   ├── script1.sh
│   └── script2.py
└── assets/               # 可选：资源文件
```

## 📝 必需文件详解

### 1. SKILL.md（必需）

**必须包含 YAML front matter**（用 `---` 包裹的元数据）：

```markdown
---
name: stock-price
description: >-
  使用腾讯财经接口查询 A 股/港股/美股实时股价，无需 API Key。
  支持代码查询 (002352, hk00700, usAAPL) 和名称查询 (顺丰控股，腾讯，苹果)。
examples:
  - "查顺丰控股股价"
  - "查 002352"
  - "查腾讯股价"
  - "查 AAPL"
---

# 技能详细说明

这里是技能的完整文档...
```

**⚠️ 关键要点：**
- YAML front matter **必须**包含 `name` 和 `description`
- `name` 必须与目录名一致
- `description` 可以跨多行（使用 `>-`）
- `examples` 数组帮助用户理解用法

### 2. _meta.json（必需）

```json
{
  "ownerId": "local",
  "slug": "stock-price",
  "version": "1.0.0",
  "publishedAt": 1740934800000
}
```

**字段说明：**
- `ownerId`: 所有者 ID（本地技能用 `"local"`）
- `slug`: 技能标识（与目录名一致）
- `version`: 语义化版本号
- `publishedAt`: Unix 时间戳（毫秒）

**⚠️ 注意：** 不要添加多余字段（如 `displayName`、`description`），可能导致识别失败。

### 3. .clawhub/origin.json（推荐）

```json
{
  "version": 1,
  "registry": "local",
  "slug": "stock-price",
  "installedVersion": "1.0.0",
  "installedAt": 1740934800000
}
```

**作用：** 标记技能来源，避免被 `clawhub` 误判为未安装。

## 🚀 创建流程

### 步骤 1：创建目录

```bash
mkdir -p ~/.openclaw/workspace/skills/<skill-name>
```

### 步骤 2：编写 SKILL.md

```bash
cat > ~/.openclaw/workspace/skills/<skill-name>/SKILL.md << 'EOF'
---
name: <skill-name>
description: >-
  技能描述，简洁说明功能。
examples:
  - "示例用法 1"
  - "示例用法 2"
---

# 详细说明

## 用法
...
EOF
```

### 步骤 3：创建 _meta.json

```bash
cat > ~/.openclaw/workspace/skills/<skill-name>/_meta.json << 'EOF'
{
  "ownerId": "local",
  "slug": "<skill-name>",
  "version": "1.0.0",
  "publishedAt": 1740934800000
}
EOF
```

### 步骤 4：创建 .clawhub 目录（推荐）

```bash
mkdir -p ~/.openclaw/workspace/skills/<skill-name>/.clawhub
cat > ~/.openclaw/workspace/skills/<skill-name>/.clawhub/origin.json << 'EOF'
{
  "version": 1,
  "registry": "local",
  "slug": "<skill-name>",
  "installedVersion": "1.0.0",
  "installedAt": 1740934800000
}
EOF
```

### 步骤 5：验证技能

```bash
# 检查技能是否被识别
openclaw skills list | grep <skill-name>

# 查看技能详情
openclaw skills info <skill-name>
```

### 步骤 6：刷新（如未显示）

```bash
# 重启 Gateway
openclaw gateway restart

# 或重新加载配置
openclaw gateway stop
openclaw gateway start
```

## ✅ 验证清单

创建完成后，确认以下几点：

- [ ] `SKILL.md` 存在且包含 YAML front matter
- [ ] `name` 字段与目录名一致
- [ ] `_meta.json` 存在且格式正确
- [ ] `_meta.json` 没有多余字段
- [ ] `.clawhub/origin.json` 存在（推荐）
- [ ] `openclaw skills list` 能看到技能
- [ ] 技能状态为 `✓ ready`

## ❌ 常见问题

### 问题 1：技能不显示在列表中

**可能原因：**
1. 缺少 `_meta.json`
2. `_meta.json` 格式错误或有额外字段
3. 缺少 YAML front matter
4. Gateway 缓存未刷新

**解决方案：**
```bash
# 1. 检查文件结构
ls -la ~/.openclaw/workspace/skills/<skill-name>/

# 2. 验证 _meta.json
cat ~/.openclaw/workspace/skills/<skill-name>/_meta.json

# 3. 重启 Gateway
openclaw gateway restart

# 4. 重新列出
openclaw skills list
```

### 问题 2：clawhub 找不到技能

**原因：** ClawHub 有独立的 lockfile 跟踪已安装技能。

**解决方案：**
```bash
# 强制重新安装
cd ~/.openclaw/workspace/skills
npx clawhub install <skill-name> --force
```

### 问题 3：技能状态显示 ✗ missing

**原因：** 依赖的 CLI 工具未安装或环境变量缺失。

**解决方案：**
- 检查 `requirements` 字段
- 安装所需工具
- 设置环境变量

## 📋 最佳实践

### 1. 命名规范
- 使用小写字母和连字符：`stock-price` ✅
- 避免大写字母和下划线：`StockPrice` ❌

### 2. 文件组织
- 脚本放在 `scripts/` 目录
- 资源文件放在 `assets/` 目录
- 主入口脚本命名为 `main.py` 或 `<skill-name>.py`

### 3. 文档质量
- `description` 简洁明了（1-2 句话）
- `examples` 覆盖常见用法
- 详细说明包含用法、限制、技术实现

### 4. 版本管理
- 使用语义化版本：`1.0.0`
- 更新时递增版本号
- 重大变更时更新 `publishedAt`

## 🔧 配置优化

在 `~/.openclaw/openclaw.json` 中添加：

```json
{
  "skills": {
    "load": {
      "extraDirs": ["~/.openclaw/workspace/skills"],
      "watch": true
    }
  }
}
```

**作用：**
- `extraDirs`: 显式指定技能目录
- `watch`: 启用热重载（修改后自动刷新）

## 📚 参考示例

### 示例 1：简单查询技能（stock-price）
- 单文件脚本
- 无需外部依赖
- 使用免费 API

### 示例 2：CLI 集成技能（weather）
- 依赖外部 CLI 工具
- 需要环境变量
- 多命令支持

### 示例 3：API 集成技能（qveris-official）
- 需要 API Key
- 复杂配置
- 多脚本协作

## 🎯 快速模板

复制以下模板快速开始：

```bash
# 创建目录
SKILL_NAME="my-skill"
mkdir -p ~/.openclaw/workspace/skills/$SKILL_NAME/.clawhub

# 创建 SKILL.md
cat > ~/.openclaw/workspace/skills/$SKILL_NAME/SKILL.md << EOF
---
name: $SKILL_NAME
description: >-
  技能描述。
examples:
  - "示例用法"
---

# $SKILL_NAME

## 用法
...
EOF

# 创建 _meta.json
cat > ~/.openclaw/workspace/skills/$SKILL_NAME/_meta.json << EOF
{
  "ownerId": "local",
  "slug": "$SKILL_NAME",
  "version": "1.0.0",
  "publishedAt": $(node -e "console.log(Date.now())")
}
EOF

# 创建 origin.json
cat > ~/.openclaw/workspace/skills/$SKILL_NAME/.clawhub/origin.json << EOF
{
  "version": 1,
  "registry": "local",
  "slug": "$SKILL_NAME",
  "installedVersion": "1.0.0",
  "installedAt": $(node -e "console.log(Date.now())")
}
EOF

# 验证
openclaw skills list | grep $SKILL_NAME
```

---

**最后更新**: 2026-03-02  
**版本**: 1.0.0  
**作者**: OpenClaw Agent
