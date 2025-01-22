import sqlite3
from .models import User, Dataset, Entity


def get_db_connection(db_name="app.db"):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn


# Base repository
class BaseRepository:
    def __init__(self, db_name="app.db"):
        self.db_name = db_name

    def insert_into(self, table_name, data):
        with get_db_connection(self.db_name) as conn:
            cursor = conn.cursor()
            columns = ', '.join(data.keys())
            placeholders = ', '.join('?' for _ in data)
            sql = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
            
            cursor.execute(sql, tuple(data.values()))
            conn.commit()
            return cursor.lastrowid

    def delete_from(self, table_name, id):
        with get_db_connection(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(f'DELETE FROM {table_name} WHERE id = ?', (id,))
            conn.commit()

    def is_exist(self, table_name, id):
        with get_db_connection(self.db_name) as conn:
            cursor = conn.cursor()
            row = cursor.execute(f'SELECT 1 FROM {table_name} WHERE id = ?', (id,)).fetchone()
            return row is not None


# User repository
class UserRepository(BaseRepository):
    def insert_user(self, user):
        data = {
            'username': user.username,
            'email': user.email,
            'password': user.password
        }
        return self.insert_into('users', data)

    def get_user_by_id(self, user_id):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            user_row = cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
            return User(user_row['id'], user_row['created'], user_row['email'], user_row['username'], user_row['password']) if user_row else None

    def get_user_by_email(self, email):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            user_row = cursor.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
            return User(user_row['id'], user_row['created'], user_row['email'], user_row['username'], user_row['password']) if user_row else None

    def get_all_users(self):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            users = cursor.execute("SELECT * FROM users").fetchall()
            return [User(u['email'], u['username'], u['password'], u['created'], u['id']) for u in users]

    def user_exists(self, user_id):
        return self.is_exist('users', user_id)


# Dataset repository
class DatasetRepository(BaseRepository):
    def insert_dataset(self, dataset):
        data = {
            'title': dataset.title,
            'password': dataset.password,
            'user_id': dataset.user_id
        }
        return self.insert_into('datasets', data)

    def get_users_datasets(self, user_id):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            datasets = cursor.execute("SELECT * FROM datasets WHERE user_id = ?", (user_id,)).fetchall()
            return [Dataset(title=d['title'], password=d['password'], user_id=d['user_id'], created=d['created']) for d in datasets]

    def delete_dataset(self, dataset_id):
        return self.delete_from('datasets', dataset_id)

    def get_id_by_password(self, password):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            dataset_row = cursor.execute('SELECT id FROM datasets WHERE password = ?', (password,)).fetchone()
            return dataset_row['id'] if dataset_row else None

    def get_dataset_by_password(self, password):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            dataset = cursor.execute('SELECT * FROM datasets WHERE password = ?', (password,)).fetchone()
            return Dataset(title=dataset['title'], password=dataset['password'], user_id=dataset['user_id'], created=dataset['created'])

    def dataset_exists(self, dataset_id):
        return self.is_exist('datasets', dataset_id)


# Entity repository
class EntityRepository(BaseRepository):

    ALLOWED_COLUMNS = ['entity_name', 'description', 'entity_name_embed', 'foreign_identifier']

    def insert_entity(self, entity):
        data = {
            'entity_name': entity.entity_name,
            'description': entity.description,
            'entity_name_embed': entity.entity_name_embed,
            'foreign_identifier': entity.foreign_identifier,
            'dataset_id': entity.dataset_id
        }

        if not data['entity_name'] or not data['description'] or not data['entity_name_embed'] or not data['foreign_identifier'] or not data['dataset_id']:
            return None

        return self.insert_into('entities', data)

    def delete_entity(self, id):
        return self.delete_from('entities', id)

    def delete_entities_by_dataset_id(self, dataset_id):
        return self.delete_from('entities', dataset_id)

    def get_entities_by_dataset_id(self, dataset_id):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM entities WHERE dataset_id = ?", (dataset_id,))
            return [Entity(
                      dataset_id=row['dataset_id'], 
                      entity_name=row['entity_name'],
                      entity_name_embed=row['entity_name_embed'],
                      description=row['description'],
                      foreign_identifier=row['foreign_identifier']
                    ) for row in cursor.fetchall()]

            

    def last_n_elements(self, dataset_id, n):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM entities WHERE dataset_id = ? ORDER BY id DESC LIMIT ?", (dataset_id, n))
            ents = [Entity(
                      dataset_id=row['dataset_id'], 
                      entity_name=row['entity_name'],
                      entity_name_embed=row['entity_name_embed'],
                      description=row['description'],
                      foreign_identifier=row['foreign_identifier']
                    ) for row in cursor.fetchall()]

            return ents

    def is_entity_exists(self, entity_id):
        return self.is_exist('entities', entity_id)

    def with_equal(self, foreign_identifier, dataset_id):
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                entity_id = cursor.execute(
                    'SELECT id FROM entities WHERE foreign_identifier = ? AND dataset_id = ?', 
                    (foreign_identifier, dataset_id)
                ).fetchone()

                return entity_id[0] if entity_id else None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None


    def get_column_values(self, ds_id, column):
        if column not in self.ALLOWED_COLUMNS:
            raise ValueError(f"Invalid column: {column}")

        return self._get_column_value(ds_id, column)

    def _get_column_value(self, ds_id, column):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT {} FROM entities WHERE dataset_id = ?".format(column), (ds_id,))
            return [row[0] for row in cursor.fetchall()]



 
