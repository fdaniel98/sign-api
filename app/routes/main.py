from app import app
from flask import jsonify


@app.route("/")
def main_route():
    res = {
        'apiVersion': 'v1.0',
        'status': 200,
        'message': 'Welcome to the Sign Flask API'
    }
    return jsonify(res);