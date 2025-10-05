from json import dumps, loads
from pathlib import Path

import requests
from ens.auto import ns

from gallery.helpers import get_eth_contract
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
        'notable_tokens': [43, 770, 1952, 1617, 1876, 1162, 454, 2033],
        'testnet_address': '0x1Ca311D37D3130C4C8Ff8686745178Ff4Dbdbb09',
        'base_uri': 'bafybeihsihtyvuswacjctzuifw5e32pr2isourvbpymk2ar7qth4j3tnza/nonfungiblesoup',
        'launch_date': '2021-08-27'
    },
    'mondriannft': {
        'title': 'MondrianNFT',
        'contract_address': '0x7f81858ea3b43513adfaf0a20dc7b4c6ebe72919',
        'description': 'Art101\'s second drop paying homage to Dutch artist Piet Mondrian. The collection spans the entirety of Piet\'s multiple styles, phases, and formats, with rarity that reflects his real-world collection but with a humanist take on generative art. Each one has small imperfections like cracked paint and jagged lines. Token ownership of Non-Fungible Soup allowed for early minting/claiming of the MondrianNFT tokens.',
        'website': 'https://mondriannft.io',
        'total_supply': 4096,
        'start_token_id': 1,
        'contract_type': 'ERC-721',
        'notable_tokens': [400, 1226, 1089, 3363, 846, 3855, 2592, 3369],
        'testnet_address': '0xBFC0a6468b8F462a6F6AE619Ff49bA05C99029f5',
        'base_uri': 'bafybeihsihtyvuswacjctzuifw5e32pr2isourvbpymk2ar7qth4j3tnza/mondriannft',
        'launch_date': '2021-09-16'
    },
    'soupxmondrian': {
        'title': 'soupXmondrian',
        'contract_address': '0x0dD0CFeAE058610C88a87Da2D9fDa496cFadE108',
        'description': 'The first exclusive commemorative companion drop of three multi-edition Andy Warhol and Piet Mondrian Vector Mash-Ups for owners of Non-Fungible Soup and MondrianNFT. Kicked off in the 1920s by Piet Mondrian, Abstract Expressionism rebuked the decadence of Art Deco in the post-war era. Just as Pop Art and artist\'s like Andy Warhol admonished Abstract Expressionism\'s loud strokes and lack of reference. Ironically, they work well together.',
        'website': 'https://soup.mondriannft.io',
        'total_supply': 3,
        'start_token_id': 1,
        'contract_type': 'ERC-1155',
        'testnet_address': '0xc2ccb2fd465c6c008b18ae1c26960dfd30bf2378',
        'base_uri': 'bafybeihsihtyvuswacjctzuifw5e32pr2isourvbpymk2ar7qth4j3tnza/soupxmondrian',
        'launch_date': '2021-10-03'
    },
    'bauhausblocks': {
        'title': 'Bauhaus Blocks',
        'contract_address': '0x62C1e9f6830098DFF647Ef78E1F39244258F7bF5',
        'description': 'Bauhaus Blocks is a generative collection of Bauhaus-inspired NFTs created from 372 unique blocks concatenated in four different formats and palettes. Bauhaus was an early 19th-century art movement, which synthesized craft, technology, and aesthetics. Seeking the creation of a "total work." Or a that is, multiple works that act as one through aesthetic unity. An idea that lends itself to simple geometric shapes cascading with cohesion, the Bauhaus "brand".',
        'website': 'https://bauhausblocks.io',
        'total_supply': 8192,
        'start_token_id': 1,
        'contract_type': 'ERC-721',
        'notable_tokens': [6851, 404, 5618, 7172, 117, 1959, 2648, 1023],
        'testnet_address': '0xC6597f7609b3dDF95a86e4B1291eFC9E03C786A4',
        'base_uri': 'bafybeihsihtyvuswacjctzuifw5e32pr2isourvbpymk2ar7qth4j3tnza/bauhausblocks',
        'launch_date': '2021-10-18'
    },
    'nftzine': {
        'title': 'NFTZine',
        'contract_address': '0xc918F953E1ef2F1eD6ac6A0d2Bf711A93D20Aa2b',
        'description': 'NFTZine is a crypto homage to a linchpin of the DIY art scene, the zine. They are generative, interactive and printable. A PDF copy of each NFT zine is attached to each tokens metadata. \'Art is Theft\' is issue #001.',
        'website': 'https://nftzine.io',
        'total_supply': 1000,
        'start_token_id': 1,
        'contract_type': 'ERC-721',
        'base_uri': 'bafybeihsihtyvuswacjctzuifw5e32pr2isourvbpymk2ar7qth4j3tnza/nftzine',
        'launch_date': '2021-11-27'
    },
    'basedvitalik': {
        'title': 'BASΞD VITALIK',
        'contract_address': '0xea2dc6f116a4c3d6a15f06b4e8ad582a07c3dd9c',
        'description': 'BASΞD VITALIK is a hyper-fauvist take on generative PFP NFTs and authentic homage to crypto-royalty; as eccentric and unapologetic as Vitalik Buterin himself. Pamp it, money-skelly.',
        'website': 'https://basedvitalik.io',
        'total_supply': 4962,
        'start_token_id': 0,
        'contract_type': 'ERC-721A',
        'notable_tokens': [2717, 2113, 2714, 2613, 2017, 3228, 1289, 2262],
        'base_uri': 'bafybeihsihtyvuswacjctzuifw5e32pr2isourvbpymk2ar7qth4j3tnza/basedvitalik',
        'launch_date': '2022-02-22'
    },
    'rmutt': {
        'title': 'R. Mutt',
        'contract_address': '0x6c61fB2400Bf55624ce15104e00F269102dC2Af4',
        'description': 'R. Mutt is a free-to-mint generative collection of 2,048 unique, meme-able, 3-D, and fully-interactive, NFT parodies of Marcel Duchamp\'s famous work, Fountain.<br/><br/> In a prank gone awry, Marcel Duchamp took the Society of Independent Artists\' up on an offer to display any work, so long as a fee was paid, at their first \'unjuried\' 1917 exhibition in Midtown Manhattan. He submitted Fountain. An upturned urinal, he bought down the street, and signed \'R. Mutt\'. The board, of which Duchamp was a member, refused to display the piece citing vulgarity and plagiarism. He resigned in protest, denouncing Parisian gatekeepers, while exclaiming, "Art is anything the artist says it is!" Duchamp\'s Fountain subsequently became one of the most influential works of the 21st century.<br/><br/>Like NFTs, Marcel Duchamp\'s Fountain forever changed the publics perception of art. A proto-meme, it\'s popularity upended traditionalism, subverted censorship, and birthed conceptual art. Without it, there would be no Warhol, no Hirst, no Goblintown.wtf. So, while collections like rektguy take the piss out of NFTs, let\'s memorialize the pisser that started it all.',
        'website': 'https://rmutt.io',
        'total_supply': 2048,
        'start_token_id': 0,
        'contract_type': 'ERC-721A',
        'notable_tokens': [164, 574, 554, 2010, 966, 1, 1233, 10],
        'base_uri': 'bafybeihsihtyvuswacjctzuifw5e32pr2isourvbpymk2ar7qth4j3tnza/rmutt',
        'launch_date': '2022-06-10'
    },
    'nftisse': {
        'title': 'NFT-isse',
        'contract_address': '0x343b68141129ec115c1fc523c5ae90586fe95b77',
        'description': 'After decades of trailblazing, Henri Matisse found himself bed-ridden, elderly, and unable to paint. Matisse turned almost exclusively to cutting painted paper as his primary medium. Initially kept secret, Henri cut organic and vegetal shapes and began collaging. An entirely novel idea at the time, Henri called the works \'cut-outs.\' They would become his best-known works of art. And early ancestor of generative art. NFT-isse is a derivative mashup of Henri Matisse\'s quintessential works, the cut-outs, and the NFTs we love.',
        'website': 'https://nftisse.io',
        'total_supply': 3072,
        'start_token_id': 0,
        'contract_type': 'ERC-721A',
        'notable_tokens': [170, 809, 1400, 3050, 45, 89, 2059, 1998],
        'base_uri': 'bafybeihsihtyvuswacjctzuifw5e32pr2isourvbpymk2ar7qth4j3tnza/nftisse',
        'launch_date': '2022-08-17'
    },
    'renascencenft': {
        'title': 'RenascenceNFT',
        'contract_address': '0x501a31185927136E87cDfC97dDd4553D8eC1bb4A',
        'description': 'Benozzo Gozzoli\'s Journey of the Magi is the preeminent illustration of Medici Florence. A painting more famous than the painter himself, the fresco depicts a young Lorenzo the Magnificent, supreme financier of the Renaissance, leading a procession of wise men. Commissioned in the 1450s by Cosimo de Medici for the family\'s private chapel, it encapsulates the relationship between creator and patron.',
        'website': 'https://renascencenft.xyz/',
        'total_supply': 4096,
        'start_token_id': 0,
        'contract_type': 'ERC-721A',
        'notable_tokens': [0, 1, 2, 3],
        'base_uri': 'bafybeihsihtyvuswacjctzuifw5e32pr2isourvbpymk2ar7qth4j3tnza/renascencenft',
        'launch_date': '2022-11-15'
    },
    'gasguzzlers': {
        'title': 'Gas Guzzlers',
        'contract_address': '0x87739a10f06c08468206008f6cf1abab8e6e9a0d',
        'description': 'A 512 NFT Web3 Parody of Ed Ruscha\'s Standard Station by ART101.',
        'website': 'https://gasguzzlers.art/',
        'total_supply': 512,
        'start_token_id': 1,
        'contract_type': 'ERC-721A',
        'notable_tokens': [7, 15, 5],
        'base_uri': 'bafybeihsihtyvuswacjctzuifw5e32pr2isourvbpymk2ar7qth4j3tnza/gasguzzlers',
        'launch_date': '2023-12-10'
    },
    'enzos': {
        'title': 'Enzos',
        'contract_address': '0x621b92370fe1a27f95e7109daf0423714b73e9b5',
        'description': 'Enzos is a FREE 5,555 PFP NFT homage to Lorenzo de Medici created by ART101.',
        'website': 'https://enzos.cash/',
        'total_supply': 5555,
        'start_token_id': 0,
        'contract_type': 'ERC-721A',
        'notable_tokens': [1, 5, 15],
        'base_uri': 'bafybeihsihtyvuswacjctzuifw5e32pr2isourvbpymk2ar7qth4j3tnza/enzos',
        'launch_date': '2023-06-04'
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
        self.token_start = self.data['start_token_id']
        self.token_end = self.data['total_supply'] - 1 + self.token_start
        self.testnet_address = self.data.get('testnet_address', None)
        self.stats = self.retrieve_collection_stats()
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
        url = f'{config.SCRAPER_API_URL}/api/{self.contract_address}/platforms'
        try:
            key_name = f'{self.contract_address}-sales-data-v1.7'
            _d = cache.get_data(key_name)
            if _d:
                return loads(_d)
            else:
                r = requests.get(url, timeout=4, headers={'Content-Type': 'application/json'})
                r.raise_for_status()
                if isinstance(r.json(), list):
                    platforms = r.json()
                    _d = {
                        'total_volume': 0,
                        'total_sales': 0,
                        'platforms': platforms
                    }
                    for platform in platforms:
                        _d['total_volume'] += float(platform['volume'])
                        _d['total_sales'] += int(platform['sales'])
                    cache.store_data(key_name, 604800, dumps(_d))
                    return _d
                else:
                    return {}
        except Exception as e:
            print(f'[!] Unable to fetch {self.title} sales stats from nft-sales-scraper')
            return {}

    def retrieve_token_id_by_rank(self, rank_number):
        try:
            with open(f'gallery/library/rarityscores/{self.url_slug}.json', 'r') as f:
                data = loads(f.read())
                return data['ranks'][str(rank_number)]
        except Exception:
            return 0

    def retrieve_token_by_id(self, token_id):
        try:
            with open(f'gallery/library/rarityscores/{self.url_slug}.json', 'r') as f:
                data = loads(f.read())
                return data[str(token_id)]
        except Exception:
            return {
                "stat_rarity": 0,
                "rarity_score": 0,
                "rarity_score_normed": 0,
                "rank": 0,
                "ranked_by": "none"
            }

    async def retrieve_token_sales(self, token_id):
        url = f'{config.SCRAPER_API_URL}/api/token/{self.contract_address}/{token_id}/history'
        try:
            key_name = f'{self.contract_address}-sales-{token_id}-v1.1'
            _d = cache.get_data(key_name)
            if _d:
                return loads(_d)
            else:
                r = requests.get(url, timeout=4, headers={'Content-Type': 'application/json'})
                r.raise_for_status()
                if isinstance(r.json(), list) and len(r.json()) > 0:
                    _d = r.json()
                    cache.store_data(key_name, 14400, dumps(_d))
                    return _d
                else:
                    return {}
        except Exception as e:
            print(f'[!] Unable to fetch {token_id} sales stats from nft-sales-scraper')
            return {}

    async def retrieve_token_metadata(self, token_id):
        key_name = f'{self.contract_address}-metadata-{token_id}-v1.6'
        try:
            _d = cache.get_data(key_name)
            if _d:
                return loads(_d)
        except Exception as e:
            print(e)
            return {}

        data = {}

        if config.LOCAL_MODE:
            metadata_path = Path(config.DATA_PATH, self.contract_address, self.data['base_uri'], f'{token_id}.json')
            if metadata_path.exists():
                data = loads(metadata_path.read_text())
            else:
                print(f'METADATA {token_id} does not exist!')
                return {}
        else:
            try:
                url = f'{config.ASSETS_URL}/{self.contract_address}/{self.data["base_uri"]}/{token_id}.json'
                r = requests.get(url, timeout=4, headers={'Content-Type': 'application/json'})
                r.raise_for_status()
                data = r.json()
            except Exception as e:
                print(e)
                return {}

        if 'name' in data:
            owner = None
            if self.erc1155:
                token_base = f'ipfs://{self.data["base_uri"]}'
                i = hex(int(token_id)).lstrip('0x').zfill(64)
                tokenURI = f'{token_base}/{i}'
            else:
                try:
                    owner = self.contract.functions.ownerOf(int(token_id)).call()
                except Exception as e:
                    print('Error getting token owner address', e)
                    owner = None
            tokenURI = f'ipfs://{self.data["base_uri"]}/{token_id}'
            data['tokenURI'] = tokenURI
            data['tokenOffchainURI'] = f'{config.ASSETS_URL}/{self.contract_address}/{self.data["base_uri"]}/{token_id}.json'
            data['ownerOf'] = owner
            if owner:
                try:
                    data['ownerENS'] = ns.name(owner)
                except Exception as e:
                    print('Error getting owner ENS address', e)
                    pass
            cache.store_data(key_name, 604800, dumps(data))
            return data
        else:
            return {}
