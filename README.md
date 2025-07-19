# vid2ascii

A simple tool that downloads a video from a URL and renders it as ASCII art in the terminal using only Python packages. It downloads the video with `yt-dlp`, reads frames with `opencv-python`, and converts them to ASCII characters with Pillow.

## Requirements

Install dependencies with pip:

```bash
pip install -r requirements.txt
```

## Usage

Run the program with a video URL:

```bash
python vid2ascii.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

The script downloads the video to a temporary location, converts each frame to ASCII art, and prints it to the terminal.
