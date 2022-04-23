from json import dumps, loads

import requests
from web3.auto import w3

from gallery.library.cache import cache
from gallery.constants import erc721_abi
from gallery import config


def get_eth_contract(_contract_address):
    """
    Return a web3 contract object for standard ERC721
    token given the contract address.
    """
    contract_abi = erc721_abi
    contract_address = w3.toChecksumAddress(_contract_address)
    return w3.eth.contract(
        address=contract_address,
        abi=contract_abi
    )


class Etherscan:
    def __init__(self, contract_address):
        self.api_key = config.ETHERSCAN_API
        self.contract_address = contract_address
        self.base = f'https://api.etherscan.io/api?apikey={self.api_key}'
        self.data = self.get_contract_launch_tx()

    def get_contract_launch_tx(self):
        _d = cache.get_data(self.contract_address)
        if _d:
            return loads(_d)
        else:
            url = f'{self.base}&module=account&action=txlist&address={self.contract_address}&page=1&offset=10&sort=asc'
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            if 'result' in r.json():
                _d = r.json()['result'][0]
                cache.store_data(self.contract_address, 604800, dumps(_d))
                return _d
