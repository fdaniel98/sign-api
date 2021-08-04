"""This is init module."""

from flask import Flask, jsonify
from flask_caching import Cache

from dotenv import dotenv_values

config = dotenv_values(".env")

CONFIG_CACHE = {
    "DEBUG": config['DEBUG'],          # some Flask specific configs
    "CACHE_TYPE": "RedisCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": config['REDIS_TIMEOUT'],
    "CACHE_REDIS_HOST": config['REDIS_HOST']
}


# Place where app is defined
from app.utils.response import response

app = Flask(__name__)
cache = Cache(app, config=CONFIG_CACHE)
app.config.from_mapping(config)
app.cache = cache

from app.routes import main


@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(response(str(e), None, 404)), 404


@app.errorhandler(500)
def resource_server_error(e):
    return jsonify(response(str(e), None, 500)), 500


@app.errorhandler
def resource_server_error(e):
    return jsonify(response(str(e), None, 400)), 400

