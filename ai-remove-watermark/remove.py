#!/usr/bin/env python3
"""
ai-remove-watermark - AI-powered watermark removal using deep learning models
Supports: LaMa, MAT, SD-Inpainting
"""

import os
import sys
import argparse
import cv2
import numpy as np
from pathlib import Path
from urllib.request import urlretrieve
from hashlib import md5

# Model configurations
MODELS = {
    'lama': {
        'url': 'https://github.com/advimman/lama/raw/main/lama_large.onnx',
        'size': '~100MB',
        'description': 'Facebook LaMa - Large Mask Inpainting (fast, good quality)'
    },
    'mat': {
        'url': 'https://huggingface.co/flyingbird/mat/resolve/main/mat.pth',
        'size': '~500MB', 
        'description': 'Mask-Aware Transformer (best quality)'
    },
    'sd-inpaint': {
        'url': 'runwayml/stable-diffusion-inpainting',
        'size': '~4GB',
        'description': 'Stable Diffusion Inpainting (requires GPU)'
    }
}

CACHE_DIR = Path.home() / ".cache" / "ai-watermark"

def ensure_cache_dir():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

def download_model(model_name):
    """Download model if not cached"""
    ensure_cache_dir()
    
    if model_name == 'lama':
        model_path = CACHE_DIR / "lama_large.onnx"
        if not model_path.exists():
            print(f"📥 Downloading LaMa model (~100MB)...")
            # Use a reliable mirror
            url = "https://huggingface.co/duck-nlp/lama-large-onnx/resolve/main/lama_large.onnx"
            try:
                urlretrieve(url, model_path)
                print(f"✅ Model downloaded to {model_path}")
            except Exception as e:
                print(f"⚠️  Download failed: {e}")
                print("💡 Try manual download from https://huggingface.co/duck-nlp/lama-large-onnx")
                return None
        return model_path
    
    elif model_name == 'mat':
        print("⚠️  MAT model requires torch. Install with: pip3 install torch torchvision")
        return None
    
    elif model_name == 'sd-inpaint':
        print("⚠️  SD-Inpaint requires diffusers + GPU. Install with: pip3 install diffusers transformers accelerate torch")
        return None
    
    return None

def detect_watermark_region(image):
    """
    Detect likely watermark region using edge detection and corner analysis.
    Returns (x, y, w, h)
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    
    # Focus on corners (most common watermark positions)
    corner_regions = [
        (0, 0, w // 3, h // 3),  # top-left
        (w * 2 // 3, 0, w // 3, h // 3),  # top-right
        (0, h * 2 // 3, w // 3, h // 3),  # bottom-left
        (w * 2 // 3, h * 2 // 3, w // 3, h // 3),  # bottom-right
    ]
    
    best_score = 0
    best_region = None
    
    for x, y, cw, ch in corner_regions:
        roi = gray[y:y+ch, x:x+cw]
        
        # Watermark often has different texture/edge density
        edges = cv2.Canny(roi, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # Also check for text-like patterns (high frequency content)
        fft = np.fft.fft2(roi)
        fft_shift = np.fft.fftshift(fft)
        magnitude = np.abs(fft_shift)
        
        # High frequency ratio
        center_y, center_x = magnitude.shape[0] // 2, magnitude.shape[1] // 2
        high_freq = magnitude[center_y-10:center_y+10, center_x-10:center_x+10].mean()
        low_freq = magnitude.mean()
        freq_ratio = high_freq / (low_freq + 1e-6)
        
        score = edge_density * freq_ratio
        
        if score > best_score:
            best_score = score
            best_region = (x, y, cw, ch)
    
    # Default to bottom-right if detection fails
    if best_region is None or best_score < 0.01:
        best_region = (w * 2 // 3, h * 2 // 3, w // 3, h // 3)
    
    return best_region

def create_mask(image, roi=None, auto=False):
    """Create binary mask for inpainting (white = area to fill)"""
    h, w = image.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    
    if auto:
        x, y, rw, rh = detect_watermark_region(image)
        mask[y:y+rh, x:x+rw] = 255
        print(f"📍 Auto-detected watermark: x={x}, y={y}, w={rw}, h={rh}")
    elif roi:
        x, y, rw, rh = map(int, roi.split(','))
        mask[y:y+rh, x:x+rw] = 255
        print(f"📍 Using ROI: x={x}, y={y}, w={rw}, h={rh}")
    
    return mask

def preprocess_for_lama(image, mask):
    """Preprocess image and mask for LaMa model"""
    # LaMa expects specific input format
    # Resize to multiple of 8 (model requirement)
    h, w = image.shape[:2]
    new_h = (h // 8) * 8
    new_w = (w // 8) * 8
    
    if new_h != h or new_w != w:
        image = cv2.resize(image, (new_w, new_h))
        mask = cv2.resize(mask, (new_w, new_h))
    
    # Normalize image to [0, 1]
    image_norm = image.astype(np.float32) / 255.0
    
    # Convert BGR to RGB for model
    image_rgb = cv2.cvtColor(image_norm, cv2.COLOR_BGR2RGB)
    
    # Create 4-channel input (RGB + mask)
    mask_norm = mask.astype(np.float32) / 255.0
    input_tensor = np.concatenate([image_rgb, mask_norm[:, :, np.newaxis]], axis=2)
    
    # Add batch dimension and transpose to NCHW
    input_tensor = np.transpose(input_tensor[np.newaxis, :, :, :], (0, 3, 1, 2))
    
    return input_tensor, (h, w)

def run_lama_inpaint(image, mask, model_path):
    """Run LaMa inpainting using ONNX runtime"""
    try:
        import onnxruntime as ort
    except ImportError:
        print("❌ onnxruntime not installed. Install with: pip3 install onnxruntime")
        return None
    
    # Load model
    session = ort.InferenceSession(str(model_path))
    
    # Preprocess
    input_tensor, original_size = preprocess_for_lama(image, mask)
    
    # Get input/output names
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    
    # Run inference
    print("🤖 Running AI inpainting...")
    result = session.run([output_name], {input_name: input_tensor})[0]
    
    # Postprocess
    result = np.transpose(result[0], (1, 2, 0))  # NCHW to HWC
    result = np.clip(result * 255, 0, 255).astype(np.uint8)
    
    # Convert RGB back to BGR
    result_bgr = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)
    
    # Resize back to original size if needed
    if result_bgr.shape[0] != original_size[0] or result_bgr.shape[1] != original_size[1]:
        result_bgr = cv2.resize(result_bgr, (original_size[1], original_size[0]))
    
    return result_bgr

def run_sd_inpaint(image, mask):
    """Run Stable Diffusion inpainting (requires GPU)"""
    try:
        from diffusers import StableDiffusionInpaintPipeline
        import torch
        from PIL import Image
    except ImportError:
        print("❌ diffusers not installed. Install with: pip3 install diffusers transformers accelerate torch")
        return None
    
    print("🤖 Loading Stable Diffusion model...")
    
    # Convert to PIL
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    mask_pil = Image.fromarray(mask)
    
    # Load pipeline
    pipe = StableDiffusionInpaintPipeline.from_pretrained(
        "runwayml/stable-diffusion-inpainting",
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
    )
    
    if torch.cuda.is_available():
        pipe = pipe.to("cuda")
        print("✅ Using GPU")
    else:
        print("⚠️  Running on CPU (slow)")
    
    print("🎨 Generating inpainting...")
    result = pipe(
        prompt="",  # No prompt needed for watermark removal
        image=image_pil,
        mask_image=mask_pil,
        num_inference_steps=50,
    ).images[0]
    
    # Convert back to OpenCV format
    result_np = np.array(result)
    result_bgr = cv2.cvtColor(result_np, cv2.COLOR_RGB2BGR)
    
    return result_bgr

def process_image(image_path, model='lama', roi=None, auto_mask=False, mask_path=None):
    """Process a single image"""
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"❌ Failed to load: {image_path}")
        return None
    
    print(f"🖼️  Processing: {image_path}")
    
    # Load or download model
    if model == 'lama':
        model_path = download_model('lama')
        if not model_path:
            return None
    elif model == 'sd-inpaint':
        model_path = 'sd-inpaint'  # Placeholder
    else:
        print(f"⚠️  Model '{model}' not fully supported yet")
        model_path = None
    
    # Create mask
    if mask_path:
        mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
        if mask is None:
            print(f"❌ Failed to load mask: {mask_path}")
            return None
        print(f"📋 Using custom mask: {mask_path}")
    else:
        mask = create_mask(image, roi=roi, auto=auto_mask or (roi is None))
    
    # Run inpainting
    if model == 'lama' and model_path:
        result = run_lama_inpaint(image, mask, model_path)
    elif model == 'sd-inpaint':
        result = run_sd_inpaint(image, mask)
    else:
        # Fallback to OpenCV inpainting
        print("⚠️  Falling back to OpenCV inpainting")
        result = cv2.inpaint(image, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
    
    if result is None:
        return None
    
    # Save result
    input_path = Path(image_path)
    output_path = input_path.parent / f"{input_path.stem}_ai_no_watermark{input_path.suffix}"
    cv2.imwrite(str(output_path), result)
    print(f"✅ Saved to: {output_path}")
    
    return str(output_path)

def main():
    parser = argparse.ArgumentParser(description="AI-powered watermark removal")
    parser.add_argument("images", nargs="+", help="Image file(s) to process")
    parser.add_argument("--model", "-m", default="lama",
                        choices=["lama", "mat", "sd-inpaint"],
                        help="AI model to use (default: lama)")
    parser.add_argument("--roi", "-r", default=None,
                        help="Region of interest: x,y,width,height")
    parser.add_argument("--auto-mask", "-a", action="store_true",
                        help="Auto-detect watermark region")
    parser.add_argument("--mask", default=None,
                        help="Custom mask image (white = watermark area)")
    
    args = parser.parse_args()
    
    # Process each image
    results = []
    for image_path in args.images:
        result = process_image(
            image_path,
            model=args.model,
            roi=args.roi,
            auto_mask=args.auto_mask,
            mask_path=args.mask
        )
        if result:
            results.append(result)
    
    print(f"\n✅ Completed: {len(results)} image(s) processed with {args.model} model")
    
    return 0 if results else 1

if __name__ == "__main__":
    sys.exit(main())
