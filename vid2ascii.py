#!/usr/bin/env python3
"""Interactive video to ASCII renderer implemented purely in Python."""

import os
import sys
import tempfile
import time

import cv2
import numpy as np
from yt_dlp import YoutubeDL

ASCII_CHARS = [" ", ".", ":", "-", "=", "+", "*", "#", "%", "@"]


def download_video(url: str, output: str) -> None:
    """Download the video from `url` to the given output path."""
    opts = {"outtmpl": output, "quiet": True}
    with YoutubeDL(opts) as ydl:
        ydl.download([url])


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
        video_path = os.path.join(tmp, "video.mp4")
        download_video(url, video_path)
        render_video(video_path, brightness, contrast, saturation)


if __name__ == "__main__":
    main()
