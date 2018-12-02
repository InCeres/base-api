# -*- coding: utf-8 -*-
import os
from datetime import timedelta, datetime

import jwt
from passlib.apps import custom_app_context

from app import config as config_module, apm
from app import models, services

config = config_module.get_config()


class Entity(object):
    repository = None

    class AlreadyExist(Exception):
        pass

    class NotExist(Exception):
        pass

    @classmethod
    def list_all(cls):
        return [cls.create_with_instance(instance) for instance in cls.repository.list_all()]

    @classmethod
    def create_new(cls, json_data):
        try:
            return cls(cls.repository.create_from_json(json_data))
        except cls.repository.RepositoryError as ex:
            if 'already exists' in ex.message.lower:
                raise cls.AlreadyExist('Entity with {} already exists in repository'.format(json_data))

    @classmethod
    def create_with_id(cls, entity_id):
        instance = cls.repository.get(entity_id)
        return cls.create_with_instance(instance)

    @classmethod
    def create_with_instance(cls, instance):
        if instance is None:
            raise cls.NotExist('Tryed to create entity with instance None. Check the stack trace to see the origin')
        return cls(instance)

    def __init__(self, instance):
        self.instance = instance
        self.id = instance.id

    @property
    def name(self):
        return self.instance.name

    def save(self):
        self.instance.save_db()

    @staticmethod
    def remove_unused_json_data_key(key, json_data):
        if key in json_data:
            del json_data[key]

    def update_me(self, json_data):
        self.instance.update_from_json(json_data)

    def as_dict(self, compact=False):
        return {
            'id': self.id,
            'name': self.name
        }


class User(Entity):
    repository = models.User

    class InvalidEntityData(Exception):
        pass

    class EntityNotExist(Exception):
        pass

    class EntityAlreadyExist(Exception):
        pass

    class CouldNotDelete(Exception):
        pass

    class WhoDaHellYouThinkYouAre(Exception):
        pass

    @classmethod
    def create_with_token(cls, token):
        try:
            data = jwt.decode(token, config.SECRET_KEY)
        except Exception as ex:
            return None
        if not data.get('id', None):
            return None
        return cls.create_with_id(data['id'])

    @classmethod
    def create_with_logged(cls, logged_user):
        return cls.create_with_email(logged_user['email'])

    @classmethod
    def create_for_login(cls, login_data):
        user = cls.create_with_email(login_data['username'])
        user.temp_password = login_data['password']
        return user

    @classmethod
    def create_with_email(cls, email):
        instance = cls.repository.get_by_email(email)
        return cls.create_with_instance(instance)

    @classmethod
    def create_new(cls, json_data):
        password = json_data.pop('password')
        instance = super(User, cls).create_new(json_data)
        instance.password_hash = custom_app_context.encrypt(password)

    def __init__(self, instance):
        super(User, self).__init__(instance)
        self.temp_password = None
        self.entity_key = None
        self.resource_key = None
        self.__kanbans = None
        self.__sprints = None
        self.__planned_sprints = None
        self.__teams = None
        self.__modules = None

    @property
    def email(self):
        return self.instance.email

    @property
    def is_manager(self):
        return self.instance.is_manager

    @property
    def password_hash(self):
        return self.instance.password_hash

    @property
    def is_correct(self):
        return custom_app_context.verify(self.temp_password, self.password_hash)

    def set_pusher_key(self, pusher_socket_id):
        services.Pusher.pusher_socket_id = pusher_socket_id

    def as_dict(self, compact=False):
        as_dict = super(User, self).as_dict()
        as_dict['email'] = self.email
        if compact:
            return as_dict

        as_dict.update({
            'is_manager': self.is_manager
        })
        return as_dict

    def generate_auth_token(self, expiration=600):
        return jwt.encode({'id': self.id, 'exp': datetime.utcnow() + timedelta(minutes=expiration)}, config.SECRET_KEY, algorithm='HS256')

    def get_item(self, **kwargs):
        return None

    def get_list(self, payload, **kwargs):
        return []
