from flask import render_template, session
import flask_dance.contrib

from CTFd.auth import confirm, register, reset_password, login
from CTFd.models import db, Users
from CTFd.utils.logging import log
from CTFd.utils.security.auth import login_user, logout_user

from CTFd import utils

def load(app):
    oauth_client_id = utils.get_app_config('OAUTH_CLIENT_ID')
    oauth_client_secret = utils.get_app_config('OAUTH_CLIENT_SECRET')
    oauth_provider = utils.get_app_config('OAUTH_PROVIDER')
    create_missing_user = utils.get_app_config('OAUTH_CREATE_MISSING_USER')

    # Either retrieve the user (if exists), create it (if appropriate), or return None
    def get_bridge_user(displayName, email):
        user = Users.query.filter_by(email=resp['userPrincipalName']).first()
        if user is not None:
            log('logins', "[{date}] {ip} - {name} OAuth2 bridged user found")
            return user
        if not create_missing_user:
            log('logins', "[{date}] {ip} - {name} No OAuth2 bridged user found and not configured to create missing users")
            return None
        with app.app_context():
            log('logins', "[{date}] {ip} - {name} No OAuth2 bridged user found, creating user")
            user = new Users(
                name=displayName.strip(),
                email=email.lower(),
                password="abc123".strip()
            )
            db.session.add(user)
            db.session.commit()
            db.session.flush()
            return user

    # Lambdas to create blueprints for the authentication endpoints
    provider_blueprints = {
        'azure': lambda: return flask_dance.contrib.make_azure_blueprint(
            login_url='/auth/azure',
            client_id=oauth_client_id,
            client_secret=oauth_client_secret,
            redirect_url="/auth/azure/confirm")
    }

    # Lambdas to retrieve/create users
    provider_users = {
        'azure': lambda: 
            resp = flask_dance.contrib.azure.get("/v1.0/me").json()
            return get_bridge_user(
                displayName=resp["displayName"],
                email=resp["userPrincipalName"]
            )
    }

    provider_blueprint = provider_blueprints[oauth_provider]()

    @provider_blueprint.route('/auth/<string:auth_provider>/confirm', methods=['GET'])
    def confirm_auth_provider(req_auth_provider):
        session.regenerate()
        user = provider_users[req_auth_provider]()
        if user is not None:
            login_user(user)
        return redirect_url('/')

    app.register_blueprint(provider_blueprints[oauth_provider])

    # TODO: Disable backend (POST) as well
    # ('', 204) is "No Content" code
    app.view_functions['auth.login'] = lambda: ('', 204)
    app.view_functions['auth.register'] = lambda: ('', 204)
    app.view_functions['auth.reset_password'] = lambda: ('', 204)
    app.view_functions['auth.confirm'] = lambda: ('', 204)     