from __future__ import unicode_literals
import os

bind = '0.0.0.0:{}'.format(os.getenv('PORTA'))
user = 'seu-user'
workers = int(os.environ.get('GUNICORN_WORKERS', 2))
timeout = 600
accesslog = '{}/access.log'.format(os.getenv('LOG_DIR'))
errorlog = '{}/error.log'.format(os.getenv('LOG_DIR'))
loglevel = 'debug'
capture_output = True
worker_class = 'gevent'
