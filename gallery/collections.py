import requests
from json import dumps, loads
from ens.auto import ns

from gallery.helpers import get_eth_contract, Etherscan
from gallery.library.cache import cache
from gallery.tasks.collection import scan_tokens
from gallery import config


all_collections = {
    'non-fungible-soup': {
        'title': 'Non-Fungible Soup',
        'contract_address': '0xdc8bEd466ee117Ebff8Ee84896d6aCd42170d4bB',
        'total_supply': 2048,
        'start_token_id': 1,
        'contract_type': 'ERC-721',
        'notable_tokens': [43, 770, 589, 1617, 1952]
    },
    'mondriannft': {
        'title': 'MondrianNFT',
        'contract_address': '0x7f81858ea3b43513adfaf0a20dc7b4c6ebe72919',
        'total_supply': 4096,
        'start_token_id': 1,
        'contract_type': 'ERC-721'
    },
    'soupxmondrian': {
        'title': 'soupXmondrian',
        'contract_address': '0x0dD0CFeAE058610C88a87Da2D9fDa496cFadE108',
        'total_supply': 3,
        'start_token_id': 1,
        'contract_type': 'ERC-1155'
    },
    'bauhausblocks': {
        'title': 'Bauhaus Blocks',
        'contract_address': '0x62C1e9f6830098DFF647Ef78E1F39244258F7bF5',
        'total_supply': 8192,
        'start_token_id': 1,
        'contract_type': 'ERC-721'
    },
    'nftzine': {
        'title': 'NFTZine',
        'contract_address': '0xc918F953E1ef2F1eD6ac6A0d2Bf711A93D20Aa2b',
        'total_supply': 1000,
        'start_token_id': 1,
        'contract_type': 'ERC-721'
    },
    'basedvitalik': {
        'title': 'BASΞD VITALIK',
        'contract_address': '0xea2dc6f116a4c3d6a15f06b4e8ad582a07c3dd9c',
        'total_supply': 4962,
        'start_token_id': 0,
        'contract_type': 'ERC-721A'
    }
}

class Collection(object):
    def __init__(self, title):
        if title not in all_collections:
            return None
        self.title = all_collections[title]['title']
        self.url_slug = title
        self.contract_address = all_collections[title]['contract_address']
        self.contract = get_eth_contract(self.contract_address)
        es = Etherscan(self.contract_address)
        self.es_data = es.data
        self.data = all_collections[title]

    def _scan_tokens(self):
        sa0 = False
        if self.url_slug == 'basedvitalik':
            sa0 = True
        scan_tokens(self.contract_address, self.data['total_supply'], sa0)

    def retrieve_token_metadata(self, token_id):
        url = f'{config.ASSETS_URL}/{self.contract_address}/{token_id}.json'
        try:
            key_name = f'{self.contract_address}-metadata-{token_id}-v1.1'
            _d = cache.get_data(key_name)
            if _d:
                return loads(_d)
            else:
                r = requests.get(url, timeout=30, headers={'Content-Type': 'application/json'})
                r.raise_for_status()
                if 'name' in r.json():
                    _d = r.json()
                    try:
                        owner = self.contract.functions.ownerOf(int(token_id)).call()
                        _d['ownerOf'] = owner
                        _d['ownerENS'] = ns.name(owner)
                    except Exception as e:
                        print(e)
                        pass
                    cache.store_data(key_name, 604800, dumps(_d))
                    return _d
                else:
                    return {}
        except Exception as e:
            print(e)
            return {}
