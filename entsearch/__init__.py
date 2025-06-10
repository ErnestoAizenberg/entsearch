import os

from flask import Flask
from flask_socketio import SocketIO

from config import Config
from entsearch.repositories import DatasetRepository, EntityRepository, UserRepository

from .models import Dataset, Entity, User, nlp_model

__all__ = [
    "Dataset",
    "Entity",
    "User",
    "nlp_model",
    "dataset_repo",
    "dataset_repo",
    "app",
    "user_repo",
    "socketio",
]
app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app)
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

user_repo = UserRepository()
dataset_repo = DatasetRepository()
entity_repo = EntityRepository()

app.user_repo = user_repo


from .auth.routes import auth_bp, logout, oauth2_authorize, oauth2_callback
from .caching.routes import configure_cache
from .views import about, demo, users

app.register_blueprint(auth_bp, url_prefix="")

from .dataset.dataset_editing import add_entity
from .dataset.dataset_creating import create_dataset

from .dataset.views import (
    create_dataset_page,
    current_dataset,
    dataset_detail,
    datasets,
)
from .nlp_prediction import handle_prediction, prediction_page
