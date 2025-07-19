# vid2ascii

A simple tool that downloads a video from a URL and renders it as ASCII art in the terminal. It relies on `yt-dlp` to download the video, `ffmpeg` for frame extraction, and `python-aalib` for ASCII rendering.

## Requirements

Install dependencies with pip (and ensure FFmpeg and AAlib libraries are installed on your system):

```bash
pip install -r requirements.txt
```

On Debian/Ubuntu you may also need the following packages:

```bash
sudo apt-get install -y ffmpeg libaa1 libaa-bin
```

## Usage

Run the program with a video URL:

```bash
python vid2ascii.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

The script downloads the video to a temporary location, converts each frame to ASCII art, and prints it to the terminal.
