from flask import Flask, g, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_mail import Mail
import ssl

PUBLIC_ENDPOINTS = {"/assetsssssss", "/public-api"}
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    CORS(
        app,
        supports_credentials=True,
        resources={r"/*": {"origins": ["http://localhost:3000", "https://sanasana.netlify.app/", "https://sanasanapwa.netlify.app/"]}},  # your frontend
        expose_headers=["Authorization", "Content-Type"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]  # allow OPTIONS explicitly
        )
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)
    register_blueprints(app)
    mail.init_app(app)

    @app.before_request
    def load_current_user():
        if request.method == "OPTIONS":
            return None  # let Flask-CORS handle the preflight
     
        from .models import User
        from .query.user_management import verify_clerk_token

        if request.path in PUBLIC_ENDPOINTS:
            g.current_user = None
            return
        payload = verify_clerk_token()
        clerk_id = payload["sub"]
        g.current_user = User.query.filter_by(id=clerk_id).first()

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
        maintenances,
        reports,
        notifications
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
    app.register_blueprint(reports.bp)
    app.register_blueprint(notifications.bp)
