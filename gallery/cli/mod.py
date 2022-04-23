import click
from flask import Blueprint

from gallery.models import User
from gallery.factory import db


bp = Blueprint('mod', 'mod')


@bp.cli.command('list')
def list():
    """
    List current server moderators.
    """
    for mod in User.query.filter(User.moderator == True):
        click.echo(mod.user.public_address)


@bp.cli.command('add')
@click.argument('address')
def add(address):
    """
    Add server moderators by wallet address.
    """
    address = address.lower()
    user = User.query.filter(User.public_address == address).first()
    if user:
        user.moderator = True
        db.session.commit()
        click.echo(f'[+] Added moderator status to `{address}`')
    else:
        u = User(
            public_address=address,
            moderator=True
        )
        db.session.add(u)
        db.session.commit()
        click.echo('[+] Created new user as moderator.')


@bp.cli.command('remove')
@click.argument('address')
def remove(address):
    """
    Remove server moderator by wallet address.
    """
    address = address.lower()
    user = User.query.filter(User.public_address == address).first()
    if user:
        user.moderator = False
        db.session.commit()
        click.echo(f'[-] Removed moderator status from `{address}`')
    else:
        click.echo('[.] That is not a valid user.')
