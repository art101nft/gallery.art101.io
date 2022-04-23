from json import dumps, loads

from gallery.helpers import get_eth_contract, Etherscan
from gallery.library.cache import cache


all_collections = {
    'non-fungible-soup': '0xdc8bEd466ee117Ebff8Ee84896d6aCd42170d4bB',
    'mondriannft': '0x7f81858ea3b43513adfaf0a20dc7b4c6ebe72919',
    # 'bauhausblocks': '0x62C1e9f6830098DFF647Ef78E1F39244258F7bF5',
    # 'nftzine': '0xc918F953E1ef2F1eD6ac6A0d2Bf711A93D20Aa2b',
}

class Collection:
    def __init__(self, title, contract_address):
        self.title = title
        self.contract_address = contract_address
        self.contract = get_eth_contract(contract_address)
        self.total_supply = self.get_total_supply()
        es = Etherscan(self.contract_address)
        self.data = es.data

    def get_total_supply(self):
        key_name = f'{self.title}-supply'
        _d = cache.get_data(key_name)
        if _d:
            return int(_d)
        else:
            _d = self.contract.functions.totalSupply().call()
            cache.store_data(key_name, 604800, int(_d))
            return int(_d)

COLLECTIONS = [
    Collection(k, v) for k, v in all_collections.items()
]
