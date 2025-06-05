from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_mail import Mail
import ssl


db = SQLAlchemy()
migrate = Migrate()
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    register_blueprints(app)

    return app


def register_blueprints(app):
    from .views import (
        assets,
        operators,
        users,
        trips,
        cards,
        fuel,
        summaries,
        clients,
        maintenances
    )

    app.register_blueprint(assets.bp)
    app.register_blueprint(operators.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(trips.bp)
    app.register_blueprint(cards.bp)
    app.register_blueprint(fuel.bp)
    app.register_blueprint(summaries.bp)
    app.register_blueprint(clients.bp)
    app.register_blueprint(maintenances.bp)
