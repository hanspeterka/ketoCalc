from flask import current_app as application

from flask_login import current_user

from sqlalchemy.exc import DatabaseError

from sqlalchemy.ext.hybrid import hybrid_property

from app import db


# Custom methods for all my classes
class BaseMixin(object):
    def __init__(self, **kwargs):
        for kwarg in kwargs:
            setattr(self, kwarg.key, kwarg.value)

    # LOADING

    @classmethod
    def load(cls, *args, **kwargs):
        object_id = kwargs.get("id", args[0])
        return db.session.query(cls).filter(cls.id == object_id).first()

    @classmethod
    def load_all(cls):
        return db.session.query(cls).all()

    @classmethod
    def load_last(cls):
        return db.session.query(cls).all()[-1]

    @classmethod
    def load_by_name(cls, name):
        return db.session.query(cls).filter(cls.name == name).first()

    @classmethod
    def load_by_attribute(cls, attribute, value):
        if not hasattr(cls, attribute):
            raise AttributeError

        return db.session.query(cls).filter(getattr(cls, attribute) == value).first()

    # DATABASE OPERATIONS

    def edit(self, **kw):
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            application.logger.error("Edit error: {}".format(e))
            return False

    def save(self, **kw):
        """Saves (new) object
        """
        try:
            db.session.add(self)
            db.session.commit()
            return self.id is not None
        except DatabaseError as e:
            db.session.rollback()
            application.logger.error("Save error: {}".format(e))
            return False

    def remove(self, **kw):
        """Deletes object
        """
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except DatabaseError as e:
            db.session.rollback()
            application.logger.error("Remove error: {}".format(e))
            return False

    def expire(self, **kw):
        """Dumps database changes
        """
        try:
            db.session.expire(self)
            return True
        except Exception as e:
            db.session.rollback()
            application.logger.error("Expire error: {}".format(e))
            return False

    def refresh(self, **kw):
        try:
            db.session.refresh(self)
            return True
        except Exception as e:
            db.session.rollback()
            application.logger.error("Refresh error: {}".format(e))
            return False

    # OTHER METHODS

    def is_author(self, user) -> bool:
        if hasattr(self, "author"):
            return self.author == user
        else:
            return False
            # raise AttributeError("No 'author' attribute.")

    # PROPERTIES

    @hybrid_property
    def public(self) -> bool:
        """alias for is_shared"""
        if hasattr(self, "is_shared"):
            return self.is_shared
        else:
            return False
            # raise AttributeError("No 'is_shared' attribute.")

    @hybrid_property
    def is_public(self):
        return self.public

    # PERMISSIONS

    def can_view(self, user) -> bool:
        return self.is_author(user) or user.is_admin or self.is_public

    @property
    def can_current_user_view(self) -> bool:
        return self.can_view(user=current_user)

    def can_edit(self, user) -> bool:
        return self.is_author(user) or user.is_admin

    @property
    def can_current_user_edit(self) -> bool:
        return self.can_edit(user=current_user)
