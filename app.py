from app import app
from dotenv import dotenv_values
from app.routes import v1

config = dotenv_values(".env")

app.register_blueprint(v1)

if __name__ == '__main__':
    # Running app in debug mode
    app.run(debug=bool(config['DEBUG']))