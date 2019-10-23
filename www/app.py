import logging; logging.basicConfig(level=logging.INFO)
import asyncio, os, json, time
from datetime import datetime

from aiohttp import web

def index(request):
	return web.Response(content_type='text/html', body=b'<h1>Awesome</h1>')

@asyncio.coroutine
def init(loop):
	app = web.Application(loop=loop)
	app.router.add_route('GET', '/', index)
	srv = yield from loop.create_server(app.make_handler(), '127.0.0.1', 9000)
	logging.info('server started at http://127.0.0.1:9000...')
	return srv

# loop = asyncio.get_event_loop()
# loop.run_until_complete(init(loop))
# loop.run_forever()

import orm
from models import User, Blog, Comment

def test(loop):
	yield from orm.create_pool(loop, user='www-data', password='www-data', db='awesome')
	# u = User(name='Test', email='test@example.com', passwd='1234567890', image='about:blank')
	# yield from u.save()
	u = User('users', 'name', 'Test')
	yield from u.remove()

# for x in test():
# 	pass


loop = asyncio.get_event_loop()
loop.run_until_complete(test(loop))
loop.close()
