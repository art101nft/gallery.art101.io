from logging.config import dictConfig

import quart.flask_patch
from quart import Quart

from gallery import config


def create_app_huey():
    _app = Quart(__name__)
    # dictConfig(config.LOGGING_CONFIG)
    return _app

def create_app():
    app = Quart(__name__)
    app.config.from_envvar('FLASK_SECRETS')

    @app.before_serving
    async def startup():
        from gallery import filters
        from gallery.routes import meta, collection, api
        from gallery.cli import cli
        app.register_blueprint(filters.bp)
        app.register_blueprint(collection.bp)
        app.register_blueprint(meta.bp)
        app.register_blueprint(api.bp)
        app.register_blueprint(cli.bp)

    return app
