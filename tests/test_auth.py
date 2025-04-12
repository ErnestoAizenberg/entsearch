from unittest.mock import MagicMock, patch

import pytest
from auth import auth_bp, get_provider_config
from flask import Flask, session, url_for


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"
    app.config["OAUTH2_PROVIDERS"] = {
        "google": {
            "client_id": "test-client-id",
            "client_secret": "test-secret",
            "authorize_url": "https://google.com/auth",
            "token_url": "https://google.com/token",
            "scopes": ["email"],
            "userinfo": {
                "url": "https://google.com/userinfo",
                "email": lambda x: x.get("email"),
            },
        }
    }
    app.register_blueprint(auth_bp)
    app.user_repo = MagicMock()
    return app


def test_logout(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    response = client.get("/auth/logout")
    assert "user_id" not in session
    assert response.status_code == 302
    assert response.location.endswith(url_for("main.prediction_page"))


def test_oauth2_authorize(client):
    response = client.get("/auth/authorize/google")
    assert response.status_code == 302
    assert "oauth2_state" in session
    assert "google.com/auth" in response.location


def test_oauth2_callback_success(client):
    with client.session_transaction() as sess:
        sess["oauth2_state"] = "test-state"

    with patch("requests.post") as mock_post, patch("requests.get") as mock_get:
        mock_post.return_value.json.return_value = {"access_token": "test-token"}
        mock_post.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"email": "test@example.com"}
        mock_get.return_value.status_code = 200

        app.user_repo.get_user_by_email.return_value = None
        app.user_repo.create_user.return_value = MagicMock(id=1)

        response = client.get("/auth/callback/google?code=test-code&state=test-state")
        assert response.status_code == 302
        assert session["user_id"] == 1
        assert response.location.endswith(url_for("main.prediction_page"))


def test_oauth2_callback_invalid_state(client):
    with client.session_transaction() as sess:
        sess["oauth2_state"] = "correct-state"

    response = client.get("/auth/callback/google?code=test-code&state=wrong-state")
    assert response.status_code == 302
    assert response.location.endswith(
        url_for("auth.oauth2_authorize", provider="google")
    )


def test_get_provider_config(app):
    with app.app_context():
        provider = get_provider_config("google")
        assert provider is not None
        assert provider.client_id == "test-client-id"
        assert get_provider_config("invalid") is None
