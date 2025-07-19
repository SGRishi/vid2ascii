import os
import sys
import tempfile
import subprocess
import time
from yt_dlp import YoutubeDL
import aalib
from PIL import Image


def download_video(url: str, output: str) -> None:
    """Download a video from `url` to the given output path."""
    ydl_opts = {"outtmpl": output, "quiet": True}
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def extract_frames(video_path: str, out_dir: str, brightness: str, contrast: str, saturation: str) -> None:
    """Use ffmpeg to extract frames from a video applying basic filters."""
    os.makedirs(out_dir, exist_ok=True)
    filt = f"eq=brightness={brightness}:contrast={contrast}:saturation={saturation},fps=10"
    cmd = [
        "ffmpeg",
        "-i",
        video_path,
        "-vf",
        filt,
        os.path.join(out_dir, "frame_%05d.png"),
        "-hide_banner",
        "-loglevel",
        "error",
    ]
    subprocess.run(cmd, check=True)


def render_frames(out_dir: str) -> None:
    """Render extracted frames as ASCII art using python-aalib."""
    screen = aalib.AsciiScreen()
    frames = sorted(os.listdir(out_dir))
    for frame in frames:
        with Image.open(os.path.join(out_dir, frame)) as img:
            img = img.convert("L").resize(screen.virtual_size)
            screen.put_image((0, 0), img)
            print(screen.render(), end="\x1b[H", flush=True)
            time.sleep(0.1)


def main() -> None:
    url = input("Video URL: ").strip()
    if not url:
        print("No URL provided")
        return

    brightness = input("Brightness [-1..1] (default 0): ").strip() or "0"
    contrast = input("Contrast (>0) (default 1.0): ").strip() or "1.0"
    saturation = input("Saturation (>0) (default 1.0): ").strip() or "1.0"

    with tempfile.TemporaryDirectory() as tmp:
        video_path = os.path.join(tmp, "video.mp4")
        frame_dir = os.path.join(tmp, "frames")
        download_video(url, video_path)
        extract_frames(video_path, frame_dir, brightness, contrast, saturation)
        render_frames(frame_dir)


if __name__ == "__main__":
    main()

