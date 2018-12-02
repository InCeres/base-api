# -*- coding: utf-8 -*-

from elasticapm.contrib import flask as flask_apm

monitor = None


def create_monitor(app):
    global monitor
    monitor = flask_apm.ElasticAPM(app)
