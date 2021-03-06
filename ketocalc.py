import os
import re
import time

import datetime

from flask import request, redirect, session, url_for
from flask import g

from flask_login import current_user

from app import create_app
from app import db

# from app.models import db
# from app.models.users import User
from app.models.request_log import RequestLog

from app.data import template_data

from app.handlers.data import DataHandler


env = os.environ.get("FLASK_ENV", "default")
application = create_app(config_name=env)


@application.context_processor
def inject_globals():
    return dict(
        icons=template_data.icons,
        social_icons=template_data.social_icons,
        texts=template_data.texts,
    )


@application.context_processor
def utility_processor():
    def human_format_date(date):
        if date == datetime.date.today():
            return "Dnes"
        elif date == datetime.date.today() + datetime.timedelta(days=-1):
            return "Včera"
        elif date == datetime.date.today() + datetime.timedelta(days=1):
            return "Zítra"
        else:
            return date.strftime("%d.%m.%Y")

    def recipe_ingredient_ids_list(recipe):
        return str([i.id for i in recipe.ingredients])

    def link_to(obj, text=None):
        if type(obj) == str:
            if obj == "login":
                if text is None:
                    text = "Přihlaste se"
                return f"<a href='{url_for('LoginView:show')}'>{text}</a>"
            elif obj == "register":
                if text is None:
                    text = "Zaregistrujte se"
                return f"<a href='{url_for('RegisterView:show')}'>{text}</a>"
            else:
                raise NotImplementedError("This string has no associated link_to")

        try:
            return obj.link_to
        except Exception:
            raise NotImplementedError("This object link_to is probably not implemented")

    def option(obj):
        return f"<option name='{obj.name}' value='{obj.id}'>{obj.name}</option>"

    def options(array):
        html = ""
        for item in array:
            html += option(item) + "\n"

        return html

    return dict(
        human_format_date=human_format_date,
        recipe_ingredient_ids_list=recipe_ingredient_ids_list,
        link_to=link_to,
        option=option,
        options=options,
    )


@application.before_request
def session_management():
    current_user.logged_from_admin = session.get("logged_from_admin")

    if application.config["APP_STATE"] == "shutdown" and request.path not in [
        "/shutdown",
        "/static/css/style.css",
    ]:
        return redirect("/shutdown")
    elif request.path == "/shutdown" and application.config["APP_STATE"] != "shutdown":
        return redirect("/")


@application.before_request
def log_request_start():
    g.log_request_start_time = time.time()


@application.teardown_request
def log_request(exception=None):
    # if application.config["APP_STATE"] == "development":
    #     return
    db.session.expire_all()
    pattern = re.compile("/static/")
    if not pattern.search(request.path):
        user_id = getattr(current_user, "id", None)

        item_type = DataHandler.get_additional_request_data("item_type")
        item_id = DataHandler.get_additional_request_data("item_id")

        log = RequestLog(
            url=request.path,
            user_id=user_id,
            remote_addr=request.environ["REMOTE_ADDR"],
            item_type=item_type,
            item_id=item_id,
            duration=time.time() - g.log_request_start_time,
        )
        log.save()


# @application.shell_context_processor
# def make_shell_context():
#     return {"db": db, "User": User}
