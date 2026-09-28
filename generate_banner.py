#!/usr/bin/env python3
"""
=============================================================================
Custom Animated Banner Generator for GitHub Profile
Author: Prathmesh Nitnaware
=============================================================================
Takes the custom stylized banner background and animates ONLY the name:
"Prathmesh Nitnaware" with a smooth, measured typewriter effect and blinking cursor.
=============================================================================
"""

import os
import sys
import shutil
import math
import argparse
from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Ensure UTF-8 console output in Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Configuration Constants
# ---------------------------------------------------------------------------
NAME_TEXT = "Prathmesh Nitnaware"
DEFAULT_BG_NAME = "banner_bg.jpg"

# Source path from user upload (copied locally)
UPLOADED_SRC = r"C:\Users\Admin\.gemini\antigravity-ide\brain\991945dc-87ac-4850-9696-0f8a05fad9b6\.user_uploaded\media_1790599246433.jpg"

FPS = 20
DURATION_SEC = 6.0  # Slow, measured typing + comfortable reading pause
TOTAL_FRAMES = int(FPS * DURATION_SEC)


def ensure_background_file(bg_path: str = DEFAULT_BG_NAME) -> str:
    """Ensures background image exists locally in the workspace."""
    if not os.path.exists(bg_path):
        if os.path.exists(UPLOADED_SRC):
            shutil.copyfile(UPLOADED_SRC, bg_path)
            print(f"[*] Copied source image to {bg_path}")
    return bg_path


def get_font(font_names: List[str], size: int) -> ImageFont.FreeTypeFont:
    """Finds first available system font or falls back to default."""
    for font_name in font_names:
        try:
            return ImageFont.truetype(font_name, size)
        except (IOError, OSError):
            continue
    try:
        return ImageFont.truetype("arial.ttf", size)
    except (IOError, OSError):
        return ImageFont.load_default()


def render_banner_frame(
    base_img: Image.Image,
    full_text: str,
    font: ImageFont.FreeTypeFont,
    frame_idx: int,
    total_frames: int
) -> Image.Image:
    """
    Renders one frame of the slower, elegant typewriter animation.
    """
    width, height = base_img.size
    t = frame_idx / total_frames

    # Typing phase: 0% to 58% of duration (slower typing)
    # Pause phase: 58% to 100% of duration (hold complete name + blinking cursor)
    typing_end_t = 0.58
    total_chars = len(full_text)

    if t < typing_end_t:
        ratio = t / typing_end_t
        # Slower linear typing progression
        visible_count = int(ratio * (total_chars + 1))
        visible_count = min(total_chars, max(0, visible_count))
        is_typing = True
    else:
        visible_count = total_chars
        is_typing = False

    displayed_text = full_text[:visible_count]

    # Blinking terminal cursor (flashes every 6 frames)
    show_cursor = (frame_idx // 6) % 2 == 0
    cursor_char = "|"

    text_with_cursor = displayed_text + (cursor_char if show_cursor else "")

    # Layout: Center text horizontally within the left 60% of the banner (open red area)
    # Character is situated on the right side (~65% to 100%)
    active_area_width = int(width * 0.62)

    dummy_draw = ImageDraw.Draw(Image.new("RGBA", (width, height)))
    # Calculate bounding box for full string to keep position stable
    full_bbox = dummy_draw.textbbox((0, 0), full_text, font=font)
    full_w = full_bbox[2] - full_bbox[0]
    full_h = full_bbox[3] - full_bbox[1]

    # Center horizontally in active red area, and vertically in the banner
    tx = (active_area_width - full_w) // 2
    ty = (height - full_h) // 2 - 2

    # Create composite frame
    frame = base_img.copy().convert("RGBA")

    # 1. Subtle drop shadow for crisp comic/graphic contrast
    shadow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    shadow_draw.text((tx + 3, ty + 3), text_with_cursor, font=font, fill=(15, 0, 0, 180))
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=2))
    frame = Image.alpha_composite(frame, shadow_layer)

    # 2. Main Crisp Typography
    draw = ImageDraw.Draw(frame)
    draw.text((tx, ty), text_with_cursor, font=font, fill=(255, 255, 255, 255))

    return frame.convert("RGB")


def generate_banner(
    bg_path: str = DEFAULT_BG_NAME,
    output_path: str = "banner.gif",
    fps: int = FPS,
    duration: float = DURATION_SEC
) -> str:
    """Generates the animated typewriter banner GIF."""
    ensure_background_file(bg_path)

    if not os.path.exists(bg_path):
        raise FileNotFoundError(f"Background image not found: {bg_path}")

    # Load source background image
    with Image.open(bg_path) as src_img:
        orig_w, orig_h = src_img.size
        # Target standard crisp banner aspect ratio
        target_w = 900
        target_h = int(orig_h * (target_w / orig_w))
        base_bg = src_img.convert("RGB").resize((target_w, target_h), Image.Resampling.LANCZOS)

    total_frames = int(fps * duration)
    print("=" * 65)
    print("🎬 GENERATING CUSTOM TYPING BANNER GIF")
    print(f"• Name Text     : {NAME_TEXT}")
    print(f"• Dimensions    : {target_w} x {target_h} px")
    print(f"• Frame Rate    : {fps} FPS | Duration: {duration}s | Frames: {total_frames}")
    print("=" * 65)

    # Dynamic bold font matching the graphic art style
    font_size = int(target_h * 0.19)
    name_font = get_font(
        [
            "Segoe UI Bold",
            "Arial Bold",
            "Impact",
            "Trebuchet MS Bold",
            "Montserrat-Bold",
            "DejaVuSans-Bold"
        ],
        size=font_size
    )

    frames: List[Image.Image] = []
    for f_idx in range(total_frames):
        frame_rgb = render_banner_frame(
            base_bg,
            NAME_TEXT,
            name_font,
            f_idx,
            total_frames
        )

        # Quantize with adaptive palette & Floyd-Steinberg dithering for small file size and rich colors
        quantized = frame_rgb.quantize(
            colors=256,
            method=Image.Quantize.MEDIANCUT,
            dither=Image.Dither.FLOYDSTEINBERG
        )
        frames.append(quantized)

        if (f_idx + 1) % 20 == 0 or f_idx == total_frames - 1:
            prog = ((f_idx + 1) / total_frames) * 100
            print(f"  [Rendering] Frame {f_idx + 1}/{total_frames} ({prog:.1f}%)")

    print("[*] Optimizing & exporting banner.gif...")
    frame_dur_ms = int(1000 / fps)

    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        optimize=True,
        duration=frame_dur_ms,
        loop=0,
        disposal=2
    )

    size_kb = os.path.getsize(output_path) / 1024
    print(f"[✓] Banner generated successfully: {output_path} ({size_kb:.2f} KB)")
    print("=" * 65)
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate typing banner GIF.")
    parser.add_argument("--bg", type=str, default=DEFAULT_BG_NAME, help="Background image path")
    parser.add_argument("--output", type=str, default="banner.gif", help="Output GIF path")
    parser.add_argument("--fps", type=int, default=FPS, help="Frames per second")
    parser.add_argument("--duration", type=float, default=DURATION_SEC, help="Duration in seconds")
    args = parser.parse_args()

    generate_banner(
        bg_path=args.bg,
        output_path=args.output,
        fps=args.fps,
        duration=args.duration
    )
