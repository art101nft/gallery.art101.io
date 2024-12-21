from quart import Quart


def create_app():
    from gallery import filters
    from gallery.routes import meta, collection, api
    app = Quart(__name__)
    app.config.from_envvar('FLASK_SECRETS')

    @app.before_serving
    async def startup():
        app.register_blueprint(filters.bp)
        app.register_blueprint(collection.bp)
        app.register_blueprint(meta.bp)
        app.register_blueprint(api.bp)

    return app
