# -*- coding: utf-8 -*-

import os
from datetime import datetime, timedelta

from flask import Flask, g, request
from flask_sqlalchemy import SQLAlchemy

from app import config as config_module, api, database, auth, apm


config = config_module.get_config()

web_app = Flask(__name__)
web_app.config.from_object(config)

apm.create_monitor(web_app)

database.AppRepository.db = SQLAlchemy(web_app)

api.create_api(web_app)


@web_app.before_request
def before_request():
    token = request.cookies.get('baseUserToken', None)
    username = request.cookies.get('baseUserName')
    api_token = request.headers.get('API-TOKEN', None)
    authenticated = None
    user = None
    user_entity = None
    new_token = None
    if token and username:
        user, new_token, user_entity = auth.check_auth_token(token)
    elif api_token:
        authenticated = api.authenticate_api(api_token)
    if user and new_token:
        g.user = user
        g.current_token = new_token
        g.user_entity = user_entity
        authenticated = True
    g.authenticated = authenticated


@web_app.after_request
def add_cache_header(response):
    response.headers['Cache-Control'] = "no-cache, no-store, must-revalidate"
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@web_app.after_request
def add_token_header(response):
    user = g.get("user")
    if user is not None:
        token = g.current_token
        expire_date = datetime.now()
        expire_date = expire_date + timedelta(days=90)
        response.set_cookie('baseUserToken', token, domain='inceres.com.br', expires=expire_date)
        response.set_cookie('baseUserName', g.user['email'], domain='inceres.com.br', expires=expire_date)

    return response


def run():
    web_app.run(host='0.0.0.0', port=int(os.environ.get('PORTA', 33366)), debug=True)
