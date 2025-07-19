# vid2ascii

A simple tool that downloads a video from a URL and renders it as ASCII art in the terminal. It downloads the video with `yt-dlp`, extracts frames with `ffmpeg`, and uses `python-aalib` to display them as ASCII characters.

## Requirements

Install the Python dependencies and make sure `ffmpeg` and the `aalib` library are available on your system:

```bash
pip install -r requirements.txt
sudo apt-get install ffmpeg aalib1 libaa1  # or use your package manager
```

## Usage

Run the program and follow the prompts for the video URL and optional brightness/contrast/saturation values:

```bash
python vid2ascii.py
```

The script downloads the video, uses ffmpeg to extract frames, and streams them in ASCII directly in your terminal.
