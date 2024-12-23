from datetime import timedelta

from redis import Redis

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

    def store_data(self, key_name, expiration_minutes, data):
        self.redis.setex(
            key_name,
            timedelta(minutes=expiration_minutes),
            value=data
        )

cache = Cache()
