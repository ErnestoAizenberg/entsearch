# app, get_user_id, render_template, session, dataset_repo, entity_repo

from flask import render_template, session

from entsearch import app, dataset_repo, entity_repo

public_id = 1


@app.route("/datasets")
def datasets():
    user_id = session.get("user_id")
    if user_id:
        user_datasets = dataset_repo.get_users_datasets(user_id)
    else:
        user_datasets = []

    public_datasets = dataset_repo.get_users_datasets(public_id)

    datasets = [
        {
            "password": dataset.password,
            "title": dataset.title,
            "created": dataset.created,
        }
        for dataset in user_datasets + public_datasets
    ]

    return render_template("datasets.html", datasets=datasets, user_id=user_id)


def get_user_id():
    i = session.get("user_id")
    return i


@app.route("/create_dataset_page")
def create_dataset_page():
    user_id = get_user_id()
    return render_template("csv_file.html", user_id=user_id)


@app.route("/dataset/<string:dataset_password>")
def dataset_detail(dataset_password):
    user_id = session.get("user_id")

    ds_id = dataset_repo.get_id_by_password(dataset_password)
    dataset = dataset_repo.get_dataset(ds_id)

    print(f"dataset received: {dataset}")
    if dataset is None:
        return "Dataset not found", 404

    entities = entity_repo.get_entities_by_dataset_id(ds_id)
    if not entities:
        print("No entities found for dataset_id:", dataset.title)

    entities = [
        {
            "foreign_identifier": ent.foreign_identifier,
            "description": ent.description,
            "entity_name": ent.entity_name,
            "entity_name_embed": ent.entity_name_embed,
            "id": ent.id,
        }
        for ent in entities
    ]
    return render_template(
        "dataset_detail.html", dataset=dataset, entities=entities, user_id=user_id
    )


@app.route("/current/<string:password>", methods=["GET"])
def current_dataset(password):
    ds_id = dataset_repo.get_id_by_password(password)
    user_id = session.get("user_id")
    if ds_id is None:
        last_elements = []
        return render_template(
            "edit_dataset_page.html", dataset=last_elements, dataset_password=password
        )

    last_elements = entity_repo.last_n_elements(ds_id, 10)[::-1]
    print("@@@:", last_elements)
    return render_template(
        "edit_dataset_page.html",
        dataset=last_elements,
        dataset_password=password,
        user_id=user_id,
    )
