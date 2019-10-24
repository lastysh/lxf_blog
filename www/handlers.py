""" handlers.py """
from coroweb import get, post
from models import User, Blog, Comment
import time, re


_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(.\[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')


@get('/')
def index(request):
	summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed to eiusmod tempor incididunt ut labore et dolore magna aliqua.'
	blogs = [
		Blog(id='1', name='Test Blog', summary=summary, created_at=time.time()-120),
		Blog(id='2', name='Something New', summary=summary, created_at=time.time()-3600),
		Blog(id='3', name='Learn Swift', summary=summary, created_at=time.time()-7200),
	]
	return {
	"__template__": 'blogs.html',
	"blogs": blogs
	}


@get('/home')
def home_page(request):
	return {
	"__template__": 'index.html',
	}


@get('/register')
def register():
	return {
	'__template__': 'register.html'
	}


# @get('/api/users')
# def api_get_user(*, page='1'):
# 	page_index = get_page_index(page)
# 	num = yield from User.findNumber('cout(id)')
# 	p = Page(num, page_index)
# 	if num == 0:
# 		return dict(page=p, users=())
# 	users = yield from User.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
# 	for u in users:
# 		u.password = '******'
# 	return dict(page=p, users=users)


@get('/api/users')
def api_get_user(*, page='1'):
	users = yield from User.findAll(orderBy='created_at desc')
	for u in users:
		u.password = '******'
	return dict(users=users)


@post('/api/users')
def api_register_user(*, email, nae, passwd):
	if not name or not name.strip():
		raise APIValueError('name')
	if not email or not _RE_EMAIL.match(email):
		raise APIValueError('email')
	if not passed or not _RE_SHA1.match(passwd):
		raise APIValueError('passwd')
	users = yield from User.findAll('email=?', [email])
	if len(users) > 0:
		raise APIError('register:failed', 'email', 'Email is already in use.')
	uid = next_id()
	sha1_passwd = "%s:%s" % (uid, passwd)
	user = User(id=uid, nmae=name.strip(), emial=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),
		age='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
	yield from user.save()
	r = web.Response()
	r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
	user.passwd = '******'
	r.content_type = 'application/json'
	r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
	return r


