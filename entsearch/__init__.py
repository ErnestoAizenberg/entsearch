import os
from flask import Flask
from flask_socketio import SocketIO
from config import Config
from entsearch.repositories import UserRepository, DatasetRepository, EntityRepository
from .models import User, Dataset, Entity, nlp_model

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app)
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

user_repo = UserRepository()
dataset_repo = DatasetRepository()
entity_repo = EntityRepository()

app.user_repo = user_repo


from .caching.routes import configure_cache
from .views import about, users, demo
from .auth.routes import auth_bp, oauth2_authorize, oauth2_callback, logout

app.register_blueprint(auth_bp, url_prefix="")

from .dataset import (
    create_dataset,
    dataset_detail,
    create_dataset_page,
    current_dataset,
    datasets,
    add_entity,
)
from .nlp_prediction import handle_prediction, prediction_page


if __name__ == "__main__":
    socketio.run(app, debug=True)
