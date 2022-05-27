import requests
from quart import Blueprint, jsonify

from gallery import config
from gallery.collections import Collection, all_collections


bp = Blueprint('api', 'api', url_prefix='/api/v1')


@bp.route('/get_collection_events/<contract_address>')
async def get_collection_events(contract_address):
    collection_slug = None
    for slug in all_collections:
        if contract_address == all_collections[slug]['contract_address']:
            collection_slug = slug
    collection = Collection(collection_slug)
    if not collection:
        return jsonify({'error': True, 'reason': 'Collection does not exist'})
    try:
        return jsonify(collection.retrieve_collection_events())
    except Exception as e:
        return jsonify({'error': True, 'reason': e})

@bp.route('/get_token_sales/<contract_address>/<token_id>')
async def get_token_sales(contract_address, token_id):
    collection_slug = None
    for slug in all_collections:
        if contract_address == all_collections[slug]['contract_address']:
            collection_slug = slug
    collection = Collection(collection_slug)
    if not collection:
        return jsonify({'error': True, 'reason': 'Collection does not exist'})
    try:
        return jsonify(collection.retrieve_token_sales(token_id))
    except Exception as e:
        return jsonify({'error': True, 'reason': e})

@bp.route('/get_token_metadata/<contract_address>/<token_id>')
async def get_token_metadata(contract_address, token_id):
    collection_slug = None
    for slug in all_collections:
        if contract_address == all_collections[slug]['contract_address']:
            collection_slug = slug
    collection = Collection(collection_slug)
    if not collection:
        return jsonify({'error': True, 'reason': 'Collection does not exist'})
    try:
        return jsonify(collection.retrieve_token_metadata(token_id))
    except Exception as e:
        return jsonify({'error': True, 'reason': e})

@bp.route('/show_collection/<collection_slug>')
async def show_collection(collection_slug):
    collection = Collection(collection_slug)
    if not collection:
        return jsonify({'error': True, 'reason': 'Collection does not exist'})
    try:
        return jsonify(all_collections[collection_slug])
    except Exception as e:
        return jsonify({'error': True, 'reason': e})
