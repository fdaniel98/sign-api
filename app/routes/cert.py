from flask import jsonify, Blueprint

from app.services import certService

certBp = Blueprint('cert', __name__, url_prefix='/cert')


@certBp.get("/")
def main_route():
    res = certService.get_all()
    return jsonify(res)


@certBp.post("/")
def post_route():
    res = certService.create_cert()
    return jsonify(res)

