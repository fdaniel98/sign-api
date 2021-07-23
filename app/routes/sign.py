from app import app
from app.services import signService
from flask import jsonify, Blueprint

signBp = Blueprint('sign', __name__, url_prefix='/sign')


@signBp.get("/")
def main_route():
    res = signService.get_all();
    return jsonify(res);

