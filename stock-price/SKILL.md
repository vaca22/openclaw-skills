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
  - "查贵州茅台"
---

# stock-price - 股价查询技能

无需 API Key，使用 **腾讯财经接口** (`qt.gtimg.cn`) 获取实时股价数据。

## 用法

### 方式 1：直接对话
```
查顺丰控股股价
查 002352
查腾讯股价
查 AAPL
```

### 方式 2：CLI 脚本
```bash
python3 ~/.openclaw/workspace/skills/stock-price/stock.py 顺丰控股
python3 ~/.openclaw/workspace/skills/stock-price/stock.py 002352
python3 ~/.openclaw/workspace/skills/stock-price/stock.py hk00700
python3 ~/.openclaw/workspace/skills/stock-price/stock.py usAAPL
```

## 支持市场

| 市场 | 代码格式 | 示例 |
|------|----------|------|
| A 股 | 6 位数字 | 002352, 600519 |
| 港股 | hk+ 代码 | hk00700, hk09988 |
| 美股 | us+ 代码 | usAAPL, usTSLA |
| 名称 | 中文/英文 | 顺丰控股，腾讯，苹果 |

## 输出格式

```markdown
## 📊 [股票名称] ([代码])

| 项目 | 数值 |
|------|------|
| 当前价 | XX.XX 元 |
| 涨跌 | +X.XX (+X.XX%) |
| 今开 | XX.XX 元 |
| 最高 | XX.XX 元 |
| 最低 | XX.XX 元 |
| 总市值 | XXXX 亿 |
| 数据时间 | YYYY-MM-DD HH:MM |
```

## 技术实现

1. 使用腾讯财经接口 `https://qt.gtimg.cn/q={code}`
2. 解析返回的实时行情数据
3. 格式化输出为 Markdown 表格

## 限制

- ✅ **A 股**: 数据完整，时间戳准确
- ⚠️ **港股/美股**: 核心数据准确，时间戳格式可能显示异常
- 盘中实时数据：交易时间内更新，非交易时间显示最近收盘价

## 在 OpenClaw 中使用

**对话直接查**：
```
查顺丰控股股价
查腾讯
查 AAPL
```

**终端执行**：
```bash
python3 ~/.openclaw/workspace/skills/stock-price/stock.py 顺丰控股
```

---

**作者**: OpenClaw Agent  
**创建**: 2026-03-02  
**版本**: 1.0.0
