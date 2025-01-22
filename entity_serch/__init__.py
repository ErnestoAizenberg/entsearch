import os
from flask import Flask
from flask_socketio import SocketIO
from .config import Config

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

from entity_serch.repositories import UserRepository, DatasetRepository, EntityRepository
from entity_serch.models import User, Dataset, Entity, nlp_model


user_repo = UserRepository()
dataset_repo = DatasetRepository()
entity_repo = EntityRepository()

from entity_serch.controller import create_dataset, oauth2_authorize, oauth2_callback, handle_prediction

from entity_serch.views import about, create_dataset_page, home, login_page, current_dataset, datasets, users, dataset_detail


if __name__ == '__main__':
    socketio.run(app,  debug=True)
