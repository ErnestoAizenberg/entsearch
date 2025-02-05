 #Entity, entity_repo, request, redirect, flash, pd(pandas), session, secrets, app

from entity_serch import app

from flask import redirect, url_for, render_template, flash, session, request
import requests
import pandas as pd
import secrets
import json
import os
from datetime import datetime

from entity_serch import Dataset, Entity
from entity_serch import dataset_repo, entity_repo




def download_file(file, file_path):
    try:
        file.save(file_path)
        return file_path
    except Exception as e:
        print('Duuring the process of loading file an exception has occurred:', e)
        return None


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



@app.route('/create_dataset', methods=['POST', 'GET'])
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

