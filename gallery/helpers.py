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
