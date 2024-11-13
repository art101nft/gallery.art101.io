import click
from quart import Blueprint

from gallery.collections import all_collections, Collection


bp = Blueprint('cli', 'cli', cli_group=None)


@bp.cli.command('refresh')
def refresh():
    collections = [Collection(k) for k in all_collections]
    for c in collections:
        click.echo(f'[+] Refreshing: {c.title} - {c.contract_address}')
        c._scan_tokens()
