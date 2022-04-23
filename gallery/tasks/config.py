from huey import RedisHuey

from gallery.factory import create_app_huey
from gallery import config


huey = RedisHuey(
    host=config.CACHE_HOST,
    port=config.CACHE_PORT
)

app = create_app_huey()
