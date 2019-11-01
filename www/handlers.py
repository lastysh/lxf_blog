""" handlers.py """
from coroweb import get, post
from models import User, Blog, Comment, next_id
import time, re, asyncio, logging
from config import configs
from apis import APIError, APIValueError, APIResourceNotFoundError, APIPermissionError, Page
import hashlib, json
from aiohttp import web


COOKIE_NAME = 'awesession'
_COOKIE_KEY = configs.session.secret
_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')


def check_admin(request):
	if request.__user__ is None or not request.__user__.admin:
		raise APIPermissionError()


def get_page_index(page_str):
	p = 1
	try:
		p = int(page_str)
	except ValueError as e:
		pass
	if p < 1:
		p = 1
	return p


def user2cookie(user, max_age):
	"""
	Generate cookie str by user.
	"""
	expires = str(int(time.time() + max_age))
	s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
	L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
	return '-'.join(L)


def text2html(text):
	lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
	return ''.join(lines)


@asyncio.coroutine
def cookie2user(cookie_str):
	'''
	Parse cookie and load user if cookie is valid.
	'''
	if not cookie_str:
		return None
	try:
		L = cookie_str.split('-')
		if len(L) != 3:
			return None
		uid, expires, sha1 = L
		if int(expires) < time.time():
			return None
		user = yield from User.find(uid)
		if user is None:
			return None
		s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
		if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
			logging.info('invalid sha1')
			return None
		user.passwd = '******'
		return user
	except Exception as e:
		logging.exception(e)
		return None


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
	"blogs": blogs,
	'__user__': request.__user__
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


#=============================== test url request function by liuchaoming 2019/10/24====================
@post('/register_complete')
def r_complete(request):
	# logging.info("<<<<<<<>>>>>>>")
	return request
#=============================== test end===============================================================


@get('/signin')
def signin(request):
	return {
	'__template__': 'signin.html',
	}


@post('/api/authenticate')
def authenticate(*, email, passwd):
	if not email:
		raise APIValueError('email', 'Invalid email.')
	if not passwd:
		raise APIValueError('passwd', 'Invalid password.')
	users = yield from User.findAll('email=?', [email])
	if len(users) == 0:
		raise APIValueError('email', 'Email not exist.')
	user = users[0]
	sha1 = hashlib.sha1()
	sha1.update(user.id.encode('utf-8'))
	sha1.update(b':')
	sha1.update(passwd.encode('utf-8'))
## ===================================== check point ==================================
	# logging.info(user.id+'<<<< login >>>>'+user.passwd)
	# logging.info("current " + passwd)
	# logging.info(sha1.hexdigest())
## ===================================== end check ====================================
	if user.passwd != sha1.hexdigest():
		raise APIValueError('passwd', 'Invalid password.')
	r = web.Response()
	r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
	user.passwd = '******'
	r.content_type = 'application/json'
	r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
	return r


@get('/signout')
def signout(request):
	referer = request.headers.get('Referer')
	r = web.HTTPFound(referer or '/')
	r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
	logging.info('user signed out.')
	return r


@get('/manage/blogs/create')
def manage_create_blog():
	return {
	'__template__': 'manage_blog_edit.html',
	'id': '',
	'action': '/api/blogs'
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
def api_register_user(*, email, name, passwd):
	if not name or not name.strip():
		raise APIValueError('name')
	if not email or not _RE_EMAIL.match(email):
		raise APIValueError('email')
	if not passwd or not _RE_SHA1.match(passwd):
		raise APIValueError('passwd')
	users = yield from User.findAll('email=?', [email])
	if len(users) > 0:
		raise APIError('register:failed', 'email', 'Email is already in use.')
	uid = next_id()
	sha1_passwd = "%s:%s" % (uid, passwd)
## =============================  check piont ====================================================
	# logging.info("save"+"<<<register>>>"+sha1_passwd)
	# logging.info(hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest())
## =============================  end check ======================================================
	user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),
		image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
	yield from user.save()
	r = web.Response()
	r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
	user.passwd = '******'
	r.content_type = 'application/json'
	r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
	return r


@get('/api/blogs/{id}')
def api_get_blog(*, id):
	blog = yield from Blog.find(id)
	return blog


@post('/api/blogs')
def api_create_blog(request, *, name, summary, content):
	check_admin(request)
	if not name or not name.strip():
		raise APIValueError('name', 'name cannot be empty.')
	if not summary or not summary.strip():
		raise APIValueError('summary', 'summary cannot be empty.')
	if not content or not content.strip():
		raise APIValueError('content', 'content cannot be empty.')
	blog = Blog(user_id=request.__user__.id, user_name=request.__user__.name, user_image=request.__user__.image, name=name.strip(),
		summary=summary.strip(), content=content.strip())
	yield from blog.save()
	return blog


@get('/api/blogs')
def api_blogs(*, page='1'):
	page_index = get_page_index(page)
	num = yield from Blog.findNumber('count(id)')
	p = Page(num, page_index)
	if num == 0:
		return dict(page=p, blogs=())
	blogs = yield from Blog.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
	return dict(page=p, blogs=blogs)


@get('/manage/blogs')
def manage_blogs(*, page='1'):
	return {
	'__template__': 'manage_blogs.html',
	'page_index': get_age_index(page)
	}