# HSL-Downloader

# HLS / M3U8 Highest Quality Video Downloader

A Python script that parses an `.m3u8` master playlist, selects the stream with the highest `BANDWIDTH`, and downloads it as an `.mp4` file using `ffmpeg` with randomized request headers.

## Features

- Automatically parses `.m3u8` playlists to find the highest `BANDWIDTH` stream.
- Generates randomized `User-Agent` headers along with a configurable `Referer` header.
- Sanitizes output filenames and falls back to meaningful names based on the URL or timestamp when no custom title is provided.
- Remuxes/downloads streams directly into `.mp4` (`-c copy`) via `ffmpeg`.

## Prerequisites

1. **Python 3.8+**
2. **FFmpeg** installed on your system and available in your `PATH`:
   - **macOS (Homebrew):** `brew install ffmpeg`
   - **Ubuntu / Debian:** `sudo apt update && sudo apt install ffmpeg`
   - **Windows (winget):** `winget install Gyan.FFmpeg`

## Installation

Clone the repository and install the Python dependencies:

```bash
git clone https://github.com/arkar76011-cmd/HSL-Downloader.git
cd HSL-Downloader
pip install -r requirements.txt
