"""This is init module."""

from flask import Flask
from app.middlewares.JWTMiddleware import JWTMiddleware

# Place where app is defined
app = Flask(__name__)

app.wsgi_app = JWTMiddleware(app.wsgi_app)

from app.route import main
