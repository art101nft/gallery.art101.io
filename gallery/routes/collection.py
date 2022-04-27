from math import ceil

from flask import Blueprint, render_template, flash
from flask import request, redirect, url_for
from web3.auto import w3

from gallery import config
from gallery.collections import Collection, all_collections


bp = Blueprint('collection', 'collection')


@bp.route('/')
def index():
    c = [Collection(k) for k in all_collections]
    return render_template('index.html', collections=c)

@bp.route('/collection/<collection_slug>')
def show(collection_slug):
    collection = Collection(collection_slug)
    if not collection:
        flash('That collection does not exist.', 'warning')
        return redirect('/')
    return render_template(
        'collection.html',
        collection=collection
    )

@bp.route('/collection/<collection_slug>/<int:token_id>')
def show_token(collection_slug, token_id):
    collection = Collection(collection_slug)
    if not collection:
        flash('That collection does not exist.', 'warning')
        return redirect('/')
    if token_id > collection.data['total_supply'] + collection.data['start_token_id'] - 1:
        flash('That token does not exist for that collection!', 'warning')
        return redirect(url_for('collection.show', collection_slug=collection_slug))
    return render_template(
        'token.html',
        collection=collection,
        token_id=token_id
    )
