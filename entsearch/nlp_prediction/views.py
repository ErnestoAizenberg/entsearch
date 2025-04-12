# app, dataset_repo, render_template, session

from flask import render_template, session

from entsearch import app, dataset_repo

public_id = 1


@app.route("/")
def prediction_page():
    user_id = session.get("user_id")
    if user_id is None:
        user_datasets = []
    else:
        user_datasets = dataset_repo.get_users_datasets(user_id)

    public_datasets = dataset_repo.get_users_datasets(public_id)

    datasets = [
        {
            "password": dataset.password,
            "title": dataset.title,
            "created": dataset.created,
        }
        for dataset in user_datasets + public_datasets
    ]

    return render_template("pred.html", datasets=datasets, user_id=user_id)
