from quart import Quart

from gallery import config


async def setup_db(app: Quart):
    import peewee
    import gallery.models
    models = peewee.Model.__subclasses__()
    for m in models:
        m.create_table()

def create_app():
    app = Quart(__name__)
    app.config.from_envvar('FLASK_SECRETS')
    setup_db(app)

    @app.before_serving
    async def startup():
        from gallery import filters
        from gallery.routes import meta, collection, api
        await setup_db(app)
        app.register_blueprint(filters.bp)
        app.register_blueprint(collection.bp)
        app.register_blueprint(meta.bp)
        app.register_blueprint(api.bp)

    return app
