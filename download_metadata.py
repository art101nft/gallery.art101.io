#!/usr/bin/env python3

"""
Iterate over all collections and download all
IPFS metadata to data/$CONTRACT_ADDRESS/$ID.json
"""

import json
import subprocess
from pathlib import Path
from os import stat

import requests
from bs4 import BeautifulSoup

from gallery.collections import all_collections, Collection
from gallery.helpers import convert_ipfs_uri
from gallery import config

s3_bucket = 'art101-assets'

try:
    collections = [Collection(k) for k in all_collections]
    for c in collections:
        ipfs_hash = c.data['base_uri']
        contract_folder = Path(config.DATA_PATH, c.contract_address)
        ipfs_folder = Path(contract_folder, ipfs_hash)
        if not ipfs_folder.exists():
            ipfs_folder.mkdir(parents=True, exist_ok=True)

        # Download token metadata from IPFS
        for token_id in range(c.data['start_token_id'], c.data['total_supply'] + c.data['start_token_id']):
            try:
                token_metadata = Path(ipfs_folder, f'{token_id}.json')
                if not token_metadata.exists() or stat(token_metadata).st_size == 0:
                    print(f'Downloading {c.title} {token_id} metadata')
                    if c.data['contract_type'] == 'ERC-1155':
                        token_id = f"{token_id:064d}"
                    req = requests.get(convert_ipfs_uri(f'ipfs://{ipfs_hash}/{token_id}', False), timeout=5)
                    req.raise_for_status()
                    with open(token_metadata, 'w') as f:
                        f.write(json.dumps(req.json()))

                with open(token_metadata, "r") as f:
                    metadata = json.loads(f.read())
                    image_hash = metadata['image'].replace('ipfs://', '')

                    # Non-Fungible Zine has animations and HTML files
                    if c.title == 'NFTZine':
                        animation_hash = metadata['animation_url']
                        animation_url = convert_ipfs_uri(animation_hash, False)
                        animation_folder = Path(contract_folder, animation_hash.replace('ipfs://', ''))
                        animation_folder.mkdir(parents=True, exist_ok=True)
                        animation_idx = Path(animation_folder, "index.html")
                        if not animation_idx.exists():
                            print(f"Downloading NFTZine {animation_url}index.html")
                            req = requests.get(animation_url, timeout=10)
                            req.raise_for_status()
                            if req.status_code == 200:
                                with open(animation_idx, 'w') as f:
                                    f.write(req.content.decode())
                        with open(animation_idx, 'r') as f:
                            soup = BeautifulSoup(f.read(), 'html.parser')
                            img_tags = soup.find_all('img')
                            for img in img_tags:
                                src = img.get('src')
                                src_path = Path(animation_folder, src)
                                if not src_path.exists():
                                    src_url = convert_ipfs_uri(f'{animation_hash}{src}', False)
                                    print(f'Downloading {src_url}')
                                    req = requests.get(src_url, timeout=10)
                                    req.raise_for_status()
                                    if req.status_code == 200:
                                        with open(src_path, 'wb') as f:
                                            f.write(req.content)

                    # Rmutt has animation files
                    if c.title == 'R. Mutt':
                        animation_ipfs = metadata['animation_url']
                        animation_hash_base, animation_src = animation_ipfs.replace('ipfs://', '').split('/')
                        animation_url = convert_ipfs_uri(animation_ipfs, False)
                        animation_folder = Path(contract_folder, animation_hash_base)
                        animation_folder.mkdir(parents=True, exist_ok=True)
                        animation_path = Path(animation_folder, animation_src)
                        if not animation_path.exists():
                            print(f'Downloading {animation_url}')
                            req = requests.get(animation_url, timeout=10)
                            req.raise_for_status()
                            with open(animation_path, 'wb') as f:
                                f.write(req.content)

                    # Download the image
                    image_path = Path(contract_folder, image_hash)
                    parts = image_hash.split('/')

                    if len(parts) > 1:
                        image_folder = Path(contract_folder, parts[0])
                        image_folder.mkdir(parents=True, exist_ok=True)
                        image_path = Path(image_folder, parts[1])
                        if not image_path.exists():
                            image_url = convert_ipfs_uri(metadata['image'], False)
                            print(f"Downloading {c.title} {token_id} image")
                            req = requests.get(image_url, timeout=10)
                            req.raise_for_status()
                            with open(image_path, 'wb') as f:
                                f.write(req.content)
                        fullsize_path = Path(image_folder, parts[1] + ".fullsize.png")
                        if not fullsize_path.exists():
                            print(f"Creating {c.title} {token_id} fullsize")
                            subprocess.run(['convert', image_path, fullsize_path], capture_output=False)
                        thumbnail_path = Path(image_folder, parts[1] + ".thumbnail.png")
                        if not thumbnail_path.exists():
                            print(f"Creating {c.title} {token_id} thumbnail")
                            subprocess.run(['convert', '-resize', '20%', image_path, thumbnail_path], capture_output=False)
                    else:
                        image_path = Path(contract_folder, parts[0])
                        if not image_path.exists():
                            image_url = convert_ipfs_uri(metadata['image'], False)
                            print(f"Downloading {c.title} {token_id} image")
                            req = requests.get(image_url, timeout=10)
                            req.raise_for_status()
                            with open(image_path, 'wb') as f:
                                f.write(req.content)
                        fullsize_path = Path(contract_folder, parts[0] + ".fullsize.png")
                        if not fullsize_path.exists():
                            print(f"Creating {c.title} {token_id} fullsize")
                            if c.title in ['Bauhaus Blocks', 'NFTZine']:
                                subprocess.run(['convert', image_path, fullsize_path], capture_output=False)
                            else:
                                cat_proc = subprocess.Popen(['cat', image_path], stdout=subprocess.PIPE)
                                inkscape_proc = subprocess.Popen(
                                    ['inkscape', '-p', '-C', '--export-dpi=30', '--export-type=png'],
                                    stdin=cat_proc.stdout,
                                    stdout=subprocess.PIPE
                                )
                                convert_proc = subprocess.Popen(
                                    ['convert', '-', fullsize_path],
                                    stdin=inkscape_proc.stdout
                                )
                                cat_proc.stdout.close()
                                convert_proc.communicate()
                        thumbnail_path = Path(contract_folder, parts[0] + ".thumbnail.png")
                        if not thumbnail_path.exists():
                            print(f"Creating {c.title} {token_id} thumbnail")
                            res = subprocess.run(['convert', '-resize', '20%', fullsize_path, thumbnail_path], capture_output=False)
            except Exception as e:
                print(f"failure...{e}")

    for c in collections:

        base_sync = [
            'aws', 's3', 'sync', str(Path(config.DATA_PATH, c.contract_address)), f's3://{s3_bucket}/{c.contract_address}/'
        ]

        print(f'Syncing {c.title} JSON assets')
        subprocess.run(base_sync + [
            '--exclude', '*',
            '--include', '*.json',
            '--content-type', 'application/json'
        ])

        print(f'Syncing {c.title} PNG assets')
        subprocess.run(base_sync + [
            '--exclude', '*',
            '--include', '*.png',
            '--content-type', 'image/png'
        ])

        if c.title in ['Non-Fungible Soup', 'MondrianNFT', 'soupXmondrian']:
            print(f'Syncing {c.title} SVG assets')
            subprocess.run(base_sync + [
                '--exclude', '*.json',
                '--exclude', '*.png',
                '--include', '*',
                '--content-type', 'image/svg+xml'
            ])

        if c.title in ['NFTZine']:
            print(f'Syncing {c.title} HTML assets')
            subprocess.run(base_sync + [
                '--exclude', '*',
                '--include', '*.html',
                '--content-type', 'text/html'
            ])

        if c.title in ['R. Mutt']:
            print(f'Syncing {c.title} GLB assets')
            subprocess.run(base_sync + [
                '--exclude', '*',
                '--include', '*.glb',
                '--content-type', 'model/gltf-binary'
            ])

    #     print(f"Creating {c.title} archive")
    #     Path('data/archives').mkdir(parents=True, exist_ok=True)
    #     subprocess.run([
    #         'tar', '-czvf', f'data/archives/{c.title}.tar.gz', '--exclude=*.fullsize.png', '--exclude=*.thumbnail.png', f'data/{c.contract_address}'
    #     ])

    # print('Syncing archives')
    # subprocess.run([
    #     'aws', 's3', 'sync', 'data/archives', f's3://{s3_bucket}/archives/'
    # ])

except KeyboardInterrupt:
    exit()