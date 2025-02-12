from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
app = Flask(__name__)
app.config.from_object(Config)
login = LoginManager(app)
login.login_view = 'login'  # Перенаправление на страницу логина
login.login_message = "Пожалуйста, войдите в систему."
db = SQLAlchemy(app)
migrate = Migrate(app, db)
from app import routes, models, forms, test_routes, signIN_and_UP, fridge, scan, shopping_list
