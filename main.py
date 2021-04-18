import asyncio
import logging
import logging.config

from aiohttp import web
from aiohttp_apispec import setup_aiohttp_apispec, validation_middleware
from aiohttp_session import setup as setup_session
from aiohttp_session.redis_storage import RedisStorage
from aiohttp_security import setup as setup_security, CookiesIdentityPolicy
from aiopg.sa import create_engine
from aioredis import create_pool

from db_auth import DBAuthorizationPolicy
from handlers import Web
from settings import config


async def init(loop):
    redis_pool = await create_pool(('localhost', 6379))
    db_engine = await create_engine(user=config['postgres']['user'],
                                    password=config['postgres']['password'],
                                    database=config['postgres']['database'],
                                    host=config['postgres']['host'])

    app = web.Application()
    logging.basicConfig(level=config['logger_level'])
    app.db_engine = db_engine
    setup_session(app, RedisStorage(redis_pool))
    setup_security(app,
                   CookiesIdentityPolicy(),
                   DBAuthorizationPolicy(db_engine))

    web_handlers = Web()
    web_handlers.configure(app)

    setup_aiohttp_apispec(app, title="My App", swagger_path="/docs")
    app.middlewares.append(validation_middleware)

    runner = web.AppRunner(app)

    await runner.setup()

    srv = web.TCPSite(runner, 'localhost', 8080)
    await srv.start()
    print('Server started at http://127.0.0.1:8080')
    return srv, app, runner


async def finalize(srv, app, handler):
    sock = srv.sockets[0]
    app.loop.remove_reader(sock.fileno())
    sock.close()

    await handler.finish_connections(1.0)
    srv.close()
    await srv.wait_closed()
    await app.finish()


def main():
    loop = asyncio.get_event_loop()
    srv, app, handler = loop.run_until_complete(init(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete((finalize(srv, app, handler)))


if __name__ == '__main__':
    main()
