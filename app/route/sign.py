from app import app
from app.services import signService
from flask import jsonify


@app.route("/")
def main_route():
    res = signService.main_route();
    return jsonify(res);