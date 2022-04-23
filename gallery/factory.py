from logging.config import dictConfig

from flask import Flask

from gallery import config


def create_app_huey():
    _app = Flask(__name__)
    # dictConfig(config.LOGGING_CONFIG)
    return _app

def create_app():
    app = Flask(__name__)
    app.config.from_envvar('FLASK_SECRETS')

    with app.app_context():
        from gallery import filters
        from gallery.routes import meta, collection
        app.register_blueprint(filters.bp)
        app.register_blueprint(collection.bp)
        app.register_blueprint(meta.bp)
        return app
