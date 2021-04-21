import logging
import logging.config

from aiohttp import web
from aiohttp_apispec import setup_aiohttp_apispec, validation_middleware

import db
from handlers import Web
from settings import config


def main():

    app = web.Application()

    app['config'] = config

    app.on_startup.append(db.init_pg)
    app.on_cleanup.append(db.close_pg)

    logging.basicConfig(level=config['logger_level'])

    web_handlers = Web()
    web_handlers.configure(app)

    setup_aiohttp_apispec(app, title="My App", swagger_path="/docs")
    app.middlewares.append(validation_middleware)

    web.run_app(app)


if __name__ == '__main__':
    main()
