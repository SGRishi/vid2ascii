import os
import sys
import tempfile
from yt_dlp import YoutubeDL
import cv2


def download_video(url: str, output: str) -> None:
    """Download a video from `url` to the given output path."""
    ydl_opts = {"outtmpl": output, "quiet": True}
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def render_video(path: str, cols: int = 80) -> None:
    """Stream a video file as ASCII art in the terminal."""
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {path}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    target_width = cols
    target_height = int(height / width * target_width * 0.5)

    chars = "@%#*+=-:. "

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.resize(frame, (target_width, target_height))
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            ascii_frame = "\n".join(
                "".join(chars[pixel * (len(chars) - 1) // 255] for pixel in row)
                for row in gray
            )
            os.system("cls" if os.name == "nt" else "clear")
            print(ascii_frame)
    finally:
        cap.release()


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python vid2ascii.py <video-url>")
        raise SystemExit(1)

    url = sys.argv[1]
    with tempfile.TemporaryDirectory() as tmp:
        video_path = os.path.join(tmp, "video.mp4")
        download_video(url, video_path)
        render_video(video_path)


if __name__ == "__main__":
    main()

