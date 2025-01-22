import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    UPLOAD_FOLDER = 'uploads'
    OAUTH2_PROVIDERS = {
        'google': {
            'client_id': os.getenv('CLIENT_ID'),
            'client_secret': os.getenv('CLIENT_SECRET'),
            'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
            'token_url': 'https://accounts.google.com/o/oauth2/token',
            'userinfo': {
                'url': 'https://www.googleapis.com/oauth2/v3/userinfo',
                'email': lambda json: json['email'],
            },
            'scopes': ['https://www.googleapis.com/auth/userinfo.email'],
        },
    }
