from flask import Blueprint

from app.routes.cert import certBp
from app.routes.sign import signBp


v1 = Blueprint('v1', __name__, url_prefix='/v1')
v1.register_blueprint(signBp)
v1.register_blueprint(certBp)
# >>>> ALL OTHERS ROUTES
