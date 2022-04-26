from flask import Blueprint
from arrow import get as arrow_get
from urllib.parse import urlencode

from gallery.helpers import get_eth_contract
from gallery import config


bp = Blueprint('filters', 'filters')


@bp.app_template_filter('shorten_address')
def shorten_address(a):
    _p = a[0:6]
    _s = a[-4:]
    return f'{_p}...{_s}'

# @bp.app_template_filter('get_token_metadata')
# def get_token_metadata(contract_address: str, token_id: int):
#

@bp.app_template_filter('humanize')
def humanize(d):
    if not d:
        return 'never'
    return arrow_get(d).humanize()

@bp.app_template_filter('from_ts')
def from_ts(s):
    return arrow_get(int(s)).datetime

@bp.app_template_filter('convert_ipfs_uri')
def convert_ipfs_uri(u):
    ipfs = u.split('ipfs://')[1]
    return f'https://gateway.pinata.cloud/ipfs/{ipfs}'

@bp.app_template_filter("fix_args")
def trim_arg(all_args):
    d = all_args.to_dict()
    if d:
        return '?' + urlencode(d)
    else:
        return ''

@bp.app_template_filter('show_etherscan')
def show_etherscan(a):
    return f'https://etherscan.io/address/{a}'
