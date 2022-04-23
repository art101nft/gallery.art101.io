from math import ceil

from flask import Blueprint, render_template, flash
from flask import request, redirect, url_for
from flask_login import current_user
from web3.auto import w3

from gallery import config
from gallery.collections import Collection, all_collections


bp = Blueprint('collection', 'collection')


@bp.route('/')
def index():
    c = [Collection(k, v) for k, v in all_collections.items()]
    return render_template('index.html', collections=c)

@bp.route('/collection/<collection_slug>')
def show(collection_slug):
    if collection_slug not in all_collections:
        flash('That collection does not exist.')
        return redirect('/')
    collection = Collection(collection_slug, all_collections[collection_slug])
    return render_template(
        'collection.html',
        collection=collection
    )

@bp.route('/collection/<collection_id>/<token_id>')
def show_token(collection_id, token_id):
    prev, next = None, None
    collection = Collection.query.get(collection_id)
    if not collection:
        flash('That collection does not exist!', 'warning')
        return redirect(url_for('collection.index'))
    token = Token.query.filter(
        Token.token_id == token_id,
        Token.collection_id == collection_id
    ).first()
    if not token:
        flash('That token does not exist for that collection!', 'warning')
        return redirect(url_for('collection.show', collection_id=collection_id))
    if current_user.is_anonymous:
        flash('Must be authenticated.', 'warning')
        return redirect(url_for('collection.index'))
    if not collection.user_can_access(current_user.id):
        flash('You are not allowed to access that collection.', 'warning')
        return redirect(url_for('collection.index'))

    _show = request.args.get('show')
    rejected, approved, all = False, False, False
    if _show == 'rejected':
        rejected = True
    elif _show == 'approved':
        approved = True
    else:
        all = True
    tokens = collection.get_tokens(rejected=rejected, approved=approved, all=all).all()
    index = tokens.index(token)
    if index + 1 < len(tokens):
        next = tokens[index + 1]
    if index > 0:
        prev = tokens[index - 1]
    return render_template(
        'token.html',
        token=token,
        prev=prev,
        next=next
    )

@bp.route('/collection/<collection_id>/<token_id>/<action>')
def update_token(collection_id, token_id, action):
    collection = Collection.query.get(collection_id)
    if not collection:
        flash('That collection does not exist!', 'warning')
        return redirect(url_for('collection.index'))
    token = Token.query.filter(
        Token.token_id == token_id,
        Token.collection_id == collection_id
    ).first()
    if not token:
        flash('That token does not exist for that collection!', 'warning')
        return redirect(url_for('collection.show', collection_id=collection_id))
    if current_user.is_anonymous:
        flash('Must be authenticated.', 'warning')
        return redirect(url_for('collection.index'))
    if not collection.user_can_access(current_user.id):
        flash('You are not allowed to access that collection.', 'warning')
        return redirect(url_for('collection.index'))
    if action == 'approve':
        token.rejected = False
        token.approved = True
        token.reject_reason = None
        db.session.commit()
        flash(f'Token was approved!', 'success')
    elif action == 'reject':
        if not request.args.get('reason'):
            flash('You need to specify a reason for rejection.', 'warning')
            return redirect(url_for('collection.show_token', collection_id=collection_id, token_id=token.token_id))
        token.rejected = True
        token.approved = False
        token.reject_reason = request.args.get('reason')
        db.session.commit()
        flash(f'Token was rejected!', 'error')
    else:
        flash('Unknown action.', 'warning')
    next = collection.get_tokens().first()
    return redirect(url_for('collection.show_token', collection_id=collection_id, token_id=next.token_id))
