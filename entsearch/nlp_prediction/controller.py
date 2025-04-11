#socketio, emit, entity_repo, nlp_model

from entity_serch import socketio, entity_repo
from flask_socketio import emit
from entity_serch import nlp_model
import time

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

