#!/usr/bin/env python
# -*- coding: utf-8 -*-

# run by pyserver

from functools import wraps
import datetime

from flask import Blueprint
from flask import render_template as template, request, redirect
from flask import flash
from flask import current_app as application

from flask_login import login_user, logout_user, current_user, login_required

from flask_dance.contrib.google import google
from flask_dance.consumer import oauth_authorized

from app import models

from app.auth.forms import LoginForm, RegisterForm


auth_blueprint = Blueprint('auth', __name__, template_folder='templates/auth/')

PASSWORD_VERSION = 'bcrypt'


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.username != 'admin':
            return redirect('/wrongpage')
        return f(*args, **kwargs)
    return decorated_function


@auth_blueprint.route('/login', methods=['GET', 'POST'])
def show_login():
    if current_user.is_authenticated:
        return redirect('/dashboard')
    form = LoginForm(request.form)
    if request.method == 'GET':
        return template('auth/login.tpl', form=form)
    elif request.method == 'POST':
        if not form.validate_on_submit():
            return template('auth/login.tpl', form=form)
        if do_login(username=form.username.data, password=form.password.data.encode('utf-8')):
            return redirect('/dashboard')
        else:
            return template('auth/login.tpl', form=form)


@oauth_authorized.connect
def oauth_login(blueprint, token):
    # TODO rewrite for multiple oaths
    if blueprint.name == 'google':
        try:
            user_info = google.get("/oauth2/v2/userinfo").json()
            username = user_info['email']
            google_id = user_info['id']
        except Exception as e:
            application.logger.error(e)
    else:
        # not implemented
        return False

    # Try to log with google_id
    user = models.User.load(google_id, load_type="google_id")
    if not user:
        user = models.User.load(username, load_type="username")

    if user:
        do_login(user=user)

    else:
        user = models.User()
        user.username = username
        user.password = None
        user.google_id = google_id

        try:
            user.first_name = user_info['given_name']
        except Exception:
            user.first_name = "-"

        try:
            user.last_name = user_info['family_name']
        except Exception:
            user.last_name = "-"

        do_register(user, source="google_oauth")


def do_login(username=None, password=None, from_register=False, user=None):
    # get user if there is none
    if user is None and username is None:
        # This shouldn't happen
        application.logger.error("Login error: user is None and username is None")
        flash('Někde se stala chyba. Kontaktujte mě <a href="mailto:ketocalc.jmp@gmail.com">e-mailem</a>')
        return False
    elif user is None and username is not None:
        # Load user by username
        user = models.User.load(username, load_type="username")
    else:
        # Already has user
        pass

    # log user, if either has google_id (going from oauth) or has valid password
    # TODO this is not very nice
    if user is not None and (user.google_id is not None or (password is not None and password != "" and user.check_login(password))):
        login_user(user, remember=True)
        if application.config['APP_STATE'] == 'production':
            user.last_logged_in = datetime.datetime.now()
            try:
                user.login_count += 1
            # in case login_count is NULL
            # TODO which Exception is it?
            except Exception:
                user.login_count = 1
            user.edit()
        if not from_register:
            flash('Byl jste úspěšně přihlášen.', 'success')
        elif from_register:
            flash('Byl jste úspěšně zaregistrován.', 'success')
        return True
    else:
        flash('Přihlášení se nezdařilo.', 'error')
        return False


@login_required
@auth_blueprint.route('/logout')
def do_logout():
    if current_user.is_authenticated:
        logout_user()
        flash('Byl jste úspěšně odhlášen.', 'info')
    return redirect('/login')


@auth_blueprint.route('/register', methods=['GET', 'POST'])
def show_register():
    form = RegisterForm(request.form)
    if request.method == 'GET':
        return template('auth/register.tpl', form=form)
    elif request.method == 'POST':
        if not form.validate_on_submit():
            return template('auth/register.tpl', form=form)
        if not validate_register(form.username.data):
            form.username.errors = ['Toto jméno nemůžete použít']
            return template('auth/register.tpl', form=form)

        user = models.User()
        form.populate_obj(user)
        user.set_password_hash(form.password.data.encode('utf-8'))
        user.password_version = PASSWORD_VERSION

        if do_register(user):
            return redirect('/dashboard')
        else:
            return template('auth/register.tpl', form=form)


def do_register(user, source=None):
    if not validate_register(user.username):
        # user with same username
        flash('Toto uživatelské jméno nemůžete použít', 'error')
        return False
    elif user.save() is True:
        if source == "google_oauth":
            do_login(user=user)
        else:
            do_login(username=user.username, password=user.password.encode('utf-8'), from_register=True)
        return True
    else:
        flash('Registrace neproběhla v pořádku', 'error')
        return False


def validate_register(username):
    """
    Tests for registration validity:
        - unique username

    Arguments:
        username {string}
    Returns:
        bool
    """
    if models.User.load(username, load_type="username") is not None:
        return False
    else:
        return True
