#!/usr/bin/env python3

# python3 -m venv .venv
# .venv/bin/pip install requests bs4
# .venv/bin/python download_nftzine.py

import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# inputs
assets_bucket_url = "art101-assets.s3.us-west-2.amazonaws.com"
ipfs_metadata = "bafybeihsihtyvuswacjctzuifw5e32pr2isourvbpymk2ar7qth4j3tnza/nftzine"
contract_address = "0xc918F953E1ef2F1eD6ac6A0d2Bf711A93D20Aa2b"
token_id = input("[?] Enter token id: ")
partial_url = f"https://{assets_bucket_url}/{contract_address}"
full_url = f"{partial_url}/{ipfs_metadata}/{token_id}.json"

# get metadata
print(f"[/] Fetching metadata from {full_url}")
res = requests.get(full_url, timeout=4)
if not res.ok:
    print(f"[!] Error retrieving metadata: {res.content}")
    exit(1)
metadata = res.json()
animation_hash = metadata["animation_url"].replace("ipfs://", "")
animation_url = f"{partial_url}/{animation_hash}"

# get html
zine_folder = Path(f"nftzine_{token_id}")
zine_folder.mkdir(parents=True, exist_ok=True)
zine_index = Path(zine_folder, "index.html")
if not zine_index.exists():
    print(f"[/] Downloading NFTZine {animation_url}index.html")
    res = requests.get(f"{animation_url}index.html", timeout=4)
    if not res.ok:
        print(f"[!] Error downloading zine html: {res.content}")
        exit(1)
    with open(zine_index, "w") as f:
        f.write(res.content.decode())

# parse html and download assets
with open(zine_index, "r") as f:
    soup = BeautifulSoup(f.read(), "html.parser")
    img_tags = soup.find_all("img")
    style_tag = soup.find("style")
    if style_tag:
        css_content = style_tag.get_text()
        match = re.search(r"background-image:.*url\((.*)\)", css_content)
        if match:
            background_image = match.group(1)
            bg_url = f"{animation_url}{background_image}"
            bg_path = Path(zine_folder, background_image)
            if not bg_path.exists():
                print(f"[/] Downloading background {bg_url}")
                res = requests.get(bg_url, timeout=4)
                res.raise_for_status()
                if res.status_code == 200:
                    with open(bg_path, "wb") as f:
                        f.write(res.content)
    for img in img_tags:
        src = img.get("src")
        src_url = f"{animation_url}{src}"
        src_path = Path(zine_folder, src)
        if not src_path.exists():
            print(f"[/] Downloading image {src_url}")
            res = requests.get(src_url, timeout=4)
            res.raise_for_status()
            if res.status_code == 200:
                with open(src_path, "wb") as f:
                    f.write(res.content)

print(f"[:] {metadata['name']} downloaded to {zine_folder}. Open {zine_folder.resolve()}/index.html in a browser to view it.")