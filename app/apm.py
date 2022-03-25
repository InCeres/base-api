# -*- coding: utf-8 -*-

from elasticapm.contrib import flask as flask_apm

from app import config

monitor = None


class FakeAPM(object):
    def capture_message(self, *args, **kwargs):
        pass

    def capture_exception(self, *args, **kwargs):
        pass


def create_monitor(app):
    global monitor
    if config.FAKE_APM:
        monitor = FakeAPM()
    else:
        monitor = flask_apm.ElasticAPM(app)
