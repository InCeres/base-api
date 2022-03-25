from __future__ import unicode_literals
import os

bind = '0.0.0.0:{}'.format(os.getenv('PORTA'))
user = 'seu-user'
workers = int(os.environ.get('GUNICORN_WORKERS', 2))
timeout = 600
if os.environ.get('IN_DOCKER', 'False') == 'False':
    accesslog = '{}/access.log'.format(os.environ['LOG_DIR'])
    errorlog = '{}/error.log'.format(os.environ['LOG_DIR'])
loglevel = 'debug'
capture_output = True
worker_class = 'gevent'
