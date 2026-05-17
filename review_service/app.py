from flask import Flask
from database import db, migrate
from shared.config import settings


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = settings.FLASK_DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate.init_app(app, db)

