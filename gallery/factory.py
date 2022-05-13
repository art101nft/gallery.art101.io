from quart import Quart, flask_patch

from gallery import config


def create_app_huey():
    _app = Quart(__name__)
    return _app


def create_app():
    app = Quart(__name__)
    app.config.from_envvar('FLASK_SECRETS')

    @app.before_serving
    async def startup():
        from gallery import filters
        from gallery.routes import meta, collection, api
        app.register_blueprint(filters.bp)
        app.register_blueprint(collection.bp)
        app.register_blueprint(meta.bp)
        app.register_blueprint(api.bp)

    return app
