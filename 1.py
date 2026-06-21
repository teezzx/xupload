import os
import re
import sys
import shutil
import subprocess
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def process_single_video(page_url, worker_id, download_dir):
    page_url = page_url.strip()
    if not page_url:
        return

    prefix = f"[Worker {worker_id}]"
    print(f"{prefix} Starting: {page_url}")

    try:
        response = requests.get(page_url, headers=headers, timeout=30)
        response.raise_for_status()
        html = response.text

        soup = BeautifulSoup(html, "html.parser")

        title = (
            soup.title.get_text(strip=True)
            if soup.title
            else f"video_{page_url.rstrip('/').split('/')[-1]}"
        )

        # Sanitize title for safe filename
        title = re.sub(r'[\\/:*?"<>|]', '', title)
        title = re.sub(r"\s+", " ", title).strip()

        # Search for video patterns using triple quotes to prevent syntax errors
        match = re.search(r"""https?://[^\s"']*2160m\.mp4[^\s"']*""", html)
        if not match:
            match = re.search(r"""https?://[^\s"']*720m\.mp4[^\s"']*""", html)

        if not match:
            print(f"{prefix} No video URL found")
            return

        video_url = match.group(0)
        current_url = video_url
        fileurl = None

        # Resolve redirects
        for _ in range(10):
            try:
                res = requests.head(
                    current_url,
                    allow_redirects=False,
                    headers=headers,
                    timeout=15
                )
                if res.status_code >= 400:
                    res = requests.get(
                        current_url,
                        allow_redirects=False,
                        stream=True,
                        headers=headers,
                        timeout=15
                    )
            except requests.RequestException:
                res = requests.get(
                    current_url,
                    allow_redirects=False,
                    stream=True,
                    headers=headers,
                    timeout=15
                )

            location = res.headers.get("Location")

            if "ahcdn.com" in current_url:
                fileurl = current_url
                break

            if not location:
                fileurl = current_url
                break

            current_url = urljoin(current_url, location)

        if not fileurl:
            fileurl = current_url

        print(f"{prefix} Title: {title}")
        print(f"{prefix} Downloading...")

        # Run aria2c with the User-Agent header passed over
        subprocess.run(
            [
                "aria2c",
                "-x16",
                "-s16",
                "-q",
                f"--header=User-Agent: {headers['User-Agent']}",
                "-o",
                f"{title}.mp4",
                "-d",
                download_dir,
                fileurl,
            ],
            check=True,
        )

        print(f"{prefix} Done: {title}.mp4")

    except Exception as e:
        print(f"{prefix} Error: {e}")


def get_urls():
    print("\\nPaste your links/text here.")
    print("Press Enter, then Ctrl+D (Linux/Mac) or Ctrl+Z (Windows) to finish processing, or simply press Enter twice:\\n")

    lines = []
    while True:
        try:
            line = input()
            if not line:
                break
            lines.append(line)
        except EOFError:
            break

    # Combine all input and find all valid HTTP/HTTPS links
    combined_text = " ".join(lines)
    found_urls = re.findall(r'(https?://[^\s,\"\'>]+)', combined_text)

    # Clean punctuation from the end of parsed URLs and deduplicate
    cleaned_urls = []
    seen = set()
    for url in found_urls:
        url_clean = url.rstrip(').,;\"\'')
        if url_clean and url_clean not in seen:
            seen.add(url_clean)
            cleaned_urls.append(url_clean)

    return cleaned_urls


def main():
    urls = get_urls()

    if not urls:
        print("No valid URLs detected.")
        return

    download_dir = "Movies"
    os.makedirs(download_dir, exist_ok=True)

    if not shutil.which("aria2c"):
        print("aria2c not found. Attempting install...")
        try:
            subprocess.run(
                ["apt-get", "update", "-y"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            subprocess.run(
                ["apt-get", "install", "-y", "aria2"],
                check=True
            )
        except Exception as e:
            print(f"Could not automatically install aria2: {e}. Please install it manually.")
            return

    print(f"\\nStarting download process for {len(urls)} target(s)...\\n")

    # Limit concurrent downloads to prevent overloading bandwidth
    max_workers = min(len(urls), 5)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                process_single_video,
                url,
                idx + 1,
                download_dir
            )
            for idx, url in enumerate(urls)
        ]

        for future in futures:
            future.result()

    print("\\nProcessing complete.")


if __name__ == "__main__":
    main()

