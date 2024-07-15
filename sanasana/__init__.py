from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    register_blueprints(app)
    
    return app


def register_blueprints(app):
    from .views import assets, operators, users
    app.register_blueprint(assets.bp)
    app.register_blueprint(operators.bp)
    app.register_blueprint(users.bp)

