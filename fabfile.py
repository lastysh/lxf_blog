import os, re
from datetime import datetime

from fabric.api import *

env.user = 'root'

env.sudo_user = 'root'

env.hosts = ['192.168.10.129']

db_user = 'www-data'
db_password = 'www-data'


_TAR_FILE = 'dist-awesome.tar.gz'

def build():
	includes = ['static', 'templates', 'transwarp', 'favicon.ico', '*.py']
	excludes = ['test', '.*', '*.pyc', '*.pyo']
	# local('rm -f dist/%s' % _TAR_FILE)
	local(r'del /F "dist\%s"' % _TAR_FILE)
	with lcd(os.path.join(os.path.abspath('.'), 'www')):
		# cmd = ['tar', '--dereference', '-czvf', '../dist/%s' % _TAR_FILE]
		cmd = ['tar', '-czvf', '../dist/%s' % _TAR_FILE]
		# cmd.extend(['--exclude=\'%s\'' % ex for ex in excludes])
		cmd.extend(includes)
		local(' '.join(cmd))

_REMOTE_TMP_TAR = '/tmp/%s' % _TAR_FILE
_REMOTE_BASE_DIR = '/srv/awesome'


def deploy():
	newdir = 'www-%s' % datetime.now().strftime('%y-%m-%d_%H.%M.%S')
	run('rm -f %s' % _REMOTE_TMP_TAR)
	put('dist/%s' % _TAR_FILE, _REMOTE_TMP_TAR)
	with cd(_REMOTE_BASE_DIR):
		sudo('mkdir %s' % newdir)

	with cd('%s/%s' % (_REMOTE_BASE_DIR, newdir)):
		sudo('tar -xzvf %s' % _REMOTE_TMP_TAR)

	with cd(_REMOTE_BASE_DIR):
		sudo('rm -f www')
		sudo('ln -s %s www' % newdir)
		sudo('chown www-data:www-data www')
		sudo('chown -R www-data:www-data %s' % newdir)
		sudo('chmod +x www/app.py')
		sudo('sed -i "s/\r//g" `grep \r -rl www`')

	with settings(warn_only=True):
		sudo('supervisorctl stop awesome')
		sudo('supervisorctl start awesome')
		sudo('/etc/init.d/nginx reload')