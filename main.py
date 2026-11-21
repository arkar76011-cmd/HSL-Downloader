import re
from datetime import datetime
from urllib.parse import urlparse, urljoin
import requests
import ffmpeg
from random_header_generator import HeaderGenerator


master_url = "https://example.com/index.m3u8"


custom_title = ""

random_header = HeaderGenerator(user_agents="program")
user_agent = random_header()["User-Agent"]

req_headers = {
    "User-Agent": user_agent,
    "Referer": "https://example.com/",
}

ffmpeg_headers = (
    f"User-Agent: {user_agent}\r\n"
    f"Referer: https://example.com/\r\n"
)


def sanitize_filename(name: str) -> str:
   
    cleaned = re.sub(r'[\\/:*?"<>|]+', "_", name).strip(" .")
    return cleaned or f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def build_output_filename(url: str, title: str = "", ext: str = ".mp4") -> str:
    if title and title.strip():
        base_name = sanitize_filename(title.strip())
        return f"{base_name}{ext}"

    parsed = urlparse(url)
    parts = [p for p in parsed.path.split("/") if p]

    generic_names = {"index.m3u8", "playlist.m3u8", "master.m3u8", "stream.m3u8", "hls.m3u8"}
    chosen = ""

    if parts:
        last_part = parts[-1]
        if last_part.lower() in generic_names and len(parts) >= 2:
            chosen = parts[-2]
        else:
            chosen = re.sub(r"\.m3u8$", "", last_part, flags=re.IGNORECASE)

    if not chosen or chosen.lower() in {"index", "playlist", "master", "stream", "hls"}:
        domain = parsed.netloc.replace("www.", "").split(".")[0] or "video"
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        chosen = f"{domain}_{stamp}"

    return f"{sanitize_filename(chosen)}{ext}"


def get_highest_quality_url(m3u8_url: str, headers: dict) -> str:
    resp = requests.get(m3u8_url, headers=headers, timeout=15)
    resp.raise_for_status()
    lines = [line.strip() for line in resp.text.splitlines() if line.strip()]

    best_bandwidth = -1
    best_url = m3u8_url

    for i, line in enumerate(lines):
        if line.startswith("#EXT-X-STREAM-INF:") and i + 1 < len(lines):
            bw_match = re.search(r"BANDWIDTH=(\d+)", line)
            bandwidth = int(bw_match.group(1)) if bw_match else 0
            stream_uri = lines[i + 1]
            if not stream_uri.startswith("#"):
                if bandwidth > best_bandwidth:
                    best_bandwidth = bandwidth
                    best_url = urljoin(m3u8_url, stream_uri)

    return best_url


target_url = get_highest_quality_url(master_url, req_headers)
output_file = build_output_filename(master_url, custom_title, ext=".mp4")

print("Selected highest quality stream:", target_url)
print("Saving as:", output_file)

(
    ffmpeg
    .input(
        target_url,
        extension_picky=0,
        allowed_segment_extensions="ALL",
        allowed_extensions="ALL",
        headers=ffmpeg_headers,
        protocol_whitelist="file,http,https,tcp,tls",
    )
    .output(output_file, c="copy")
    .run()
)
