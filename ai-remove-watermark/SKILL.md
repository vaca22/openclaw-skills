---
name: ai-remove-watermark
description: >-
  使用深度学习 AI 模型去除图片水印。支持 LaMa、MAT、SD-Inpainting 等先进模型。
  比传统方法更自然，适合复杂背景。需要 GPU 或 ONNX runtime。
examples:
  - "用 AI 去除这张图片的水印"
  - "用 LaMa 模型处理 photo.png"
  - "批量 AI 去水印 screenshots 目录"
---

# ai-remove-watermark - AI 深度学习去水印技能

使用先进的深度学习模型进行图像修复 (inpainting)，效果远超传统方法。

## 支持的模型

| 模型 | 描述 | 速度 | 质量 | 需要 GPU |
|------|------|------|------|----------|
| `lama` | Facebook LaMa (Large Mask Inpainting) | 快 | ⭐⭐⭐⭐ | 否 (ONNX) |
| `mat` | Mask-Aware Transformer | 中 | ⭐⭐⭐⭐⭐ | 推荐 |
| `sd-inpaint` | Stable Diffusion Inpainting | 慢 | ⭐⭐⭐⭐⭐ | 是 |
| `openglama` | OpenLaMa (优化版) | 快 | ⭐⭐⭐⭐ | 否 |

## 用法

### 方式 1：直接对话
```
用 AI 去除这张图片的水印
用 LaMa 模型处理 photo.png
批量 AI 去水印 screenshots 目录
```

### 方式 2：CLI 脚本
```bash
# 使用 LaMa 模型 (推荐，快速且效果好)
python3 ~/.openclaw/workspace/skills/ai-remove-watermark/remove.py image.png

# 指定模型
python3 ~/.openclaw/workspace/skills/ai-remove-watermark/remove.py image.png --model lama

# 使用 Stable Diffusion (需要 GPU)
python3 ~/.openclaw/workspace/skills/ai-remove-watermark/remove.py image.png --model sd-inpaint

# 自动检测水印区域
python3 ~/.openclaw/workspace/skills/ai-remove-watermark/remove.py image.png --auto-mask

# 手动指定掩码图片 (黑白图，白色为水印区域)
python3 ~/.openclaw/workspace/skills/ai-remove-watermark/remove.py image.png --mask watermark_mask.png

# 批量处理
python3 ~/.openclaw/workspace/skills/ai-remove-watermark/remove.py ./photos/*.png --model lama
```

## 安装依赖

### 基础安装 (LaMa - ONNX 推理)
```bash
pip3 install onnxruntime opencv-python numpy --break-system-packages
```

### 完整安装 (支持所有模型)
```bash
pip3 install torch torchvision diffusers transformers accelerate --break-system-packages
```

### 或使用 requirements.txt
```bash
pip3 install -r ~/.openclaw/workspace/skills/ai-remove-watermark/requirements.txt
```

## 模型下载

首次运行会自动下载模型到 `~/.cache/ai-watermark/`

- LaMa: ~100MB
- MAT: ~500MB  
- SD-Inpaint: ~4GB

## 输出格式

处理后的图片保存为 `{original}_ai_no_watermark.{ext}`

## 技术实现

1. **LaMa**: 使用大掩码图像修复，在 Places2 和 COCO 上训练
2. **MAT**: Transformer 架构，处理复杂结构更好
3. **SD-Inpaint**: 基于 Stable Diffusion 的文本引导修复

## 对比传统方法

| 场景 | 传统方法 | AI 方法 |
|------|----------|---------|
| 纯色背景 | ✅ 好 | ✅ 好 |
| 复杂纹理 | ⚠️ 模糊 | ✅ 自然 |
| 文字水印 | ❌ 残留 | ✅ 完整去除 |
| 大区域水印 | ❌ 失真 | ✅ 合理填充 |

## 限制

- ⚠️ 首次运行需要下载模型
- ⚠️ SD 模型需要 GPU (4GB+ VRAM)
- ✅ LaMa 模型 CPU 可运行

---

**作者**: OpenClaw Agent  
**创建**: 2026-03-02  
**版本**: 1.0.0
