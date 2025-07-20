#!/usr/bin/env python3
"""Interactive video to ASCII renderer implemented purely in Python."""

import os
import sys
import tempfile
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from yt_dlp import YoutubeDL

ASCII_CHARS = [" ", ".", ":", "-", "=", "+", "*", "#", "%", "@"]

# Font settings for rendering ASCII to images
FONT = ImageFont.load_default()
bbox = FONT.getbbox("A")
CHAR_WIDTH, CHAR_HEIGHT = bbox[2] - bbox[0], bbox[3] - bbox[1]


def download_video(url: str, output_dir: str) -> str:
    """Download the video from `url` into `output_dir` and return the file path."""
    opts = {"outtmpl": os.path.join(output_dir, "video.%(ext)s"), "quiet": True}
    with YoutubeDL(opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
        except Exception as exc:
            raise RuntimeError(f"Video download failed: {exc}") from exc
        return ydl.prepare_filename(info)


def frame_to_ascii(frame: np.ndarray, width: int = 80) -> str:
    """Convert an image frame (BGR numpy array) to an ASCII string."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    aspect_ratio = h / w
    new_height = int(aspect_ratio * width * 0.55)
    resized = cv2.resize(gray, (width, new_height))
    chars = []
    for row in resized:
        line = "".join(ASCII_CHARS[pixel * (len(ASCII_CHARS) - 1) // 255] for pixel in row)
        chars.append(line)
    return "\n".join(chars)


def frame_to_ascii_image(frame: np.ndarray, width: int = 80) -> Image.Image:
    """Convert an image frame (BGR numpy array) to a colored ASCII PIL Image."""
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h, w = rgb.shape[:2]
    aspect_ratio = h / w
    new_height = int(aspect_ratio * width * 0.55)
    resized = cv2.resize(rgb, (width, new_height))
    img = Image.new("RGB", (width * CHAR_WIDTH, new_height * CHAR_HEIGHT), "black")
    draw = ImageDraw.Draw(img)
    for y in range(new_height):
        for x in range(width):
            r, g, b = resized[y, x]
            gray = int(0.299 * r + 0.587 * g + 0.114 * b)
            char = ASCII_CHARS[gray * (len(ASCII_CHARS) - 1) // 255]
            draw.text((x * CHAR_WIDTH, y * CHAR_HEIGHT), char, fill=(r, g, b), font=FONT)
    return img


def render_video(path: str, brightness: float, contrast: float, saturation: float) -> None:
    """Stream a video file as ASCII art with basic adjustments."""
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {path}")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # brightness/contrast adjustment
        frame = cv2.convertScaleAbs(frame, alpha=contrast, beta=brightness * 255)
        # saturation adjustment
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(float)
        hsv[:, :, 1] *= saturation
        hsv = np.clip(hsv, 0, 255).astype("uint8")
        frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        ascii_frame = frame_to_ascii(frame)
        sys.stdout.write("\x1b[H" + ascii_frame)
        sys.stdout.flush()
        time.sleep(1 / 30)

    cap.release()


def save_ascii_video(
    path: str,
    output_path: str,
    brightness: float,
    contrast: float,
    saturation: float,
    width: int = 80,
    fps: int = 60,
) -> None:
    """Convert `path` video to colored ASCII and save it as an MP4 file."""
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {path}")

    ret, frame = cap.read()
    if not ret:
        cap.release()
        raise RuntimeError("Unable to read video frames")

    frame = cv2.convertScaleAbs(frame, alpha=contrast, beta=brightness * 255)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(float)
    hsv[:, :, 1] *= saturation
    hsv = np.clip(hsv, 0, 255).astype("uint8")
    frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    ascii_img = frame_to_ascii_image(frame, width=width)
    size = ascii_img.size
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, size)
    out.write(cv2.cvtColor(np.array(ascii_img), cv2.COLOR_RGB2BGR))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.convertScaleAbs(frame, alpha=contrast, beta=brightness * 255)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(float)
        hsv[:, :, 1] *= saturation
        hsv = np.clip(hsv, 0, 255).astype("uint8")
        frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        ascii_img = frame_to_ascii_image(frame, width=width)
        out.write(cv2.cvtColor(np.array(ascii_img), cv2.COLOR_RGB2BGR))

    cap.release()
    out.release()


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

    with tempfile.TemporaryDirectory() as tmp:
        try:
            video_path = download_video(url, tmp)
        except RuntimeError as err:
            print(err)
            return
        render_video(video_path, brightness, contrast, saturation)
        print("Saving ASCII video to ascii_output.mp4 ...")
        try:
            save_ascii_video(
                video_path,
                "ascii_output.mp4",
                brightness,
                contrast,
                saturation,
            )
            print("Saved ascii_output.mp4")
        except RuntimeError as err:
            print(f"Failed to save video: {err}")


if __name__ == "__main__":
    main()
