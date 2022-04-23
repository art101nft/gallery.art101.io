import os
import requests
from time import sleep

from gallery.tasks.config import huey, app
from gallery.helpers import get_eth_contract


@huey.task()
def scan_tokens(contract_address, supply, start_at_0=False):
    with app.app_context():
        if start_at_0:
            r = range(supply-1, -1, -1)
        else:
            r = range(supply, 0, -1)
        print('scanning tokens with supply ' + supply)
        # for token_id in r:
        #     print(token_id)
        #     scan_token(token_id)


@huey.task()
def scan_token(token_id: int):
    with app.app_context():
        print(token_id)


# @huey.periodic_task(crontab(minute='30', hour='*/2'))
# def fetch_missed():
#     with app.app_context():
#         pass
