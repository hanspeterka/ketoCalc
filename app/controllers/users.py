from flask import render_template as template
from flask import request, url_for, redirect, abort, flash
from flask import current_app as application

from flask_classful import FlaskView
from flask_login import login_required, current_user

from app.models.users import User


class UsersView(FlaskView):
    decorators = [login_required]

    def before_request(self, name):
        self.user = User.load(current_user.id)
        if self.user is None:
            abort(404)

    def post(self, page_type=None):
        if page_type == "change_password":
            self.user.set_password_hash(request.form["password"].encode("utf-8"))
            self.user.password_version = application.config["PASSWORD_VERSION"]

            if self.user.edit():
                flash("Heslo bylo změněno", "success")
            else:
                flash("Nepovedlo se změnit heslo", "error")
            return redirect(url_for("UsersView:show"))
        else:
            self.user.first_name = request.form["firstname"]
            self.user.last_name = request.form["lastname"]
            if self.user.edit() is not None:
                flash("Uživatel byl upraven", "success")
            else:
                flash("Nepovedlo se změnit uživatele", "error")
            return redirect(url_for("UsersView:show"))

    def show(self):
        return template("users/show.html.j2", user=self.user)

    def edit(self):
        return template("users/edit.html.j2", user=self.user)
