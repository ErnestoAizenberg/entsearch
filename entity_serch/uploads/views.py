from entity_serch import app, socketio

from flask import redirect, url_for, render_template, flash, session, current_app, request, abort
import json

import time

from entity_serch import UserRepository, DatasetRepository, EntityRepository
from entity_serch import User, Dataset, Entity, nlp_model

from entity_serch import user_repo
from entity_serch import dataset_repo
from entity_serch import entity_repo


from .utils import download_file, generate_random_password

@app.after_request
def add_cache_headers(response):
    response.cache_control.public = True
    response.cache_control.max_age = 30 * 24 * 60 * 60  #30 times will day past
    response.headers['Cache-Control'] = 'public, max-age={}'.format(30 * 24 * 60 * 60)
    return response

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)
  
public_dses= [
      {
         'password' : 'b5Mi8Ccj2F5Hz3rX',
         'title': 'big_dataset'
      },
      {
         'password' : 'UBqdObHtc8q1btIm', 
         'title': 'short_dataset'
       }
    ]

@app.route('/')
def home():
    user_id = session.get('user_id')
    if user_id:
        user_datasets = dataset_repo.get_users_datasets(user_id)
    else:
        user_datasets = []
    public_datasets = public_dses
    user_datasets = [{'password': dataset.password, 'title': dataset.title, 'created': dataset.created} for dataset in user_datasets]
    
    return render_template('pred.html', user_datasets=user_datasets, public_datasets=public_datasets, user_id=user_id)


@app.route("/about")
def about():
    user_id = session.get('user_id')
    userinfo = user_repo.get_user_by_id(user_id)
    email = userinfo.email if userinfo else "without email"
    return render_template('about.html', email=email)


@app.route("/users/<int:passw>")
def users(passw):
    password = 111
    if passw == password:
        users = user_repo.get_all_users()
        return render_template('users.html', users=users)


@app.route("/datasets")
def datasets():
    user_id = session.get('user_id')
    user_datasets = dataset_repo.get_users_datasets(user_id)
    user_datasets = [{'password': dataset.password, 'title': dataset.title, 'created': dataset.created} for dataset in user_datasets]
    
    return render_template('datasets.html', datasets=user_datasets)


@app.route("/dataset/<string:dataset_password>")
def dataset_detail(dataset_password):
    ds_id = dataset_repo.get_id_by_password(dataset_password)
    dataset = dataset_repo.get_dataset(ds_id)
    
    if dataset is None:
        return "Dataset not found", 404

    entities = entity_repo.get_entities_by_dataset_id(dataset.id)
    if not entities:
        print("No entities found for dataset_id:", dataset.title)

    entities = [{'foreign_identifier': ent.foreign_identifier, 'description': ent.description, 'entity_name': ent.entity_name, 'entity_name_embed': ent.entity_name_embed, 'id': ent.id} for ent in entities]
    return render_template('dataset_detail.html', dataset=dataset, entities=entities)


def get_user_id():
    i = session.get('user_id')
    return i

@app.route('/create_dataset_page')
def create_dataset_page():
    user_id = get_user_id()
    return render_template('csv_file.html')


@app.route('/current/<string:password>', methods=['GET'])
def current_dataset(password):
    ds_id = dataset_repo.get_id_by_password(password)
      
    if ds_id is None:
        last_elements=[]
        return render_template(
                      'edit_dataset_page.html',        
                       dataset=last_elements,
                       dataset_password=password)

    last_elements = entity_repo.last_n_elements(ds_id, 10)[::-1]
    return render_template('edit_dataset_page.html', dataset=last_elements, dataset_password=password)
