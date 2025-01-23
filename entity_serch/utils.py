import secrets
import string
import os
from flask import flash


def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(characters) for i in range(length))
    return password


def download_file(file, file_path):
    try:
        file.save(file_path)
        return file_path
    except Exception as e:
        print('Duuring the process of loading file an exception has occurred:', e)
        return None
