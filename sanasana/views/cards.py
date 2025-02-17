from flask import (
    Blueprint,  jsonify, request
)
from werkzeug.utils import secure_filename
import os
from .. import db
from sanasana.models import Card

bp = Blueprint('cards', __name__, url_prefix='/cards')


@bp.route('/')
def get_cards():
    cards = Card.query.all()
    data = [card.as_dict() for card in cards]
    return jsonify(data)


@bp.route('/create', methods=['POST'])
def add_card():
    try:
        data = request.json
        files = request.files

        required_fields = [
            'c_organization_id', 'c_created_by', 'c_number'
        ]
        data = {k.strip().lower(): v for k, v in data.items()}
        required_fields_normalized = [field.lower() for field in required_fields]
        missing_fields = [field for field in required_fields_normalized if field not in data]

        if missing_fields:
            return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

        new_card = Card(
            c_organization_id=data.get('c_organization_id'),
            c_created_by=data.get('c_created_by', ''),
            c_assign_by=data.get('c_assign_by', ''),
            c_assigned_at=data.get('c_assigned_at'),
            c_assigned_to=data.get('c_assigned_to',),
            c_attached_asset=data.get('c_attached_asset'),
            c_number=data.get('c_number'),
            c_expiry_date=data.get('c_expiry_date')
        )

        for attachment in ['a_attachment1', 'a_attachment2', 'a_attachment3']:
            if attachment in files:
                file = files[attachment]
                filename = secure_filename(file.filename)
                file_path = os.path.join('images/assets', filename)
                file.save(file_path)
                setattr(new_card, attachment, file_path)

        db.session.add(new_card)
        db.session.commit()

        return jsonify(new_card.as_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
