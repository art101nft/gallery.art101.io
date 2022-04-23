from json import dumps, loads

from gallery.helpers import get_eth_contract, Etherscan
from gallery.library.cache import cache


class Collection:
    def __init__(self, title, contract_address):
        self.title = title
        self.contract_address = contract_address
        self.contract = get_eth_contract(contract_address)
        stored_info = cache.get_data(self.title)
        if stored_info:
            print('retrieved info from cache')
            _d = loads(stored_info)
            self.total_supply = _d['total_supply']
            self.block_number = _d['block_number']
            self.timestamp = _d['timestamp']
            self.tx_hash = _d['tx_hash']
            self.from_address = _d['from_address']
        else:
            print('stored info in cache')
            es = Etherscan(self.contract_address)
            print(es)
            launch_tx = es.get_contract_launch_tx()
            print(launch_tx)
            self.total_supply = self.contract.functions.totalSupply().call()
            self.block_number = launch_tx['blockNumber']
            self.timestamp = launch_tx['timeStamp']
            self.tx_hash = launch_tx['hash']
            self.from_address = launch_tx['from']
            cache.store_data(self.title, 86400, dumps({
                'total_supply': self.total_supply,
                'block_number': self.block_number,
                'timestamp': self.timestamp,
                'tx_hash': self.tx_hash,
                'from_address': self.from_address,
            }))


nfs = Collection('non-fungible-soup', '0xdc8bEd466ee117Ebff8Ee84896d6aCd42170d4bB')

COLLECTIONS = [
    nfs
]
