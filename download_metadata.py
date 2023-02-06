#!/usr/bin/env python3

import requests, json
from os.path import exists
from os import stat, mkdir

from gallery.collections import all_collections, Collection
from gallery.helpers import convert_ipfs_uri
from gallery import config


collections = [Collection(k) for k in all_collections]
for c in collections:
    print(f'[+] Fetching metadata for {c.title} - {c.contract_address}')
    traits = {}
    _p = f'{config.DATA_PATH}/{c.contract_address}'
    traits_folder = f'gallery/library/traits'
    trait_data = f'{traits_folder}/{c.url_slug}.json'
    if not exists(traits_folder):
        mkdir(traits_folder)
    if not exists(_p):
        mkdir(_p)
    for token_id in range(c.data['start_token_id'], c.data['total_supply'] + c.data['start_token_id']):
        p = f'{_p}/{str(token_id)}.json'
        if not exists(p) or stat(p).st_size == 0:
            print(f'{p} does not exist - fetching')
            token_uri = c.contract.functions.tokenURI(token_id).call()
            r = requests.get(convert_ipfs_uri(token_uri, False))
            r.raise_for_status()
            with open(p, 'w') as f:
                f.write(json.dumps(r.json()))
                print(f'saved {token_uri}:\n\n{r.json()}\n\n')
        with open(p, 'r') as f:
            metadata = json.loads(f.read())
            for attribute in metadata['attributes']:
                trait_key = attribute['trait_type']
                attribute_value = attribute['value']
                if trait_key == 'Generation':
                    continue
                if trait_key not in traits:
                    traits[trait_key] = []
                if attribute_value not in traits[trait_key]:
                    traits[trait_key].append(attribute_value)
    with open(trait_data, 'w') as f:
        f.write(json.dumps(traits))

