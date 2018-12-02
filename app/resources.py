# -*- coding: utf-8 -*-

from functools import wraps
import re

from flask import request, g, Response
from flask_restful import Resource

from app import config as config_module, domain, apm

config = config_module.get_config()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        authenticated = getattr(g, 'authenticated', False)
        if not authenticated:
            return Response('{"result": "Not Authorized"}', 401, content_type='application/json')
        return f(*args, **kwargs)
    return decorated_function


def not_allowed(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return Response('{"result": "Method not allowed"}', 405, content_type='application/json')
    return decorated_function


class ResourceBase(Resource):
    http_methods_allowed = ['GET', 'POST', 'PUT', 'DELETE']
    entity_key = None
    resource_key = None
    list_compact = True

    def __init__(self):
        self.me = getattr(g, 'user_entity', None)
        if self.me is None and self.logged_user is not None:
            self.me = domain.User.create_with_logged(self.logged_user)
        if self.me is not None:
            self.me.entity_key = self.entity_key
            self.me.resource_key = self.resource_key
            self.me.set_pusher_key(request.headers.get('PUSHER-SOCKET-ID'))

    @staticmethod
    def camel_to_snake(name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    @staticmethod
    def snake_to_camel(name):
        result = []
        for index, part in enumerate(name.split('_')):
            if index == 0:
                result.append(part.lower())
            else:
                result.append(part.capitalize())
        return ''.join(result)

    def transform_key(self, data, method):
        if isinstance(data, dict):
            return {method(key): self.transform_key(value, method) for key, value in data.items()}
        if isinstance(data, list):
            for index, item in enumerate(data):
                if isinstance(item, dict):
                    data[index] = {method(key): self.transform_key(value, method) for key, value in item.items()}
        return data

    @property
    def payload(self):
        payload = {}
        if request.json:
            payload.update(self.transform_key(request.json, self.camel_to_snake))
        if request.form:
            payload.update(self.transform_key(request.form, self.camel_to_snake))
        if request.args:
            payload.update(self.transform_key(request.args, self.camel_to_snake))
        if request.files:
            payload['attachment'] = request.files
        return payload

    @property
    def cookies(self):
        username = request.cookies.get('baseUserName', None)
        token = request.cookies.get('baseUserToken', 'null')
        return {'baseUserName': username, 'baseUserToken': token}

    @property
    def headers(self):
        return request.headers

    @property
    def logged_user(self):
        return getattr(g, 'user', None)

    def return_not_allowed(self):
        return self.response({'result': 'Method not allowed'}), 405

    def return_unexpected_error(self, ex):
        return self.response({'result': 'error', 'exception': str(ex)}), 500

    def response(self, data_dict):
        return self.transform_key(data_dict, self.snake_to_camel)

    def get_list(self, **kwargs):
        try:
            entity_list = self.me.get_list(self.payload, **kwargs)
            return [self.response(entity.as_dict(compact=self.list_compact)) for entity in entity_list]
        except Exception as ex:
            apm.monitor.capture_exception(exc_info=True)
            return self.return_unexpected_error(ex)

    def get_item(self, **kwargs):
        try:
            return self.response(self.me.get_item(**kwargs).as_dict())
        except self.me.EntityNotExist:
            apm.monitor.capture_exception(exc_info=True)
            return "Item doesn't exist", 404
        except Exception as ex:
            apm.monitor.capture_exception(exc_info=True)
            return self.return_unexpected_error(ex)

    @login_required
    def get(self, **kwargs):
        if 'GET' not in self.http_methods_allowed:
            return self.return_not_allowed()
        if kwargs.get('{}_id'.format(self.entity_key)) is None:
            return self.get_list(**kwargs)
        else:
            return self.get_item(**kwargs)

    @login_required
    def post(self, **kwargs):
        if 'POST' not in self.http_methods_allowed:
            return self.return_not_allowed()
        try:
            created = self.me.create_new_entity(self.payload, **kwargs)
            return self.response(created.as_dict()), 201
        except self.me.InvalidEntityData as ex:
            apm.monitor.capture_exception(exc_info=True)
            return self.response({'erro': 'Invalid data.', 'internal_code': ex.message}), 400
        except self.me.EntityAlreadyExist as ex:
            apm.monitor.capture_exception(exc_info=True)
            return {'erro': 'already-exist', 'exception': ex.message}, 400
        except Exception as ex:
            apm.monitor.capture_exception(exc_info=True)
            return self.return_unexpected_error(ex)

    def __extract_file_attached(self):
        try:
            if 'attachment' in self.payload:
                what_i_need = ['creator_id', 'created_at', 'file_attached']
                attachments_results = []
                for attachment in self.payload['attachment'].itervalues():
                    key = attachment.name.replace('[file]', '')
                    attachment_result = {}
                    for props in what_i_need:
                        attachment_result[props] = self.payload['{}[{}]'.format(key, props)]
                    attachment_result['file'] = {'name': attachment.filename, 'stream': attachment.stream}
                    attachments_results.append(attachment_result)
                return attachments_results
        except Exception as ex:
            pass
        return None

    @login_required
    def put(self, **kwargs):
        if 'PUT' not in self.http_methods_allowed:
            return self.return_not_allowed()
        try:
            payload = self.payload
            file_attached = self.__extract_file_attached()
            if file_attached is not None:
                payload = {
                    'uploading': True,
                    'file_attached': file_attached
                }
            updated = self.me.update(payload, **kwargs)
            if updated:
                return self.response(updated.as_dict()), 200
            return self.response({'result': 'ERROR'}), 500
        except self.me.InvalidEntityData as ex:
            apm.monitor.capture_exception(exc_info=True)
            return self.response({'erro': 'Invalid data.', 'internal_code': ex.message}), 400
        except self.me.EntityAlreadyExist as ex:
            apm.monitor.capture_exception(exc_info=True)
            return {'erro': 'already-exist', 'exception': ex.message}, 400
        except Exception as ex:
            apm.monitor.capture_exception(exc_info=True)
            return self.return_unexpected_error(ex)

    @login_required
    def delete(self, **kwargs):
        if 'DELETE' not in self.http_methods_allowed:
            return self.return_not_allowed()
        try:
            self.me.delete(**kwargs)
            return {'resultado': 'OK'}, 204
        except self.me.CouldNotDelete as ex:
            apm.monitor.capture_exception(exc_info=True)
            return self.response({'erro': 'Could not Delete', 'internal_code': ex.message}), 400
        except self.me.WhoDaHellYouThinkYouAre as ex:
            apm.monitor.capture_exception(exc_info=True)
            return self.response({'erro': 'Could not Delete', 'internal_code': 'its_not_yours'}), 400
        except Exception as ex:
            apm.monitor.capture_exception(exc_info=True)
            return self.return_unexpected_error(ex)


class LoginResource(ResourceBase):
    http_methods_allowed = ['POST']
    entity = domain.User

    def post(self):
        try:
            user = self.entity.create_for_login(self.payload)
            if user.is_correct:
                g.user = user.as_dict()
                g.current_token = user.generate_auth_token()
                return {'logged': True}, 200
        except Exception:
            apm.monitor.capture_exception(exc_info=True)
            return {'result': 'Not Authorized'}, 401
        return {'result': 'Not Authorized'}, 401


class MeResource(ResourceBase):
    http_methods_allowed = ['GET', 'PUT']

    @login_required
    def get(self):
        try:
            return self.response(self.me.as_dict())
        except Exception as ex:
            apm.monitor.capture_exception(exc_info=True)
            return self.return_unexpected_error(ex)

    @login_required
    def put(self):
        try:
            self.me.update_me(self.payload)
            return self.response({'result': 'OK'})
        except Exception as ex:
            apm.monitor.capture_exception(exc_info=True)
            return self.return_unexpected_error(ex)


class MeHollyday(ResourceBase):
    http_methods_allowed = ['GET']
    entity_key = 'hollyday'
    resource_key = 'hollyday'


class HealthcheckResource(Resource):
    def get(self, service=None):
        from app import models
        if service is None:
            return {"result": "OK"}, 200
        else:
            if service == 'database':
                try:
                    models.User.get(1)
                    return {"result": "OK"}, 200
                except:
                    return {"result": "NOT"}, 200
