#!/usr/bin/env python3
"""Download a video from a URL and save a coloured ASCII rendition as an MP4."""

import os
import sys
import tempfile

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from yt_dlp import YoutubeDL

ASCII_CHARS = [" ", ".", ":", "-", "=", "+", "*", "#", "%", "@"]


def download_video(url: str, output_dir: str) -> str:
    """Download the video from `url` into `output_dir` and return the file path."""
    opts = {
        "outtmpl": os.path.join(output_dir, "video.%(ext)s"),
        "quiet": True,
        "format": "best[ext=mp4]/best"
    }
    with YoutubeDL(opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
        except Exception as exc:
            raise RuntimeError(f"Video download failed: {exc}") from exc
        return ydl.prepare_filename(info)


def frame_to_ascii_image(frame: np.ndarray, width: int = 80) -> np.ndarray:
    """Convert a BGR image frame to a coloured ASCII art image."""
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h, w, _ = frame_rgb.shape
    aspect_ratio = h / w
    font = ImageFont.load_default()
    try:
        bbox = font.getbbox("A")
        fw, fh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    except AttributeError:
        # Fallback for older Pillow versions
        fw, fh = font.getsize("A")
    new_height = int(aspect_ratio * width * fh / fw)
    resized = cv2.resize(frame_rgb, (width, new_height))
    img = Image.new("RGB", (width * fw, new_height * fh), "black")
    draw = ImageDraw.Draw(img)

    for y in range(new_height):
        for x in range(width):
            r, g, b = resized[y, x]
            brightness = int((int(r) + int(g) + int(b)) / 3)
            ch = ASCII_CHARS[brightness * (len(ASCII_CHARS) - 1) // 255]
            draw.text((x * fw, y * fh), ch, fill=(int(r), int(g), int(b)), font=font)

    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def _adjust_frame(frame: np.ndarray, brightness: float, contrast: float, saturation: float) -> np.ndarray:
    """Apply brightness, contrast and saturation adjustments to a BGR frame."""
    frame = cv2.convertScaleAbs(frame, alpha=contrast, beta=brightness * 255)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(float)
    hsv[:, :, 1] *= saturation
    hsv = np.clip(hsv, 0, 255).astype("uint8")
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def save_ascii_video(path: str, out_path: str, brightness: float, contrast: float, saturation: float, width: int = 80, fps: int = 60) -> None:
    """Convert the video at `path` to coloured ASCII and save to `out_path`."""
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {path}")

    ret, frame = cap.read()
    if not ret:
        cap.release()
        raise RuntimeError("Unable to read video frames")

    frame = _adjust_frame(frame, brightness, contrast, saturation)
    ascii_img = frame_to_ascii_image(frame, width)
    h, w, _ = ascii_img.shape
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(out_path, fourcc, fps, (w, h))
    writer.write(ascii_img)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = _adjust_frame(frame, brightness, contrast, saturation)
        ascii_img = frame_to_ascii_image(frame, width)
        writer.write(ascii_img)

    writer.release()
    cap.release()


def main() -> None:
    url = input("Video URL: ").strip()
    if not url:
        print("No URL provided")
        return

    try:
        brightness = float(input("Brightness [-1..1] (default 0): ").strip() or 0)
        contrast = float(input("Contrast (>0) (default 1.0): ").strip() or 1.0)
        saturation = float(input("Saturation (>0) (default 1.0): ").strip() or 1.0)
    except ValueError:
        print("Invalid numeric value provided")
        return

    output_name = input("Output file name (without extension): ").strip() or "ascii_output"
    if not output_name.lower().endswith(".mp4"):
        output_name += ".mp4"

    with tempfile.TemporaryDirectory() as tmp:
        try:
            video_path = download_video(url, tmp)
        except RuntimeError as err:
            print(err)
            return

        print(f"Saving ASCII video to {output_name} ...")
        try:
            save_ascii_video(video_path, output_name, brightness, contrast, saturation)
        except RuntimeError as err:
            print(f"Failed to save video: {err}")
            return
        print("Done")


if __name__ == "__main__":
    main()
