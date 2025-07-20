# vid2ascii

A simple tool that downloads a video from a URL and converts it into a coloured ASCII video. Everything is implemented with pure Python packages so no external programs are required.

## Requirements

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Usage

Run the program and follow the prompts for the video URL and optional brightness, contrast, and saturation values. You will also be asked for the output filename. If you omit the extension the tool will append `.mp4` for you. The script is executable, so you can run it directly:

```bash
./vid2ascii.py
```

After downloading the video the program renders the frames as coloured ASCII art and saves them to an MP4 file at 60&nbsp;fps. Nothing is displayed in the terminal.
