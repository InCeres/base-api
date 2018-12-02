# -*- coding: utf-8 -*-
from sqlalchemy_utils.types import choice


class AppRepository(object):
    db = None


HOLLYDAY_TYPE = [
    ('N', 'National'),
    ('S', 'State'),
    ('M', 'Municipal'),
    ('O', 'Optional'),
]


class HollydayType(choice.ChoiceType):
    def __init__(self):
        super(HollydayType, self).__init__(HOLLYDAY_TYPE)

    def __repr__(self):
        return "HollydayType()"
