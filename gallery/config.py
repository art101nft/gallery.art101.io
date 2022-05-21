import json
from os import getenv
from dotenv import load_dotenv

from gallery.constants import erc721_abi, erc1155_abi
from gallery.constants import marketplace_contract, marketplace_abi


load_dotenv()

# App
SECRET_KEY = getenv('SECRET_KEY', 'yyyyyyyyyyyyy')
SERVER_NAME = getenv('SERVER_NAME', '127.0.0.1:5000')
ETHERSCAN_API = getenv('ETHERSCAN_API', 'xxxxxxx')
IPFS_SERVER = getenv('IPFS_SERVER', 'http://127.0.0.1:8080')
DATA_PATH = getenv('DATA_PATH', '/opt/gallery.art101.io/data')
ASSETS_URL = getenv('ASSETS_URL', 'https://art101-assets.s3.us-west-2.amazonaws.com')
SCRAPER_API_URL = getenv('SCRAPER_API_URL', 'http://127.0.0.1:3000')
ERC721_ABI = erc721_abi
ERC1155_ABI = erc1155_abi
MARKETPLACE_ABI = marketplace_abi
MARKETPLACE_ADDRESS = marketplace_contract

# Cache
CACHE_HOST = getenv('CACHE_HOST', '127.0.0.1')
CACHE_PORT = getenv('CACHE_PORT', '6379')

# Logging
LOGGING_CONFIG = {
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'stream': 'ext://sys.stdout',
        },
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }
    },
    'loggers': {
        'gunicorn.error': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'gunicorn.access': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console'],
    }
}
