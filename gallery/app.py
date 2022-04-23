from logging.config import dictConfig

from gallery.factory import create_app
from gallery import config


app = create_app()

dictConfig(config.LOGGING_CONFIG)

if __name__ == '__main__':
    app.run()
