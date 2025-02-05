#app, dataset_repo, render_template, session

from entity_serch import app, dataset_repo
from flask import render_template, session


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
def prediction_page():
    user_id = session.get('user_id')
    if user_id:
        user_datasets = dataset_repo.get_users_datasets(user_id)
    else:
        user_datasets = []
    public_datasets = public_dses
    user_datasets = [{'password': dataset.password, 'title': dataset.title, 'created': dataset.created} for dataset in user_datasets]
    
    return render_template('pred.html', user_datasets=user_datasets, public_datasets=public_datasets, user_id=user_id)
