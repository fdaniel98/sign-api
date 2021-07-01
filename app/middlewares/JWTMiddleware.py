from werkzeug.wrappers import Request, Response
from dotenv import dotenv_values
from flask import jsonify

from app.utils.JWToken import verify_token


class JWTMiddleware():
    '''
    Simple WSGI middlewares
    '''

    def __init__(self, app):
        self.app = app
        self.config = config = dotenv_values(".env")

    def __call__(self, environ, start_response):
        request = Request(environ)
        auth_header = request.headers.get('Authorization')

        if auth_header is None:
            res = Response('Token Missing', mimetype='application/json', status=401)
            return res(environ, start_response)

        # verify the token
        if verify_token(auth_header, self.config['JWT_SECRET_TOKEN']):
            return self.app(environ, start_response)

        res = Response(u'Authorization failed', mimetype='text/plain', status=401)
        return res(environ, start_response)
