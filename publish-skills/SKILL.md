---
name: publish-skills
description: >-
  将本地 skills 打包并发布到 GitHub 仓库或 ClawHub。
  支持单个 skill 或整个 skills 目录的发布。
examples:
  - "发布 stock-price skill"
  - "把所有 skills 推到 GitHub"
  - "发布 skill 到 clawhub"
---

# publish-skills - Skill 发布工具

将 OpenClaw 的 skills 打包并发布到 GitHub 仓库或 ClawHub 平台。

## 用法

### 方式 1：直接对话
```
发布 stock-price skill
把所有 skills 推到 GitHub
发布 skill 到 clawhub
```

### 方式 2：CLI 脚本
```bash
# 发布单个 skill
python3 ~/.openclaw/workspace/skills/publish-skills/publish.py stock-price

# 发布所有 skills
python3 ~/.openclaw/workspace/skills/publish-skills/publish.py --all

# 发布到 ClawHub
python3 ~/.openclaw/workspace/skills/publish-skills/publish.py --clawhub stock-price
```

## 功能

| 功能 | 描述 |
|------|------|
| GitHub 发布 | 创建/更新 GitHub 仓库，推送 skill 文件 |
| ClawHub 发布 | 打包 skill 并提交到 ClawHub 平台 |
| 批量发布 | 一次性发布整个 skills 目录 |
| 版本管理 | 自动处理版本号和 changelog |

## 配置

在 `~/.openclaw/openclaw.json` 中添加：

```json
{
  "skills": {
    "entries": {
      "publish-skills": {
        "githubOwner": "your-github-username",
        "githubToken": "gho_xxx",
        "clawhubApiKey": "xxx"
      }
    }
  }
}
```

## 输出

发布成功后返回：
- GitHub 仓库 URL
- ClawHub 技能页面链接
- 版本号

---

**作者**: OpenClaw Agent  
**创建**: 2026-03-02  
**版本**: 1.0.0
