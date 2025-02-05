from entity_serch import app, socketio

from flask import redirect, url_for, render_template, flash, abort, session, current_app, request
from datetime import datetime 
import os 
from io import StringIO
import requests
import pandas as pd
import time
import json

from urllib.parse import urlencode
import secrets
import string
from flask_socketio import emit


from .utils import download_file, generate_random_password

from entity_serch import UserRepository, DatasetRepository, EntityRepository
from entity_serch import User, Dataset, Entity, nlp_model

from entity_serch import user_repo
from entity_serch import dataset_repo
from entity_serch import entity_repo


# Функция для преобразования формы в DataFrame
def form_to_df(file):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    saved_path = download_file(file, file_path)
    
    if saved_path is None:
        return None, "error: не удалось сохранить файл"

    try:
        df = pd.read_csv(saved_path, header=None)
    except Exception as e:
        return None, f"error: не удалось прочитать CSV - {str(e)}"

    return df, "info: DataFrame успешно создан"


def add_entities(df, Entity, entity_repo, dataset_id, structure):
    try:
        for i, row in df.iterrows():
            try:
                entity_name = row.iloc[structure['name']]
                description = row.iloc[structure['description']]
                entity_name_embed = json.dumps([[0, 0, 0], [1, 1, 1], [2, 2, 2]])
                identificator = row.iloc[structure['id_p']] if structure['id_p'] else i
            except Exception as e:
                return None, f"error: не удалось извлечь данные из строки {i} - {str(e)}"

            try:
                entity = Entity(
                    dataset_id=dataset_id,
                    entity_name=entity_name,
                    description=description,
                    entity_name_embed=entity_name_embed,
                    foreign_identifier=identificator
                )
            except Exception as e:
                return None, f"error: не удалось создать сущность на строке {i} - {str(e)}"

            try:
                last_id = entity_repo.insert_entity(entity)
                if last_id is None: None, f"error: не удалось вставить сущность на строке {i}"

            except Exception as e:
                return None, f"error: не удалось вставить сущность на строке {i} - {str(e)}"

    except Exception as e:
        return None, f"error: ошибка при добавлении сущностей - {str(e)}"

    return 1, "info: все сущности успешно добавлены"


def insert_dataset(user_id, title=None):
    message = "success: dataset_created"
    if user_id is None:
        user_id = 999
        message = "info: is not registred"

    password = secrets.token_urlsafe(12)
    if not title:
        title = secrets.token_urlsafe(6)

    dataset_id = dataset_repo.insert_dataset(
        Dataset(
            title=title,
            password=password,
            user_id=user_id,
            created=datetime.now()
        )
    )
    if dataset_id is None:
        message = "error: dataset hasn't been created"
    return dataset_id, message


@app.route('/create_dataset', methods=['POST'])
def create_dataset():
    user_id = session.get('user_id')
    title = request.form.get('name_file')
    file = request.files.get('csv-file')

    if user_id is None:
        flash("error: загрузка файлов требует чтоб пользователь был зарегистрированны")
        return redirect(url_for('create_dataset_page'))

    if not file:
        flash("error: пожалуйста выберите файл")
        return redirect(url_for('create_dataset_page'))

    dataset_id, message = insert_dataset(user_id=user_id, title=title)
    flash(message)
    if dataset_id is None:
        return redirect(url_for('create_dataset_page'))

    isforeign_id = request.form.get('isid') == 'on'
    name_p = int(request.form.get("name_p"))
    description_p = int(request.form.get("description_p"))
    id_p = int(request.form.get("id_p")) if isforeign_id else None
    structure = {'name': name_p, 'description': description_p, 'id_p': id_p}
    flash("info: " + json.dumps(structure))

    df, message = form_to_df(file)
    print(df)
    flash(message)

    if df is not None:
        status, message = add_entities(df, Entity, entity_repo, dataset_id, structure)
        if status is None:
            entity_repo.delete_entities_by_dataset_id(dataset_id)
            flash('error: произошла ошибка, данные удалены')
        else:
            flash(message)
    else:
        flash('error: error')

    return redirect(url_for('create_dataset_page'))




@socketio.on('predict')
def handle_prediction(data):
    emit('clean')
    dataset_ids = list(data['dataset'])
    input_text = data['text']
    threshold = data['threshold']
    by_description = data['isdescription']
   
    for ds_id in dataset_ids:
        lst_names = entity_repo.get_column_values(ds_id, 'entity_name')
        lst_descriptions = entity_repo.get_column_values(ds_id, 'description')
        name_embedding = entity_repo.get_column_values(ds_id, 'entity_name_embed')

        lst_of_shure, lst_of_id = nlp_model(text=input_text)

        sorted_inds = [i for i in range(len(lst_of_id)) if lst_of_shure[i] >= threshold]
        lst_of_shure, lst_of_id = [lst_of_shure[i] for i in sorted_inds], [lst_of_id[i] for i in sorted_inds]
        
        amount = len(lst_of_id)

        lst_of_name = [lst_names[i] for i in lst_of_id if i < len(lst_names)]   
        lst_of_description = [lst_descriptions[i] for i in lst_of_id if i < len(lst_descriptions)] if by_description else None
        
        data = {
            'dataset_name': ds_id,
            'amount': amount,
            'status': 200,
            'prediction': {
                 'shure': lst_of_shure,
                 'id': lst_of_id,
                 'name': lst_of_name,
                 'description': lst_of_description
            }
        }

        emit('data_ready', data)





def handle_flashes(messages, response):
    for message in messages:
        flash(message)
    return response

@app.route('/add_entity', methods=['POST'])
def add_entity():
    user_id = session.get('user_id')
    ds_password = request.form.get('currentValue')
    ds_id = dataset_repo.get_id_by_password(ds_password)
    
    messages = [] #list to store messages 

    if not ds_id:
        ds_id, message = insert_dataset(user_id)
        messages.append(message)

        dataset = dataset_repo.get_dataset(ds_id)
        ds_password = dataset.password

    foreign_identifier = request.form.get('hidden-id')
    entity_name = request.form.get('word')
    description = request.form.get('description') or 'None'
    entity_name_embed = json.dumps([[0, 0, 0], [1, 1, 1], [2, 2, 2]])

    if not foreign_identifier:
        lst_of_foreign_identifiers = entity_repo.get_column_values(ds_id, 'foreign_identifier')
        foreign_identifier = 1
        while foreign_identifier in lst_of_foreign_identifiers:
            foreign_identifier += 1
            if foreign_identifier > 1000000:
                messages.append('error: server error, there might be too many entities in your dataset')
                return handle_flashes(messages, redirect('/'))
    
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
            messages.append("error: Failed to insert entity.")

    return handle_flashes(messages, redirect(url_for('current_dataset', password=ds_password)))

