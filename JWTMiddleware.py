from dotenv import dotenv_values
from wtforms import ValidationError
from wtforms.form import BaseForm

from app import cache
from app.utils.JWToken import verify_token


def valid_api_key(form: BaseForm, _field):
    config = dotenv_values(".env")
    auth_header = form.data['Authorization']
    secret = config['JWT_SECRET_TOKEN']
    token = auth_header.replace('Bearer ', '')

    # verify the token
    data = verify_token(token, secret)

    if not data:
        raise ValidationError('API Key invalid')

    cache.set(token, data)
