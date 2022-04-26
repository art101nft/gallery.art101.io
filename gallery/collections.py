from gallery.helpers import get_eth_contract, Etherscan
from gallery.library.cache import cache
from gallery.tasks.collection import scan_tokens


all_collections = {
    'non-fungible-soup': {
        'title': 'Non-Fungible Soup',
        'contract_address': '0xdc8bEd466ee117Ebff8Ee84896d6aCd42170d4bB',
        'total_supply': 2048,
        'contract_type': 'ERC-721',
        'notable_tokens': [43, 770, 589, 1617, 1952]
    },
    'mondriannft': {
        'title': 'MondrianNFT',
        'contract_address': '0x7f81858ea3b43513adfaf0a20dc7b4c6ebe72919',
        'total_supply': 4096,
        'contract_type': 'ERC-721'
    },
    'soupxmondrian': {
        'title': 'soupXmondrian',
        'contract_address': '0x0dD0CFeAE058610C88a87Da2D9fDa496cFadE108',
        'total_supply': 3,
        'contract_type': 'ERC-1155'
    },
    'bauhausblocks': {
        'title': 'Bauhaus Blocks',
        'contract_address': '0x62C1e9f6830098DFF647Ef78E1F39244258F7bF5',
        'total_supply': 8192,
        'contract_type': 'ERC-721'
    },
    'nftzine': {
        'title': 'NFTZine',
        'contract_address': '0xc918F953E1ef2F1eD6ac6A0d2Bf711A93D20Aa2b',
        'total_supply': 1000,
        'contract_type': 'ERC-721'
    },
    'basedvitalik': {
        'title': 'BASΞD VITALIK',
        'contract_address': '0xea2dc6f116a4c3d6a15f06b4e8ad582a07c3dd9c',
        'total_supply': 4962,
        'contract_type': 'ERC-721A'
    }
}

class Collection(object):
    def __init__(self, title, data):
        self.title = data['title']
        self.url_slug = title
        self.contract_address = data['contract_address']
        self.contract = get_eth_contract(self.contract_address)
        es = Etherscan(self.contract_address)
        self.es_data = es.data
        self.data = data

    def _scan_tokens(self):
        sa0 = False
        if self.url_slug == 'basedvitalik':
            sa0 = True
        scan_tokens(self.contract_address, self.data['total_supply'], sa0)
