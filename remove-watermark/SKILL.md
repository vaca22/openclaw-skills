---
name: remove-watermark
description: >-
  去除图片水印的 skill。支持多种算法：inpainting、模糊覆盖、裁剪等。
  使用 OpenCV 和 ffmpeg 处理，无需 API Key。
examples:
  - "去除这张图片的水印"
  - "帮我把 watermark.png 处理一下"
  - "批量去除 screenshots 目录所有图片的水印"
---

# remove-watermark - 图片去水印技能

使用 OpenCV 和图像处理算法去除图片水印，支持多种模式。

## 用法

### 方式 1：直接对话
```
去除这张图片的水印
帮我把 photo.png 的水印去掉
批量去除 screenshots 目录的水印
```

### 方式 2：CLI 脚本
```bash
# 单张图片 - 自动检测水印
python3 ~/.openclaw/workspace/skills/remove-watermark/remove.py image.png

# 指定水印位置 (右下角)
python3 ~/.openclaw/workspace/skills/remove-watermark/remove.py image.png --position bottom-right

# 指定水印区域 (x,y,width,height)
python3 ~/.openclaw/workspace/skills/remove-watermark/remove.py image.png --roi 100,200,150,50

# 批量处理
python3 ~/.openclaw/workspace/skills/remove-watermark/remove.py ./screenshots/*.png

# 使用 inpainting 算法 (更自然)
python3 ~/.openclaw/workspace/skills/remove-watermark/remove.py image.png --method inpaint
```

## 支持的方法

| 方法 | 描述 | 适用场景 |
|------|------|----------|
| `inpaint` | 图像修复算法，用周围像素填充 | 水印在复杂背景上 |
| `blur` | 高斯模糊覆盖 | 水印在纯色背景上 |
| `crop` | 直接裁剪掉水印区域 | 水印在边缘 |
| `clone` | 克隆印章工具 | 需要手动指定源区域 |

## 输出格式

处理后的图片保存在原文件同目录，命名为 `{original}_no_watermark.{ext}`

## 技术实现

1. 使用 OpenCV 检测或手动指定水印区域
2. 根据选择的方法处理水印区域
3. 保存处理后的图片

## 依赖

```bash
pip3 install opencv-python numpy
```

## 限制

- ✅ 简单水印效果好
- ⚠️ 复杂背景可能需要手动调整参数
- ❌ 无法完全去除覆盖重要内容的水印

---

**作者**: OpenClaw Agent  
**创建**: 2026-03-02  
**版本**: 1.0.0
