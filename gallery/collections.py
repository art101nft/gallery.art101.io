import requests
from json import dumps, loads
from ens.auto import ns

from gallery.helpers import get_eth_contract, Etherscan
from gallery.library.cache import cache
from gallery import config


all_collections = {
    'non-fungible-soup': {
        'title': 'Non-Fungible Soup',
        'contract_address': '0xdc8bEd466ee117Ebff8Ee84896d6aCd42170d4bB',
        'description': 'Art101\'s flagship stealth drop which put us on the map. This was the first real drop as a newly established Art101 brand with an art-centric take on generative NFT and crypto art. The digital version of silk screening, Andy Warhol would have loved NFTs.',
        'website': 'https://nonfungiblesoup.io',
        'total_supply': 2048,
        'start_token_id': 1,
        'contract_type': 'ERC-721',
        'notable_tokens': [43, 770, 1952, 1617, 1876, 1162, 454, 2033]
    },
    'mondriannft': {
        'title': 'MondrianNFT',
        'contract_address': '0x7f81858ea3b43513adfaf0a20dc7b4c6ebe72919',
        'description': 'Art101\'s second drop paying homage to French artist Piet Mondrian. The collection spans the entirety of Piet\'s multiple styles, phases, and formats, with rarity that reflects his real-world collection but with a humanist take on generative art. Each one has small imperfections like cracked paint and jagged lines. Token ownership of Non-Fungible Soup allowed for early minting/claiming of the MondrianNFT tokens.',
        'website': 'https://mondriannft.io',
        'total_supply': 4096,
        'start_token_id': 1,
        'contract_type': 'ERC-721',
        'notable_tokens': [400, 1226, 1089, 3363, 846, 3855, 2592, 3369]
    },
    'soupxmondrian': {
        'title': 'soupXmondrian',
        'contract_address': '0x0dD0CFeAE058610C88a87Da2D9fDa496cFadE108',
        'description': 'The first exclusive commemorative companion drop of three multi-edition Andy Warhol and Piet Mondrian Vector Mash-Ups for owners of Non-Fungible Soup and MondrianNFT. Kicked off in the 1920s by Piet Mondrian, Abstract Expressionism rebuked the decadence of Art Deco in the post-war era. Just as Pop Art and artist\'s like Andy Warhol admonished Abstract Expressionism\'s loud strokes and lack of reference. Ironically, they work well together.',
        'website': 'https://soup.mondriannft.io',
        'total_supply': 3,
        'start_token_id': 1,
        'contract_type': 'ERC-1155'
    },
    'bauhausblocks': {
        'title': 'Bauhaus Blocks',
        'contract_address': '0x62C1e9f6830098DFF647Ef78E1F39244258F7bF5',
        'description': 'Bauhaus Blocks is a generative collection of Bauhaus-inspired NFTs created from 372 unique blocks concatenated in four different formats and palettes. Bauhaus was an early 19th-century art movement, which synthesized craft, technology, and aesthetics. Seeking the creation of a "total work." Or a that is, multiple works that act as one through aesthetic unity. An idea that lends itself to simple geometric shapes cascading with cohesion, the Bauhaus "brand".',
        'website': 'https://bauhausblocks.io',
        'total_supply': 8192,
        'start_token_id': 1,
        'contract_type': 'ERC-721',
        'notable_tokens': [6851, 404, 5618, 7172, 117, 1959, 2648, 1023]
    },
    'nftzine': {
        'title': 'NFTZine',
        'contract_address': '0xc918F953E1ef2F1eD6ac6A0d2Bf711A93D20Aa2b',
        'description': 'NFTZine is a crypto homage to a linchpin of the DIY art scene, the zine. They are generative, interactive and printable. A PDF copy of each NFT zine is attached to each tokens metadata. \'Art is Theft\' is issue #001.',
        'website': 'https://nftzine.io',
        'total_supply': 1000,
        'start_token_id': 1,
        'contract_type': 'ERC-721'
    },
    'basedvitalik': {
        'title': 'BASΞD VITALIK',
        'contract_address': '0xea2dc6f116a4c3d6a15f06b4e8ad582a07c3dd9c',
        'description': 'BASΞD VITALIK is a hyper-fauvist take on generative PFP NFTs and authentic homage to crypto-royalty; as eccentric and unapologetic as Vitalik Buterin himself. Pamp it, money-skelly.',
        'website': 'https://basedvitalik.io',
        'total_supply': 4962,
        'start_token_id': 0,
        'contract_type': 'ERC-721A',
        'notable_tokens': [2717, 501, 2714, 269, 2017, 102, 3228, 1289, 655]
    }
}

class Collection(object):
    def __init__(self, title):
        if title not in all_collections:
            return None
        self.data = all_collections[title]
        self.title = self.data['title']
        self.description = self.data['description']
        self.contract_address = self.data['contract_address']
        self.url_slug = title
        self.contract = get_eth_contract(self.contract_address)
        es = Etherscan(self.contract_address)
        self.es_data = es.data
        self.stats = self.retrieve_collection_stats()
        self.token_start = self.data['start_token_id']
        self.token_end = self.data['total_supply'] - 1 + self.token_start
        if 'contract_type' in self.data:
            if self.data['contract_type'] == 'ERC-1155':
                self.erc1155 = True
            else:
                self.erc1155 = False
        else:
            self.erc1155 = False

    def token_id_is_allowed(self, token_id):
        if not token_id.isnumeric():
            return False
        _token_id = int(token_id)
        if _token_id < self.token_start or _token_id > (self.token_end):
            return False
        return True

    def retrieve_collection_stats(self):
        key_name = f'opensea-stats-{self.url_slug}'
        _d = cache.get_data(key_name)
        if _d:
            return loads(_d)
        else:
            try:
                url = f'https://api.opensea.io/api/v1/collection/{self.url_slug}/stats'
                r = requests.get(url, headers={"Accept": "application/json"}, timeout=10)
                r.raise_for_status()
                if 'stats' in r.json():
                    _d = r.json()['stats']
                    cache.store_data(key_name, 604800, dumps(_d))
                    return _d
            except Exception as e:
                print(e)
                return {}

    def retrieve_token_metadata(self, token_id):
        url = f'{config.ASSETS_URL}/{self.contract_address}/{token_id}.json'
        try:
            key_name = f'{self.contract_address}-metadata-{token_id}-v1.6'
            _d = cache.get_data(key_name)
            if _d:
                return loads(_d)
            else:
                r = requests.get(url, timeout=30, headers={'Content-Type': 'application/json'})
                r.raise_for_status()
                if 'name' in r.json():
                    _d = r.json()
                    try:
                        if self.erc1155:
                            owner = None
                            _tokenURI = self.contract.functions.uri(int(token_id)).call()
                            i = hex(int(token_id)).lstrip('0x').zfill(64)
                            tokenURI = _tokenURI.replace('{id}', i)
                        else:
                            owner = self.contract.functions.ownerOf(int(token_id)).call()
                            tokenURI = self.contract.functions.tokenURI(int(token_id)).call()
                        _d['tokenURI'] = tokenURI
                        _d['tokenOffchainURI'] = f'{config.ASSETS_URL}/{self.contract_address}/{token_id}.json'
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
