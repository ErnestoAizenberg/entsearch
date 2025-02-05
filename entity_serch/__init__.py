import os
from flask import Flask
from flask_socketio import SocketIO
from .config import Config

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

from .repositories import UserRepository, DatasetRepository, EntityRepository
from .models import User, Dataset, Entity, nlp_model

user_repo = UserRepository()
dataset_repo = DatasetRepository()
entity_repo = EntityRepository()

from .views import about, users
from .registration import oauth2_authorize, oauth2_callback, logout, login_page
from .dataset import create_dataset,  dataset_detail, create_dataset_page, current_dataset, datasets, add_entity
from .nlp_prediction import handle_prediction, prediction_page


if __name__ == '__main__':
    socketio.run(app,  debug=True)
