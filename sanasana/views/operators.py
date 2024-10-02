from flask import (
    Blueprint,  jsonify, request
)
from werkzeug.utils import secure_filename
import os
from .. import db
from flask_restful import Api, Resource
from sanasana.models.operators import Operator, Ostatus
from sanasana.models import operators as qoperator

bp = Blueprint('operators', __name__, url_prefix='/operators')
api_operators = Api(bp)


class AllOperators(Resource):
    def get(self, org_id, user_id):
        data = [operator.as_dict() for operator in qoperator.get_operator_by_org(org_id)]
        return jsonify(data)
    

class OperatorById(Resource):
    def get(self, org_id, user_id, id):
        data = qoperator.get_operator_by_id(org_id, id).as_dict()
        return jsonify(data)


api_operators.add_resource(AllOperators, '/<org_id>/<user_id>/')
api_operators.add_resource(OperatorById, '/<org_id>/<user_id>/<id>')


def get_operator_column(operator_id, column_name):
    operator = Operator.query.get(operator_id)
    return getattr(operator, column_name, None) if operator else None


@bp.route('/status')
def get_operator_status():
    operator_status = Ostatus.query.all()
    status_list = [status.as_dict() for status in operator_status]
    return jsonify(status_list)


@bp.route('/create', methods=['POST'])
def add_operator():
    try:
        data = request.json
        files = request.files

        required_fields = [
            'o_organisation_id', 'o_created_by', 'o_name', 'o_national_id'
        ]
        data = {k.strip().lower(): v for k, v in data.items()}
        required_fields_normalized = [field.lower() for field in required_fields]
        missing_fields = [field for field in required_fields_normalized if field not in data]

        if missing_fields:
            return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

        new_operator = Operator(
            o_organisation_id=data.get('o_organisation_id', ''),
            o_created_by=data.get('o_created_by', ''),
            o_name=data.get('o_name', ''),
            o_email=data.get('o_email'),
            o_phone=data.get('o_phone',),
            o_national_id=data.get('o_national_id'),
            o_lincense_id=data.get('o_lincense_id'),
            o_lincense_type=data.get('o_lincense_type'),
            o_lincense_expiry=data.get('o_lincense_expiry'),
            o_payment_card_id=data.get('o_payment_card_id'),
            o_Payment_card_no=data.get('o_Payment_card_no') ,
            o_role=data.get('o_role', ''),
            o_status=data.get('o_status', ''),
            o_cum_mileage=float(data.get('o_cum_mileage', 0)),
            o_expirence=float(data.get('o_expirence', 0)),
            o_assigned_asset=data.get('o_assigned_asset')
        )

        if 'o_image' in files:
            image_file = files['o_image']
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join('images/assets', image_filename)
            image_file.save(image_path)
            new_operator.o_image = image_path

        for attachment in ['a_attachment1', 'a_attachment2', 'a_attachment3']:
            if attachment in files:
                file = files[attachment]
                filename = secure_filename(file.filename)
                file_path = os.path.join('images/assets', filename)
                file.save(file_path)
                setattr(new_operator, attachment, file_path)

        db.session.add(new_operator)
        db.session.commit()

        return jsonify(new_operator.as_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
