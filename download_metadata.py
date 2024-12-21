#!/usr/bin/env python3

"""
Iterate over all collections and download all
IPFS metadata to data/$CONTRACT_ADDRESS/$ID.json
"""

import requests
import json
from os.path import exists
from pathlib import Path
from os import stat, mkdir

from gallery.collections import all_collections, Collection
from gallery.helpers import convert_ipfs_uri
from gallery import config


try:
    collections = [Collection(k) for k in all_collections]
    for c in collections:
        collection_folder = Path(config.DATA_PATH, c.contract_address)
        if not exists(collection_folder):
            mkdir(collection_folder)
        for token_id in range(c.data['start_token_id'], c.data['total_supply'] + c.data['start_token_id']):
            token_metadata = Path(collection_folder, str(token_id) + '.json')
            if not exists(token_metadata) or stat(token_metadata).st_size == 0:
                print(f'{c.title} token {token_id} does not exist - fetching token URI from Infura and JSON body from IPFS')
                token_uri = c.contract.functions.tokenURI(token_id).call()
                req = requests.get(convert_ipfs_uri(token_uri, False))
                req.raise_for_status()
                with open(token_metadata, 'w') as f:
                    f.write(json.dumps(req.json()))
except KeyboardInterrupt:
    exit()