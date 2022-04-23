import os
import requests
from time import sleep

from gallery.tasks.config import huey, app
from gallery.models import Collection, Token
from gallery.helpers import retrieve_token_metadata
from gallery.factory import db
from gallery import config


@huey.task()
def fetch_collection_metadata(collection_id: int):
    with app.app_context():
        collection = Collection.query.get(collection_id)
        if collection:
            print(f'[+] Updating collection {collection_id}')
            _f = collection.get_metadata_folder()
            print(_f)
            if not os.path.exists(_f):
                os.makedirs(_f)
                print(f'[.] created folder {_f}')
            for i in range(collection.start_token_id, collection.end_token_id + 1):
                token = Token.query.filter(
                    Token.token_id == i,
                    Token.collection_id == collection.id
                ).first()
                if not token:
                    print(f'[+] adding database item for collection {collection} token {i}')
                    token = Token(
                        collection_id=collection_id,
                        token_id=i
                    )
                    db.session.add(token)
                    db.session.commit()

                print(f'[.] Scheduling retrieval of token metadata for token #{token.token_id} (db token {token.id}) of collection #{token.collection.id}')
                _retrieve_token_metadata(token.id)


@huey.task()
def _retrieve_token_metadata(token_id: int):
    with app.app_context():
        token = Token.query.get(token_id)
        if token and not token.metadata_exists():
            retrieve_token_metadata(token_id)


# @huey.periodic_task(crontab(minute='30', hour='*/2'))
# def fetch_missed():
#     with app.app_context():
#         pass
