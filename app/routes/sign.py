from flask import request
from flask_inputs import Inputs
from wtforms.validators import DataRequired

from app.services import signService
from flask import jsonify, Blueprint

from app.validations.validations import SignInputs
from config import config

signBp = Blueprint('sign', __name__, url_prefix='/sign')

@signBp.get("/")
def main_route():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", config['PER_PAGE']))

    res = signService.get_all(page, per_page);

    return jsonify(res);


@signBp.post("")
def store_route():
    inputs = SignInputs(request)

    if not inputs.validate():
        return jsonify(success=False, errors=inputs.errors)

    data = request.form
    file = request.files['file'] if 'file' in request.files else None

    res = signService.make_sign(data, file)

    return jsonify(res)

