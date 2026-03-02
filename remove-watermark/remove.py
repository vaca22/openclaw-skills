#!/usr/bin/env python3
"""
remove-watermark - Remove watermarks from images using OpenCV
"""

import os
import sys
import argparse
import cv2
import numpy as np
from pathlib import Path

def detect_watermark_region(image):
    """
    Attempt to automatically detect watermark region.
    Looks for text-like regions in corners (common watermark locations).
    Returns (x, y, w, h) or None if not found.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    
    # Check corners (most common watermark positions)
    corners = [
        (0, 0, w // 4, h // 4),  # top-left
        (w * 3 // 4, 0, w // 4, h // 4),  # top-right
        (0, h * 3 // 4, w // 4, h // 4),  # bottom-left
        (w * 3 // 4, h * 3 // 4, w // 4, h // 4),  # bottom-right
    ]
    
    for x, y, cw, ch in corners:
        roi = gray[y:y+ch, x:x+cw]
        # Check if this region has different characteristics (likely watermark)
        if np.std(roi) < np.std(gray) * 0.5:  # Lower variance might indicate watermark
            return (x, y, cw, ch)
    
    # Default: assume bottom-right corner
    return (w * 3 // 4, h * 3 // 4, w // 4, h // 4)

def remove_watermark_inpaint(image, mask):
    """
    Use OpenCV inpainting to remove watermark.
    """
    # Telea algorithm (faster) or NS (better quality)
    result = cv2.inpaint(image, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
    return result

def remove_watermark_blur(image, x, y, w, h):
    """
    Apply Gaussian blur to watermark region.
    """
    result = image.copy()
    roi = result[y:y+h, x:x+w]
    blurred = cv2.GaussianBlur(roi, (21, 21), 0)
    result[y:y+h, x:x+w] = blurred
    return result

def remove_watermark_crop(image, x, y, w, h):
    """
    Crop out the watermark region.
    """
    h, w = image.shape[:2]
    # Crop to exclude the watermark area
    if x > w // 2:  # watermark on right
        return image[:, :x]
    elif y > h // 2:  # watermark on bottom
        return image[:y, :]
    else:
        return image

def remove_watermark_clone(image, x, y, w, h, src_x, src_y):
    """
    Clone from source region to cover watermark.
    """
    result = image.copy()
    # Simple clone: copy source region to watermark region
    result[y:y+h, x:x+w] = image[src_y:src_y+h, src_x:src_x+w]
    return result

def process_image(image_path, method='inpaint', position=None, roi=None):
    """
    Process a single image to remove watermark.
    """
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"❌ Failed to load image: {image_path}")
        return None
    
    h, w = image.shape[:2]
    
    # Determine watermark region
    if roi:
        # User specified ROI: x,y,width,height
        x, y, rw, rh = map(int, roi.split(','))
    elif position:
        # Position-based
        pw, ph = w // 4, h // 4
        positions = {
            'top-left': (0, 0, pw, ph),
            'top-right': (w - pw, 0, pw, ph),
            'bottom-left': (0, h - ph, pw, ph),
            'bottom-right': (w - pw, h - ph, pw, ph),
        }
        x, y, rw, rh = positions.get(position, positions['bottom-right'])
    else:
        # Auto-detect
        detected = detect_watermark_region(image)
        if detected:
            x, y, rw, rh = detected
        else:
            x, y, rw, rh = w * 3 // 4, h * 3 // 4, w // 4, h // 4
    
    print(f"📍 Watermark region: x={x}, y={y}, w={rw}, h={rh}")
    
    # Create mask for inpainting
    mask = np.zeros((h, w), dtype=np.uint8)
    mask[y:y+rh, x:x+rw] = 255
    
    # Apply selected method
    if method == 'inpaint':
        result = remove_watermark_inpaint(image, mask)
    elif method == 'blur':
        result = remove_watermark_blur(image, x, y, rw, rh)
    elif method == 'crop':
        result = remove_watermark_crop(image, x, y, rw, rh)
    elif method == 'clone':
        # For clone, use adjacent region as source
        src_x, src_y = max(0, x - rw), max(0, y - rh)
        result = remove_watermark_clone(image, x, y, rw, rh, src_x, src_y)
    else:
        print(f"❌ Unknown method: {method}")
        return None
    
    # Generate output path
    input_path = Path(image_path)
    output_path = input_path.parent / f"{input_path.stem}_no_watermark{input_path.suffix}"
    
    # Save result
    cv2.imwrite(str(output_path), result)
    print(f"✅ Saved to: {output_path}")
    
    return str(output_path)

def main():
    parser = argparse.ArgumentParser(description="Remove watermarks from images")
    parser.add_argument("images", nargs="+", help="Image file(s) to process")
    parser.add_argument("--method", "-m", default="inpaint", 
                        choices=["inpaint", "blur", "crop", "clone"],
                        help="Removal method (default: inpaint)")
    parser.add_argument("--position", "-p", default=None,
                        choices=["top-left", "top-right", "bottom-left", "bottom-right"],
                        help="Watermark position (auto-detect if not specified)")
    parser.add_argument("--roi", "-r", default=None,
                        help="Region of interest: x,y,width,height")
    
    args = parser.parse_args()
    
    # Check dependencies
    try:
        import cv2
        import numpy
    except ImportError:
        print("❌ Missing dependencies. Install with:")
        print("   pip3 install opencv-python numpy")
        sys.exit(1)
    
    # Process each image
    results = []
    for image_path in args.images:
        print(f"\n🖼️  Processing: {image_path}")
        result = process_image(image_path, args.method, args.position, args.roi)
        if result:
            results.append(result)
    
    print(f"\n✅ Completed: {len(results)} image(s) processed")
    
    return 0 if results else 1

if __name__ == "__main__":
    sys.exit(main())
