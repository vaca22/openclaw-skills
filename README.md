# OpenClaw Skills Collection

精选的 OpenClaw 技能集合。

## 包含的技能

### 📊 stock-price
使用腾讯财经接口查询 A 股/港股/美股实时股价，无需 API Key。
- 支持代码查询 (002352, hk00700, usAAPL)
- 支持名称查询 (顺丰控股，腾讯，苹果)

### 🛠️ skill-creator-guide
创建和发布 OpenClaw 技能的指南和工具。

## 使用方法

### 方式 1：直接复制到你的 skills 目录
```bash
cp -r stock-price ~/.openclaw/workspace/skills/
cp -r skill-creator-guide ~/.openclaw/workspace/skills/
```

### 方式 2：作为子模块引入
```bash
git submodule add https://github.com/vaca22/openclaw-skills.git skills
```

## 许可证

MIT

---
**作者**: vaca22  
**创建**: 2026-03-02
