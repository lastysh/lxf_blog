""" handlers.py """
from coroweb import get, post
from models import User

@get('/')
def index(request):
	users = yield from User.findAll()
	return {
	"__template__": 'test.html',
	"users": users,
	}

@get('/a')
def a(request):
	return {
	"__template__": 'a.html',
	}

@get('/b')
def b(request):
	return {
	"__template__": 'b.html',
	}