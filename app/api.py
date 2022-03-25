# -*- coding: utf-8 -*-

"""
This module define all the api endpoints
"""

from flask_restful import Api


def create_api(app):
    """
    Used when creating a Flask App to register the REST API and its resources
    """
    from app import resources
    api = Api(app)

    api.add_resource(resources.LoginResource, '/api/login')
    api.add_resource(resources.MeResource, '/api/me')
    api.add_resource(resources.MeHollyday, '/api/me/hollydays')

    api.add_resource(resources.HealthcheckResource,
                     '/api/healthcheck',
                     '/api/healthcheck/<string:service>')


def authenticate_api(token):
    from app import config
    return token == config.API_TOKEN
