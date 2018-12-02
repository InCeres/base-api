#  -*- coding: utf-8 -*-
"""
Config File for enviroment variables
"""

import os
from importlib import import_module

from dotenv import load_dotenv


class Config(object):
    """
    Base class for all config variables
    """
    DEBUG = False
    TESTING = False
    DEVELOPMENT = False
    CSRF_ENABLED = True
    AMBIENTE = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    def __init__(self):
        if self.AMBIENTE is None:
            raise TypeError('You should use one of the specialized config class')
        self.API_TOKEN = os.environ['API_TOKEN']
        self.SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
        self.SECRET_KEY = os.environ['SECRET_KEY']

        self.PUSHER_APP_ID = os.environ['PUSHER_APP_ID']
        self.PUSHER_KEY = os.environ['PUSHER_KEY']
        self.PUSHER_SECRET = os.environ['PUSHER_SECRET']
        self.PUSHER_CLUSTER = os.environ['PUSHER_CLUSTER']

        self.HOLLYDAY_TOKEN = os.environ['HOLLYDAY_TOKEN']

        self.ELASTIC_APM = {
            'SERVICE_NAME': 'base',
            'SECRET_TOKEN': os.environ['APM_SECRET_TOKEN'],
            'SERVER_URL': os.environ['APM_SERVER_URL'],
            'ENVIRONMENT': self.AMBIENTE,
            'DEBUG': self.DEBUG,
            'CAPTURE_BODY': 'errors'
        }


class ProductionConfig(Config):
    """
    Production Config... this is the real thing
    """
    AMBIENTE = 'production'


class StagingConfig(Config):
    """
    Staging Config is for... staging things
    """
    AMBIENTE = 'staging'
    DEBUG = False


class DevelopmentConfig(Config):
    """
    Development Config... this is your home developer!
    """
    AMBIENTE = 'development'
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ECHO = True


class SandboxConfig(Config):
    """
    Development Config... this is your home developer!
    """
    AMBIENTE = 'sandbox'
    DEBUG = True
    SQLALCHEMY_RECORD_QUERIES = True


class TestingConfig(DevelopmentConfig):
    """
    Test Config... You should be testing right now instead reading docs!!!
    """
    AMBIENTE = 'test'
    TESTING = True
    KEY_ON_TEST = 'KEY ON TEST'


class ConfigClassNotFound(Exception):
    """
    Raises when the APP_SETTINGS environment variable have a value which does not point to an uninstantiable class.
    """
    pass


def get_config():
    """
    Get the Config Class instance defined in APP_SETTINGS environment variable
    :return The config class instance
    :rtype: Config
    """
    app_settings = os.environ.get('APP_SETTINGS', 'app.config.DevelopmentConfig')
    if app_settings == 'app.config.DevelopmentConfig':
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
        if not os.path.exists(env_path):
            raise ValueError('Could not find a .env file in project root. Did you miss this step in project install doc?')
        load_dotenv(verbose=True, dotenv_path=env_path)

    config_imports = app_settings.split('.')
    config_class_name = config_imports[-1]
    config_module = import_module('.'.join(config_imports[:-1]))
    config_class = getattr(config_module, config_class_name, None)
    if not config_class:
        raise ConfigClassNotFound('Unable to find a config class in {}'.format(app_settings))
    return config_class()
