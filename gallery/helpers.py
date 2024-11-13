from json import dumps, loads
from os import makedirs
from os.path import exists

import requests
from web3.auto import w3
from eth_account.messages import encode_defunct

from gallery.library.cache import cache
from gallery.constants import erc721_abi
from gallery import config


def verify_signature(message, signature, public_address):
    msg = encode_defunct(text=message)
    recovered = w3.eth.account.recover_message(msg, signature=signature)
    if recovered.lower() == public_address.lower():
        return True
    else:
        return False

def get_eth_contract(_contract_address):
    """
    Return a web3 contract object for standard ERC721
    token given the contract address.
    """
    contract_abi = erc721_abi
    contract_address = w3.to_checksum_address(_contract_address)
    return w3.eth.contract(
        address=contract_address,
        abi=contract_abi
    )

def convert_ipfs_uri(u, external=True):
    if u.startswith('ipfs://'):
        ipfs = u.split('ipfs://')[1]
        if external:
            return f'https://gateway.pinata.cloud/ipfs/{ipfs}'
        else:
            return f'{config.IPFS_SERVER}/ipfs/{ipfs}'
    else:
        return u

def store_json(contract_address: str, token_id: int, data: dict):
    _p = f'{config.DATA_PATH}/{contract_address}'
    p = f'{_p}/{str(token_id)}.json'
    makedirs(_p, exist_ok=True)
    if not exists(p):
        with open(p, 'w') as f:
            f.write(dumps(data))

class Etherscan:
    def __init__(self, contract_address):
        self.api_key = config.ETHERSCAN_API
        self.contract_address = contract_address
        self.base = f'https://api.etherscan.io/api?apikey={self.api_key}'
        self.data = self.get_contract_launch_tx()

    def get_contract_launch_tx(self):
        key_name = self.contract_address
        _d = cache.get_data(key_name)
        if _d:
            return loads(_d)
        else:
            url = f'{self.base}&module=account&action=txlist&address={self.contract_address}&page=1&offset=10&sort=asc'
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            if 'result' in r.json():
                _d = r.json()['result'][0]
                cache.store_data(key_name, 604800, dumps(_d))
                return _d
