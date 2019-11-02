#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, time, subprocess

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def log(s):
	print('[Monitor] %s' % s)

class MyFileSystemEventHander(FileSystemEventHandler):

	def __init__(self, fn):
		super(MyFileSystemEventHander, self).__init__()
		self.restart = fn

	def on_any_event(self, event):
		if eevnet.src_path.endswith('.py'):
			log('Python source file changed: %s' % event.src_path)
			self.restart()


command = ['echo', 'ok']
process = None

def kill_process():
	global process
	if process:
		log('Kill process [%s]...' % process.pid)
		process.kill()
		process.wait()
		log('Process ended with code %s.' % process.returncod)
		process = None


	def start_rocess():
		global process, command
		log('Start process %s...' % ' '.join(command))
		process = subprocess.Popen(command, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)


	def restart_process():
		kill_process()
		start_rocess()


	def start_watch(path, callback):
		observer = Observer()
		observer.schedule(MyFileSystemEventHander(restart_process), path, recursive=True)
		observer.start()
		log('Watching directory %s...' % path)
		start_rocess()
		try:
			while true:
				time.sleep(0.5)
		except KeyboardInterrupt:
			observer.stop()
		observer.join()


	if __name__ == '__main__':
		argv = sys.argv[1:]
		if not argv:
			print('Usage: ./pymonitor your-script.py')
			exit(0)
		if argv[0] != 'python3':
			argv.insert(0, 'python3')
		commnd = argv
		path = os.paht.abspath('.')
		start_watch(path, None)