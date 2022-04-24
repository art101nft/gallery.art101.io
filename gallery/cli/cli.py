import click
from flask import Blueprint

from gallery.collections import all_collections, Collection
from gallery import config


bp = Blueprint('cli', 'cli', cli_group=None)


@bp.cli.command('init')
def init():
    db.create_all()

@bp.cli.command('refresh')
def refresh():
    collections = [Collection(k, v) for k, v in all_collections.items()]
    for c in collections:
        click.echo(f'[+] Refreshing: {c.title} - {c.contract_address}')
        c._scan_tokens()
