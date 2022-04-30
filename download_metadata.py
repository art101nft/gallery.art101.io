#!/usr/bin/env python3

import requests, json
from os.path import exists
from time import sleep

from gallery.collections import all_collections, Collection
from gallery.helpers import convert_ipfs_uri
from gallery import config


collections = [Collection(k) for k in all_collections]
for c in collections:
    print(f'[+] Fetching metadata for {c.title} - {c.contract_address}')
    _p = f'{config.DATA_PATH}/{c.contract_address}'
    for token_id in range(c.data['start_token_id'], c.data['total_supply'] - 1 + c.data['start_token_id']):
        p = f'{_p}/{str(token_id)}.json'
        if not exists(p):
            print(f'{p} does not exist - fetching')
            sleep(1)
            token_uri = c.contract.functions.tokenURI(token_id).call()
            r = requests.get(convert_ipfs_uri(token_uri), timeout=60)
            r.raise_for_status()
            with open(p, 'w') as f:
                f.write(json.dumps(r.json()))
                print(f'saved {token_uri}:\n\n{r.json()}\n\n')
