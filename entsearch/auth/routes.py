from flask import Blueprint, redirect, url_for, session, current_app, request, abort, flash
import requests
import secrets
from urllib.parse import urlencode
from typing import Optional, Dict, Any, Tuple, Callable
from dataclasses import dataclass

auth_bp = Blueprint('auth', __name__, url_prefix='')

@dataclass
class OAuthProvider:
    client_id: str
    client_secret: str
    authorize_url: str
    token_url: str
    userinfo: Dict[str, Any]
    scopes: list[str]

def get_provider_config(provider_name: str) -> Optional[OAuthProvider]:
    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider_name)
    if not provider_data:
        return None
    return OAuthProvider(**provider_data)

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You've been logged out.", 'success')
    return redirect(url_for('prediction_page'))

@auth_bp.route('/authorize/<provider>')
def oauth2_authorize(provider: str):
    if 'user_id' in session:
        return redirect(url_for('prediction_page'))

    provider_config = get_provider_config(provider)
    if not provider_config:
        abort(404)

    session['oauth2_state'] = secrets.token_urlsafe(16)

    qs = urlencode({
        'client_id': provider_config.client_id,
        'redirect_uri': url_for('auth.oauth2_callback', provider=provider, _external=True),
        'response_type': 'code',
        'scope': ' '.join(provider_config.scopes),
        'state': session['oauth2_state'],
    })

    print(f"[DEBUG] {provider_config.authorize_url}?{qs}")
    return redirect(f"{provider_config.authorize_url}?{qs}")

@auth_bp.route('/callback/<provider>')
def oauth2_callback(provider: str):
    if 'user_id' in session:
        return redirect(url_for('prediction_page'))

    provider_config = get_provider_config(provider)
    if not provider_config:
        abort(404)

    if 'error' in request.args:
        for k, v in request.args.items():
            if k.startswith('error'):
                flash(f'{k}: {v}', 'error')
        return redirect(url_for('prediction_page'))

    if 'oauth2_state' not in session or request.args.get('state') != session['oauth2_state']:
        return redirect(url_for('auth.oauth2_authorize', provider=provider))

    session.pop('oauth2_state')

    if 'code' not in request.args:
        abort(401)

    token_response = requests.post(
        provider_config.token_url,
        data={
            'client_id': provider_config.client_id,
            'client_secret': provider_config.client_secret,
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': url_for('auth.oauth2_callback', provider=provider, _external=True),
        },
        headers={'Accept': 'application/json'}
    )

    if token_response.status_code != 200:
        abort(401)

    oauth2_token = token_response.json().get('access_token')
    if not oauth2_token:
        abort(401)

    user_response = requests.get(
        provider_config.userinfo['url'],
        headers={
            'Authorization': f'Bearer {oauth2_token}',
            'Accept': 'application/json',
        }
    )

    if user_response.status_code != 200:
        abort(401)

    user_info = user_response.json()
    email = provider_config.userinfo['email'](user_info)
    if not email:
        flash('Email not provided by the OAuth provider.', 'error')
        back_url = url_for('prediction_page')
        return redirect(back_url)

    user = current_app.user_repo.get_user_by_email(email)
    if not user:
        base_username = email.split('@')[0]
        username = base_username
        suffix = 1
        while current_app.user_repo.get_user_by_username(username):
            username = f"{base_username}_{suffix}"
            suffix += 1

        user = current_app.user_repo.create_user(
            username=username,
            email=email,
            password="oauth_user"
        )

    session['user_id'] = user.id
    return redirect(url_for('prediction_page'))