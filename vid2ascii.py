import os
import sys
import json
import tempfile
import subprocess
from yt_dlp import YoutubeDL
import aalib
from PIL import Image

def download_video(url, output):
    ydl_opts = {"outtmpl": output, "quiet": True}
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def get_video_size(path):
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "json",
            path,
        ],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    info = json.loads(result.stdout)
    stream = info["streams"][0]
    return stream["width"], stream["height"]

def render_video(path, cols=80):
    width, height = get_video_size(path)
    # adjust height to compensate for character aspect ratio
    target_width = cols
    target_height = int(height / width * target_width * 0.5)
    with tempfile.TemporaryDirectory() as tmp:
        frame_pattern = os.path.join(tmp, "frame_%05d.png")
        ffmpeg_cmd = [
            "ffmpeg",
            "-loglevel",
            "quiet",
            "-i",
            path,
            "-vf",
            f"scale={target_width}:{target_height}",
            frame_pattern,
        ]
        subprocess.run(ffmpeg_cmd, check=True)
        screen = aalib.AsciiScreen(width=target_width, height=target_height)
        frames = sorted(os.listdir(tmp))
        for frame in frames:
            img = Image.open(os.path.join(tmp, frame)).convert("L")
            screen.put_image((0, 0), img)
            art = screen.render()
            os.system("clear")
            print(art)

def main():
    if len(sys.argv) != 2:
        print("Usage: python vid2ascii.py <video-url>")
        sys.exit(1)
    url = sys.argv[1]
    with tempfile.TemporaryDirectory() as tmp:
        video_path = os.path.join(tmp, "video.mp4")
        download_video(url, video_path)
        render_video(video_path)

if __name__ == "__main__":
    main()
