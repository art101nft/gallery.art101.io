#!/usr/bin/env python3

import requests, json
from os.path import exists
from os import stat, mkdir

from gallery.collections import all_collections, Collection
from gallery.helpers import convert_ipfs_uri
from gallery import config


# download all collection metadata from ipfs
collections = [Collection(k) for k in all_collections]
for c in collections:
    print(f'[+] Fetching metadata for {c.title} - {c.contract_address}')
    traits = {
        'all': {},
        'by_token': {},
        'by_trait': {}
    }
    # set paths
    _p = f'{config.DATA_PATH}/{c.contract_address}'
    traits_folder = f'gallery/library/traits'
    trait_data = f'{traits_folder}/{c.url_slug}.json'
    # create folders
    if not exists(traits_folder):
        mkdir(traits_folder)
    if not exists(_p):
        mkdir(_p)
    # loop through tokens
    for token_id in range(c.data['start_token_id'], c.data['total_supply'] + c.data['start_token_id']):
        p = f'{_p}/{str(token_id)}.json'
        # save metadata
        if not exists(p) or stat(p).st_size == 0:
            print(f'{p} does not exist - fetching')
            token_uri = c.contract.functions.tokenURI(token_id).call()
            r = requests.get(convert_ipfs_uri(token_uri, False))
            r.raise_for_status()
            with open(p, 'w') as f:
                f.write(json.dumps(r.json()))
                print(f'saved {token_uri}:\n\n{r.json()}\n\n')
        # parse metadata to summarize all traits
        with open(p, 'r') as f:
            metadata = json.loads(f.read())
            # loop all traits
            for attribute in metadata['attributes']:
                trait_key = attribute['trait_type']
                trait_value = attribute['value']
                if trait_key == 'Generation':
                    continue
                # layout data structure
                if trait_key not in traits['all']:
                    traits['all'][trait_key] = []
                if trait_key not in traits['by_trait']:
                    traits['by_trait'][trait_key] = {}
                if trait_value not in traits['by_trait'][trait_key]:
                    traits['by_trait'][trait_key][trait_value] = []
                if trait_value not in traits['all'][trait_key]:
                    traits['all'][trait_key].append(trait_value)
                if token_id not in traits['by_token']:
                    traits['by_token'][token_id] = {}
                # add token_id to each trait
                if token_id not in traits['by_trait'][trait_key][trait_value]:
                    traits['by_trait'][trait_key][trait_value].append(token_id)
                # add traits to each token_id
                traits['by_token'][token_id][trait_key] = trait_value
    with open(trait_data, 'w') as f:
        f.write(json.dumps(traits))

