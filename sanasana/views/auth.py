from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for,
    jsonify, json
)
from .db import get_db
from flask_login import (
    LoginManager,
    login_required,
    login_user,
    logout_user,
    current_user
)

auth_bp = Blueprint('auth', __name__)
login_manager = LoginManager()


# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return user_id

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.index"))


@auth_bp.route("/")
def index():
    db = get_db()
    cursor = db.cursor()

    unitcode = request.args.get('u_id')

    query = None
    wo_data = None

    if unitcode:
        query = (
             'SELECT * FROM maintenance.units,maintenance.leases,maintenance.properties'
             ' WHERE l_u_id=units.u_id and u_p_id=p_id and u_id = %s'
            )
    if query:
        cursor.execute(query, (unitcode, ))
        row = cursor.fetchone()
        if row:
            columns = [col[0] for col in cursor.description]
            wo_data = dict(zip(columns, row))
        db.close()
    return jsonify(wo_data)