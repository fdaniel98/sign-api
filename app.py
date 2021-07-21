from app import app
from dotenv import dotenv_values
from app.route.sign import signBp

config = dotenv_values(".env")

app.register_blueprint(signBp, url_prefix='/v1/sign')

if __name__ == '__main__':
    # Running app in debug mode
    app.run(debug=bool(config['DEBUG']))