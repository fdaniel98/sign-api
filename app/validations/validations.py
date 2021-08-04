from flask_inputs import Inputs
from wtforms.validators import DataRequired

from JWTMiddleware import valid_api_key


class ApiTokenValidation(Inputs):
    headers = {
        'Authorization': [DataRequired('Authorization header is required'), valid_api_key]
    }


class SignInputs(Inputs):
    form = {
        'cert': [DataRequired(message='Cert is required')],
        'reason': [DataRequired(message='reason is required')],
        'text_sign': [DataRequired(message='text_sign is required')],
        'location': [DataRequired(message='location is required')],
        'contact': [DataRequired(message='contact is required')]
    }