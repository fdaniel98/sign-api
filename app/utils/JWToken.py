from flask import request
from jwt import decode
from dotenv import dotenv_values

config = dotenv_values('.env')


def verify_token(token, secret):
    data = decode(token, secret, algorithms=["HS256"]);
    return data;


def get_user():
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        return None
    secret = config['JWT_SECRET_TOKEN']
    token = auth_header.replace('Bearer ', '')
    return verify_token(token, secret)