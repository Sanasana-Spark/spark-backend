from flask import (
    Blueprint,  jsonify, request
)
from sanasana.views.db import get_db
from sanasana.models.operators import Operator

bp = Blueprint('operators', __name__, url_prefix='/operators')


@bp.route('/')
def get_assets():
    operators = Operator.query.all()
    data = [operator.as_dict() for operator in operators]
    return jsonify(data)