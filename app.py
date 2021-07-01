from app import app
from dotenv import dotenv_values

config = dotenv_values(".env")

if __name__ == '__main__':
    # Running app in debug mode
    app.run(debug=bool(config['DEBUG']))