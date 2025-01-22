from entity_serch import app, socketio

from flask import redirect, url_for, render_template, flash, session, current_app, request, abort
import json

import time

from entity_serch import UserRepository, DatasetRepository, EntityRepository
from entity_serch import User, Dataset, Entity, nlp_model

from entity_serch import user_repo
from entity_serch import dataset_repo
from entity_serch import entity_repo

  
@app.route('/')
def home():
    user_id = session.get('user_id')
    user_datasets = dataset_repo.get_users_datasets(user_id)
    user_datasets = [{'password': dataset.password, 'title': dataset.title, 'created': dataset.created} for dataset in user_datasets]
    
    return render_template('pred.html', datasets=user_datasets, user_id=user_id)


@app.route('/login', methods=["GET", "POST"])
def login_page():
    user_id = session.get('user_id')
    return render_template('login.html', user_id=user_id)


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
    dataset = dataset_repo.get_dataset_by_password(dataset_password)
    
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

    time.sleep(0)
    user_id = get_user_id()
    #if request.method == 'POST':
    
    return render_template('csv_file.html')


@app.route('/current/<string:password>', methods=['GET', 'POST'])
def current_dataset(password):
    ds_id = dataset_repo.get_id_by_password(password)      
    if ds_id is None: abort(404)

    if request.method == 'POST':
        foreign_identifier = request.form.get('hidden-id')
        entity_name = request.form.get('word')
        description = request.form.get('description')
        entity_name_embed = json.dumps([[0, 0, 0], [1, 1, 1], [2, 2, 2]])

        if not description:
            description = 'None'

        if not foreign_identifier:
            lst_of_foreign_identifiers = entity_repo.get_column_values(ds_id, 'foreign_identifier')
            foreign_identifier = 1
            while foreign_identifier in lst_of_foreign_identifiers:
                foreign_identifier += 1
                if foreign_identifier > 1000000:
                    flash('error: server error, there are might be too much entities in your dataset')
                    return redirect('/')


        entity_id = entity_repo.with_equal(
               foreign_identifier=foreign_identifier,
               dataset_id=ds_id
         )

        diction = {
            'foreign_identifier': foreign_identifier,
            'dataset_id': ds_id,
            'entity_name': entity_name,
            'description': description,
            'entity_name_embed': entity_name_embed
        }

        if entity_id:
            entity_repo.delete_entity(entity_id)
        
        if entity_name:  
            if entity_repo.insert_entity(Entity(**diction)) is None:
                flash("error: Failed to insert entity.")

    last_elements = entity_repo.last_n_elements(ds_id, 10)[::-1]
    return render_template('edit_dataset_page.html', dataset=last_elements)
