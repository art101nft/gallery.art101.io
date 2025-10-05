from quart import Blueprint, render_template, flash
from quart import request, redirect, url_for

from gallery.collections import Collection, all_collections
from gallery.owners import Owner
from gallery import config


bp = Blueprint('collection', 'collection')


@bp.route('/')
async def index():
    c = [Collection(k) for k in all_collections]
    return await render_template('index.html', collections=c)

@bp.route('/collection/<collection_slug>')
async def show(collection_slug):
    collection = Collection(collection_slug)
    owner = None
    if not collection:
        await flash('That collection does not exist.', 'warning')
        return redirect('/')
    try:
        await request.get_data()
        a = request.args
        if a.get('wallet'):
            try:
                owner = Owner(str(a.get('wallet')))
            except Exception:
                await flash('Address provided is not allowed', 'critical')
        elif a.get('rankId'):
            i = a.get('rankId')
            if collection.token_id_is_allowed(i):
                return redirect(url_for('collection.show_token', collection_slug=collection.url_slug, token_id=collection.retrieve_token_id_by_rank(i)))
            await flash(f'Token provided is not allowed ({collection.token_start} - {collection.token_end})', 'error')
        elif a.get('tokenId'):
            i = a.get('tokenId')
            if collection.token_id_is_allowed(i):
                return redirect(url_for('collection.show_token', collection_slug=collection.url_slug, token_id=i))
            await flash(f'Token provided is not allowed ({collection.token_start} - {collection.token_end})', 'error')
    except Exception as e:
        print(e)
        await flash(e, 'error')
    return await render_template(
        'collection.html',
        collection=collection,
        owner=owner
    )

@bp.route('/collection/<collection_slug>/<int:token_id>')
async def show_token(collection_slug, token_id):
    collection = Collection(collection_slug)
    if not collection:
        await flash('That collection does not exist.', 'warning')
        return redirect('/')
    if token_id > collection.data['total_supply'] + collection.data['start_token_id'] - 1:
        await flash('That token does not exist for that collection!', 'warning')
        return redirect(url_for('collection.show', collection_slug=collection_slug))
    return await render_template(
        'token.html',
        collection=collection,
        token_id=token_id
    )

@bp.route('/collection/<collection_slug>/<int:token_id>/<size>')
async def show_image(collection_slug, token_id, size):
    if size not in ['fullsize', 'thumbnail']:
        size = 'fullsize'
    collection = Collection(collection_slug)
    if not collection:
        await flash('That collection does not exist.', 'warning')
        return redirect('/')
    if token_id > collection.data['total_supply'] + collection.data['start_token_id'] - 1:
        await flash('That token does not exist for that collection!', 'warning')
        return redirect(url_for('collection.show', collection_slug=collection_slug))
    meta = await collection.retrieve_token_metadata(token_id)
    image = meta['image'].replace('ipfs://', '')
    return redirect(f'{config.ASSETS_URL}/{collection.contract_address}/{image}.{size}.png')
