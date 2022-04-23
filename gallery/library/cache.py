from json import loads as json_loads
from json import dumps as json_dumps
from hexbytes import HexBytes
from datetime import timedelta

from redis import Redis
from flask import current_app

from gallery import config


class Cache(object):
    def __init__(self):
        self.redis = Redis(host=config.CACHE_HOST, port=config.CACHE_PORT)

    def get_data(self, key_name):
        data = self.redis.get(key_name)
        if data:
            return data
        else:
            return None

    def store_data(self, item_name, expiration_minutes, data):
        current_app.logger.info(f'SET - {item_name} - expires in {expiration_minutes} minutes')
        self.redis.setex(
            item_name,
            timedelta(minutes=expiration_minutes),
            value=data
        )

cache = Cache()
