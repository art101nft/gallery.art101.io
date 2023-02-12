import re
from quart import Blueprint, jsonify, request

from gallery import config
from gallery.models import Profile
from gallery.helpers import verify_signature
from gallery.collections import Collection, all_collections


bp = Blueprint('api', 'api', url_prefix='/api/v1')


@bp.route('/get_collection_active_bids/<contract_address>')
async def get_collection_active_bids(contract_address):
    collection_slug = None
    for slug in all_collections:
        if contract_address == all_collections[slug]['contract_address']:
            collection_slug = slug
    collection = Collection(collection_slug)
    if not collection:
        return jsonify({'error': True, 'reason': 'Collection does not exist'})
    try:
        return jsonify(collection.retrieve_collection_active_bids())
    except Exception as e:
        return jsonify({'error': True, 'reason': e})

@bp.route('/get_collection_active_offers/<contract_address>')
async def get_collection_active_offers(contract_address):
    collection_slug = None
    for slug in all_collections:
        if contract_address == all_collections[slug]['contract_address']:
            collection_slug = slug
    collection = Collection(collection_slug)
    if not collection:
        return jsonify({'error': True, 'reason': 'Collection does not exist'})
    try:
        return jsonify(collection.retrieve_collection_active_offers())
    except Exception as e:
        return jsonify({'error': True, 'reason': e})

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

@bp.route('/get_tokens_by_trait/<contract_address>/<trait_key>/<trait_value>')
async def get_tokens_by_trait(contract_address, trait_key, trait_value):
    collection_slug = None
    for slug in all_collections:
        if contract_address == all_collections[slug]['contract_address']:
            collection_slug = slug
    collection = Collection(collection_slug)
    if not collection:
        return jsonify({'error': True, 'reason': 'Collection does not exist'})
    try:
        return jsonify(collection.retrieve_tokens_by_trait(trait_key, trait_value))
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

@bp.route('/show_tokens_by_rank/<collection_slug>')
async def show_tokens_by_rank(collection_slug):
    collection = Collection(collection_slug)
    data = {}
    for token_id in range(collection.token_start, collection.token_end + 1):
        rarity = collection.retrieve_token_by_id(token_id)
        data[rarity["rank"]] = token_id
    return jsonify(data)

@bp.route('/check_address_exists')
async def check_address_exists():
    """
    Check to see if a given address exists in the database to save profile info.
    This logic will help the login/connect workflow.
    """
    if 'address' not in request.args:
        return jsonify({'success': False})

    p = Profile.select().where(Profile.address == request.args['address'].lower()).first()
    if p:
        nonce = p.nonce
    else:
        nonce = Profile().generate_nonce()
    return jsonify({
        'user_exists': p is not None,
        'nonce': nonce,
        'success': True,
        'socials': {
            'discord': p is not None and len(p.discord) > 0,
            'twitter': p is not None and len(p.twitter) > 0,
            'email': p is not None and len(p.email) > 0
        }
    })


@bp.route('/save_profile', methods=['POST'])
async def save_profile():
    """
    This route stores profile info after successfully verifying a signature
    provided by the user. They POST a `signedData` blob; a message signed by
    the user with MetaMask (`personal_sign` method).
    """
    data = await request.get_json()

    prof = Profile.select().where(
        Profile.address == data['address'].strip().lower()
    ).first()

    # Check signature of provided payload
    signature_good = verify_signature(
        data['message'],
        data['signed_data'],
        data['address']
    )

    # Error if invalid signature
    if not signature_good:
        return jsonify({'success': False, 'message': 'Invalid signature'})

    if prof:
        # Error if current nonce does not match stored nonce
        if not data['message'].endswith(prof.nonce):
            return jsonify({'success': False, 'message': 'Invalid nonce'})
    else:
        # Create profile if it doesn't exist
        prof = Profile(address=data['address'].strip().lower())
        prof.change_nonce()

    # Save info
    for svc in ['discord', 'twitter', 'email']:
        # If provided data is not the same as stored and not all asterisks, save it
        if data[svc] != getattr(prof, svc) and not re.match(r'^[*]+$', data[svc]):
            setattr(prof, svc, data[svc].strip())

    prof.save()

    return jsonify({
        'success': True,
        'message': 'Updated user profile',
        'profile': prof.show()
    })
