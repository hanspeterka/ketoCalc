from flask import request, redirect

from app import create_app

from app.models import db, User

from app.data import template_data

application = create_app()


@application.context_processor
def inject_globals():
    return dict(icons=template_data.icons, texts=template_data.texts)


@application.before_request
def session_management():
    # print(application.config['APP_STATE'])
    if application.config['APP_STATE'] == 'shutdown' and request.path not in ['/shutdown', '/static/style.css']:
        return redirect('/shutdown')
    elif request.path == '/shutdown' and application.config['APP_STATE'] != 'shutdown':
        return redirect('/')


@application.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}
