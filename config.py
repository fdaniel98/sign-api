"""This module is to configure app to connect with database."""

from os.path import join, dirname
from pymongo import MongoClient
from dotenv import dotenv_values

config = dotenv_values(".env")

DEBUG = config['DEBUG']
URL = config['MONGO_DB']

MongoClient = MongoClient(URL)
SignsDatabase = MongoClient.dsignature.signs
CertsDatabase = MongoClient.dsignature.certs
