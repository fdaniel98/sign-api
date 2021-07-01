"""This module is to configure app to connect with database."""

from os.path import join, dirname
from pymongo import MongoClient
from dotenv import load_dotenv
dotenv_path = join(dirname(__file__), '.env')  # Path to .env file
load_dotenv(dotenv_path)

DATABASE = MongoClient()['restfulapi'] # DB_NAME
DEBUG = True
client = MongoClient('localhost', 27017)