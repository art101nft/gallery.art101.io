import os
import requests
from json import dumps, loads
from time import sleep

from gallery.tasks.config import huey, app
from gallery.helpers import get_eth_contract, convert_ipfs_uri
from gallery.library.cache import cache


@huey.task()
def scan_tokens(contract_address: str, supply: int, start_at_0=False):
    with app.app_context():
        if start_at_0:
            r = range(supply-1, -1, -1)
        else:
            r = range(supply, 0, -1)
        for token_id in r:
            key_name = f'{contract_address}-token-{token_id}'
            if not cache.get_data(key_name):
                print(f'fetching token info {key_name}')
                c = get_eth_contract(contract_address)
                token_uri = c.functions.tokenURI(token_id).call()
                owner_of = c.functions.ownerOf(token_id).call()
                try:
                    token_meta = requests.get(convert_ipfs_uri(token_uri), timeout=30)
                    token_meta.raise_for_status()
                    token_meta = token_meta.json()
                except:
                    token_meta = None
                data = {
                    'tokenURI': token_uri,
                    'ownerOf': owner_of,
                    'metadata': token_meta
                }
                cache.store_data(key_name, 604800, dumps(data))
                sleep(1)


# @huey.periodic_task(crontab(minute='30', hour='*/2'))
# def fetch_missed():
#     with app.app_context():
#         pass
