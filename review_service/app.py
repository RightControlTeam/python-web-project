from os import environ
from flask import Flask
from database import db, migrate
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate.init_app(app, db)