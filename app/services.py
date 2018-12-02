# -*- coding: utf-8 -*-

from importlib import import_module
from datetime import datetime

import requests
import pusher
from lxml import etree

from app import config as config_module, ClassProperty

config = config_module.get_config()


class Service(object):
    _domain = None

    class InvalidDomain(Exception):
        pass

    @ClassProperty
    def domain(cls):
        if cls._domain is None:
            raise cls.InvalidDomain('You should use a specific service implementation')
        return import_module(cls._domain)


class HollydaysService(Service):
    _domain = 'app.domain'

    @classmethod
    def list_hollydays(cls):
        current_year = datetime.now().year
        hollydays = cls.domain.Hollyday.list_all()
        if len(hollydays) == 0:
            cls.domain.Hollyday.fill_for_year(current_year)
            hollydays = cls.domain.Hollyday.list_all()
        return hollydays

    @classmethod
    def get_hollydays_dates(cls, year):
        url = 'http://www.calendario.com.br/api/api_feriados.php?ano={}&estado=SP&cidade=PIRACICABA&token={}'.format(year, config.HOLLYDAY_TOKEN)
        response = requests.get(url)
        root = etree.fromstring(response.content)
        events = root.iter('event')
        result_dict = []
        for event_xml in events:
            event_dict = {'name': None, 'date': None, 'type_code': None}
            for props in list(event_xml):
                if props.tag in event_dict:
                    event_dict[props.tag] = props.text
            result_dict.append(event_dict)
        return result_dict


class Pusher(object):
    client = pusher.Pusher(
        app_id=config.PUSHER_APP_ID,
        key=config.PUSHER_KEY,
        secret=config.PUSHER_SECRET,
        cluster=config.PUSHER_CLUSTER,
        ssl=True
    )
    pusher_socket_id = None

    @classmethod
    def _send(cls, event, message, **data):
        if not data:
            data = {}
        data['message'] = message
        cls.client.trigger('base', event, cls._transform_key(data), cls.pusher_socket_id)

    @staticmethod
    def _snake_to_camel(name):
        result = []
        for index, part in enumerate(name.split('_')):
            if index == 0:
                result.append(part.lower())
            else:
                result.append(part.capitalize())
        return ''.join(result)

    @classmethod
    def _transform_key(cls, data):
        if isinstance(data, dict):
            return {cls._snake_to_camel(key): cls._transform_key(value) for key, value in data.items()}
        if isinstance(data, list):
            for index, item in enumerate(data):
                if isinstance(item, dict):
                    data[index] = {cls._snake_to_camel(key): cls._transform_key(value) for key, value in item.items()}
        return data

    @classmethod
    def send_sample(cls, **kwargs):
        cls._send('base.sample', **kwargs)
