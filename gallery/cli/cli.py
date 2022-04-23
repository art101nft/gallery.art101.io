import click
from flask import Blueprint

from gallery.factory import db
from gallery.models import Collection
from gallery import config


bp = Blueprint('cli', 'cli', cli_group=None)


@bp.cli.command('init')
def init():
    db.create_all()

@bp.cli.command('list')
def list():
    """
    List collections
    """
    collections = Collection.query.filter().order_by(Collection.create_date.desc())
    for c in collections:
        click.echo(f'{c.id} - {c.title} - {c.user.public_address} - {c.secret_token}')
