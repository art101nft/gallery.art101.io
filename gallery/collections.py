from json import dumps, loads

from gallery.helpers import get_eth_contract, Etherscan
from gallery.library.cache import cache


class Collection:
    def __init__(self, title, contract_address):
        self.title = title
        self.contract_address = contract_address
        self.contract = get_eth_contract(contract_address)
        self.total_supply = self.contract.functions.totalSupply().call()
        es = Etherscan(self.contract_address)
        self.data = es.data


COLLECTIONS = [
    Collection('non-fungible-soup', '0xdc8bEd466ee117Ebff8Ee84896d6aCd42170d4bB'),
    Collection('mondriannft', '0x7f81858ea3b43513adfaf0a20dc7b4c6ebe72919')
]
