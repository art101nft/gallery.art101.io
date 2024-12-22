#!/usr/bin/env python3

"""
Iterate over all collections and download all
IPFS metadata to data/$CONTRACT_ADDRESS/$ID.json
"""

import requests
import json
from os.path import exists
from pathlib import Path
from os import stat

from gallery.collections import all_collections, Collection
from gallery.helpers import convert_ipfs_uri
from gallery import config

try:
    collections = [Collection(k) for k in all_collections]
    for c in collections:
        ipfs_hash = c.data['base_uri']
        ipfs_folder = Path(config.DATA_PATH, c.contract_address, ipfs_hash)
        if not exists(ipfs_folder):
            ipfs_folder.mkdir(parents=True, exist_ok=True)
        for token_id in range(c.data['start_token_id'], c.data['total_supply'] + c.data['start_token_id']):
            token_metadata = Path(ipfs_folder, f'{token_id}.json')
            if not exists(token_metadata) or stat(token_metadata).st_size == 0:
                print(f'{c.title} token {token_id} does not exist - fetching token URI from Infura and JSON body from IPFS')
                req = requests.get(convert_ipfs_uri(f'ipfs://{ipfs_hash}/{token_id}', False))
                req.raise_for_status()
                with open(token_metadata, 'w') as f:
                    f.write(json.dumps(req.json()))
except KeyboardInterrupt:
    exit()