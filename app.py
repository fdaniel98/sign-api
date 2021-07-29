from flask import request, jsonify

from app import app
from dotenv import dotenv_values
from app.routes import v1
from app.validations.validations import ApiTokenValidation

config = dotenv_values(".env")
app.register_blueprint(v1)


@app.before_request
def before():
    inputs = ApiTokenValidation(request)

    if not inputs.validate():
        return jsonify(success=False, errors=inputs.errors), 403


if __name__ == '__main__':
    # Running app in debug mode
    app.run(debug=bool(config['DEBUG']))