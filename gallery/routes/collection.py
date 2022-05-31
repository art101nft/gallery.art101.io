from math import ceil

from quart import Blueprint, current_app, render_template, flash
from quart import request, redirect, url_for
from ens.auto import ns
from web3.auto import w3

from gallery import config
from gallery.collections import Collection, all_collections
from gallery.owners import Owner


bp = Blueprint('collection', 'collection')


@bp.route('/')
async def index():
    c = [Collection(k) for k in all_collections]
    return await render_template('index.html', collections=c)

@bp.route('/collection/<collection_slug>', methods=['GET', 'POST'])
async def show(collection_slug):
    collection = Collection(collection_slug)
    owner = None
    if not collection:
        await flash('That collection does not exist.', 'warning')
        return redirect('/')
    if request.method == 'GET':
        try:
            await request.get_data()
            a = request.args
            if a.get('wallet'):
                try:
                    owner = Owner(str(a.get('wallet')))
                except:
                    await flash('Address provided is not allowed', 'warning')
            elif a.get('rankId'):
                i = a.get('rankId')
                if collection.token_id_is_allowed(i):
                    return redirect(url_for('collection.show_token', collection_slug=collection.url_slug, token_id=collection.retrieve_token_id_by_rank(i)))
                await flash(f'Token provided is not allowed ({collection.token_start} - {collection.token_end})', 'warning')
            elif a.get('tokenId'):
                i = a.get('tokenId')
                if collection.token_id_is_allowed(i):
                    return redirect(url_for('collection.show_token', collection_slug=collection.url_slug, token_id=i))
                await flash(f'Token provided is not allowed ({collection.token_start} - {collection.token_end})', 'warning')
        except Exception as e:
            print(e)
            await flash(e, 'error')
    elif request.method == 'POST':
        await request.get_data()
        a = request.data
        i = a.get('tokenId')
        if i and collection.token_id_is_allowed(i):
            return redirect(url_for('collection.show_token', collection_slug=collection.url_slug, token_id=i))
        await flash(f'Token provided is not allowed ({collection.token_start} - {collection.token_end})', 'warning')
    return await render_template(
        'collection.html',
        collection=collection,
        owner=owner
    )

@bp.route('/collection/<collection_slug>/offers')
async def show_offers(collection_slug):
    collection = Collection(collection_slug)
    if not collection:
        await flash('That collection does not exist.', 'warning')
        return redirect('/')
    if not collection.retrieve_collection_active_offers():
        await flash('No active offers at this time.', 'warning')
        return redirect(url_for('collection.show', collection_slug=collection.url_slug))
    return await render_template(
        'offers.html',
        collection=collection
    )

@bp.route('/collection/<collection_slug>/bids')
async def show_bids(collection_slug):
    collection = Collection(collection_slug)
    if not collection:
        await flash('That collection does not exist.', 'warning')
        return redirect('/')
    if not collection.retrieve_collection_active_bids():
        await flash('No active bids at this time.', 'warning')
        return redirect(url_for('collection.show', collection_slug=collection.url_slug))
    return await render_template(
        'bids.html',
        collection=collection
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

@bp.route('/activity')
async def activity():
    c = [Collection(k) for k in all_collections]
    for collection in c:
        if not collection:
            await flash('That collection does not exist.', 'warning')
            return redirect('/')
        collection.retrieve_collection_active_bids()
        collection.retrieve_collection_active_offers()
    return await render_template(
        'activity.html',
        collection=collection
    )
