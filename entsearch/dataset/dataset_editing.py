# session, dataset_repo, request, app, insert_dataset, flash, entity_repo, redirect, url_for, Entity

import json
import secrets
from datetime import datetime

from flask import flash, redirect, request, session, url_for

from entsearch import Dataset, Entity, app, dataset_repo, entity_repo


def insert_dataset(user_id, title=None):
    message = "success: dataset_created"
    if user_id is None:
        user_id = 999
        message = "info: is not registred"

    password = secrets.token_urlsafe(12)
    if not title:
        title = secrets.token_urlsafe(6)

    dataset_id = dataset_repo.insert_dataset(
        Dataset(title=title, password=password, user_id=user_id, created=datetime.now())
    )
    if dataset_id is None:
        message = "error: dataset hasn't been created"
    return dataset_id, message


def show(objs):
    for o in objs:
        print(
            "***: ",
            o.id,
            o.dataset_id,
            o.entity_name,
            o.entity_name_embed,
            o.description,
            o.foreign_identifier,
        )
    print("end")


def handle_flashes(messages, response):
    for message in messages:
        flash(message)
    return response


@app.route("/add_entity", methods=["POST"])
def add_entity():
    user_id = session.get("user_id")
    ds_password = request.form.get("currentValue")
    print("###ds_password: ", ds_password)
    ds_id = dataset_repo.get_id_by_password(ds_password)
    print("###ds_id :", ds_id)
    messages = []  # list to store messages

    if not ds_id:
        ds_id, message = insert_dataset(user_id)
        messages.append(message)

        dataset = dataset_repo.get_dataset(ds_id)
        ds_password = dataset.password

    foreign_identifier = request.form.get("hidden-id")
    entity_name = request.form.get("word")
    description = request.form.get("description") or "None"
    entity_name_embed = json.dumps([[0, 0, 0], [1, 1, 1], [2, 2, 2]])

    if not foreign_identifier:
        lst_of_foreign_identifiers = entity_repo.get_column_values(
            ds_id, "foreign_identifier"
        )
        foreign_identifier = 1
        while foreign_identifier in lst_of_foreign_identifiers:
            foreign_identifier += 1
            if foreign_identifier > 1000000:
                messages.append(
                    "error: server error, there might be too many entities in your dataset"
                )
                return handle_flashes(messages, redirect("/"))

    entity_id = entity_repo.with_equal(
        foreign_identifier=foreign_identifier, dataset_id=ds_id
    )

    diction = {
        "foreign_identifier": foreign_identifier,
        "dataset_id": ds_id,
        "entity_name": entity_name,
        "description": description,
        "entity_name_embed": entity_name_embed,
    }

    if entity_id:
        entity_repo.delete_entity(entity_id)
        print("&&&&&&&&: deliting...")

    if entity_name:
        if entity_repo.insert_entity(Entity(**diction)) is None:
            messages.append("error: Failed to insert entity.")

    last_elements = entity_repo.last_n_elements(ds_id, 10)[::-1]
    show(last_elements)
    return handle_flashes(
        messages, redirect(url_for("current_dataset", password=ds_password))
    )
