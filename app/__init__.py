"""This is init module."""

from flask import Flask, jsonify
from app.middlewares.JWTMiddleware import JWTMiddleware

# Place where app is defined
from app.utils.response import response

app = Flask(__name__)

app.wsgi_app = JWTMiddleware(app.wsgi_app)

from app.routes import main


@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(response(str(e), None, 404)), 404


@app.errorhandler(500)
def resource_server_error(e):
    return jsonify(response(str(e), None, 500)), 500

