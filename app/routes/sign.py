import os

from flask import request, send_file

from app import app
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

    path = signService.make_sign(data, file)
    full_path = os.path.join(os.path.dirname(app.instance_path), path)

    return send_file(path_or_file=full_path,
                     mimetype=file.mimetype,
                     attachment_filename='test.pdf',
                     as_attachment=True)

