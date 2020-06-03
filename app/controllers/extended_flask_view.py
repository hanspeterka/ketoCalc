import inspect
import re

from flask_classful import FlaskView

from flask import render_template as template

from app.models import *  # noqa: F401, F403, F406
from app.controllers.forms import *  # noqa: F401, F403, F406


class ExtendedFlaskView(FlaskView):
    """docstring for ExtendedFlaskView"""

    def before_request(self, name, id=None, *args, **kwargs):
        model_name = type(self).__name__.replace("sView", "")
        # form_name = model_name + "sForm"
        snake_model_name = re.sub("(?!^)([A-Z]+)", r"_\1", model_name).lower()

        # e.g. User
        # model_name = model_name
        # e.g. user
        attribute_name = snake_model_name

        # e.g. class <User>
        try:
            model_klass = globals()[model_name]
        except KeyError:
            model_klass = None
        # e.g. class <UsersForm>
        # try:
        #     form_klass = globals()[form_name]
        # except KeyError:
        #     form_klass = None

        if id is not None and model_klass is not None:
            instance = model_klass().load(id)
            # e.g. self.user, or None
            setattr(self, attribute_name, instance)
        else:
            setattr(self, attribute_name, None)

    def template(self, template_name=None, **kwargs):
        # Template name is given from view and method names if not provided
        calling_method = inspect.stack()[1].function
        if template_name is None:
            template_name = (
                self._get_attribute_name() + "s/" + calling_method + ".html.j2"
            )

        # All public variables of the view are passed to template
        view_attributes = self.__dict__
        public_attributes = {
            k: view_attributes[k] for k in view_attributes if not k.startswith("_")
        }

        # kwargs has higher priority, therefore rewrites public attributes
        merged_values = {**public_attributes, **kwargs}

        return template(template_name, **merged_values)

    def _get_attribute_name(self):
        model_name = type(self).__name__.replace("sView", "")
        snake_model_name = re.sub("(?!^)([A-Z]+)", r"_\1", model_name).lower()
        attribute_name = snake_model_name
        return attribute_name