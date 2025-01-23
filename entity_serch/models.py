# Domain models
class User:
    def __init__(self, email, username, password, id, created=None,):
        self.id = id
        self.created = created
        self.email = email
        self.username = username
        self.password = password


class Dataset:
    def __init__(self, title, password, user_id, created, id=None):
        self.id = id
        self.title = title
        self.password = password
        self.user_id = user_id
        self.created = created


class Entity:
    _id_counter = 0
    def __init__(self, dataset_id, entity_name, entity_name_embed, description, foreign_identifier):
        self.id = self._generate_id()
        self.dataset_id = dataset_id
        self.entity_name = entity_name
        self.entity_name_embed = entity_name_embed
        self.description = description
        self.foreign_identifier = foreign_identifier

    def _generate_id(self):
        self._id_counter += 1
        return self._id_counter

def nlp_model(text):
    return [0.1, 0.2, 0.3, 0.4, 0.5, 0.6], [1, 2, 3, 4, 5, 98]




# Define DAO interfaces
class UserDAO:
    def get_user_by_id(self, id):
        raise NotImplementedError

class DatasetDAO:
    def get_all_datasets(self, user_id):
        """Возвращает все датасеты для указанного пользователя."""
        raise NotImplementedError

    def insert_dataset(self, dataset):
        """Вставляет новый датасет."""
        raise NotImplementedError
    
    def delete_dataset(self, dataset_id):
        """Удаляет датасет по ID."""
        raise NotImplementedError

class EntityDAO:
    def get_column_values(self, ds_id, column_name):
        raise NotImplementedError
