# -*- coding: utf-8 -*-

from sqlalchemy import exc, text, or_, and_

from app import database, config as config_module, ClassProperty

config = config_module.get_config()
db = database.AppRepository.db


class AbstractModel(object):
    class NotExist(Exception):
        pass

    class RepositoryError(Exception):
        pass

    @classmethod
    def create_from_json(cls, json_data):
        try:
            instance = cls()
            instance.set_values(json_data)
            instance.save_db()
            return instance
        except exc.IntegrityError as ex:
            raise cls.RepositoryError(ex.message)

    @classmethod
    def list_with_filter(cls, **kwargs):
        return cls.query.filter_by(**kwargs).all()

    @classmethod
    def list_all(cls):
        return cls.query.all()

    @classmethod
    def get_with_filter(cls, **kwargs):
        return cls.query.filter_by(**kwargs).one_or_none()

    @classmethod
    def get(cls, item_id):
        item = cls.query.get(item_id)
        if not item:
            raise cls.NotExist
        else:
            return item

    @classmethod
    def rollback_db(cls):
        db.session.rollback()

    def save_db(self):
        db.session.add(self)
        db.session.flush()
        db.session.refresh(self)

    def delete_db(self):
        try:
            db.session.delete(self)
            db.session.flush()
        except exc.IntegrityError as ex:
            raise self.RepositoryError(ex.message)

    def update_from_json(self, json_data):
        try:
            self.set_values(json_data)
            self.save_db()
            return self
        except exc.IntegrityError as ex:
            raise self.RepositoryError(ex.message)

    def set_values(self, json_data):
        for key, value in json_data.iteritems():
            setattr(self, key, json_data.get(key, getattr(self, key)))


class User(db.Model, AbstractModel):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String)
    is_manager = db.Column(db.Boolean, default=False)

    @classmethod
    def get_by_email(cls, email):
        return cls.get_with_filter(email=email)


class Hollyday(db.Model, AbstractModel):
    __tablename__ = 'hollydays'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    date = db.Column(db.Date)
    type = db.Column(database.HollydayType(), nullable=False, default=u'N')
