import pytest
from aiohttp import web


async def previous(request):
    if request.method == 'POST':
        request.app['value'] = (await request.post())['value']
        return web.json_response({'message': 'post data'})
    return web.json_response({'value': request.app['value']})


@pytest.fixture
def cli(loop, aiohttp_client):
    app = web.Application()
    app.router.add_get('/', previous)
    app.router.add_post('/', previous)
    return loop.run_until_complete(aiohttp_client(app))


async def test_post(cli):
    resp = await cli.post('/', data={'value': 'post data'})
    assert resp.status == 200
    assert await resp.json() == {"message": "post data"}
    assert cli.server.app['value'] == 'post data'


async def test_get(cli):
    cli.server.app['value'] = 'index'
    resp = await cli.get('/')
    assert resp.status == 200
    assert await resp.json() == {"value": "index"}


