from huey import crontab

from gallery.tasks.config import huey, app
from gallery.library.cache import cache


@huey.periodic_task(crontab(minute='30', hour='*/2'))
def do_thing():
    with app.app_context():
        pass
