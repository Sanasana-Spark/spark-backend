from flask import (
    Blueprint,  jsonify, request
)
from werkzeug.utils import secure_filename
import os
from .. import db
from sanasana.models.assets import Asset

bp = Blueprint('assets', __name__, url_prefix='/assets')


@bp.route('/')
def get_assets():
    assets = Asset.query.all()
    assets_list = [asset.as_dict() for asset in assets]
    return jsonify(assets_list)


@bp.route('/create', methods=['POST'])
def add_asset():
    try:
        data = request.form.to_dict()
        files = request.files

        required_fields = [
            'a_name', 'a_make', 'a_model', 'a_year', 'a_license_plate',
            'a_type', 'a_engine_size', 'a_tank_size', 'a_fuel_type', 'a_cost',
            'a_value', 'a_status',  'a_efficiency_rate'
        ]

        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

        new_asset = Asset(
            a_name=data['a_name'],
            a_make=data['a_make'],
            a_model=data['a_model'],
            a_year=int(data['a_year']),
            a_license_plate=data['a_license_plate'],
            a_type=data['a_type'],
            a_msrp=float(data['a_msrp']),
            a_chasis_no=data['a_chasis_no'],
            a_engine_size=float(data['a_engine_size']),
            a_tank_size=float(data['a_tank_size']),
            a_efficiency_rate=float(data['a_efficiency_rate']),
            a_fuel_type=data['a_fuel_type'],
            a_cost=float(data['a_cost']),
            a_value=float(data['a_value']),
            a_depreciation_rate=float(data['a_depreciation_rate']),
            a_apreciation_rate=float(data['a_apreciation_rate']),
            a_accumulated_dep=float(data['a_accumulated_dep']),
            a_status=data['a_status'],
            a_owner_id=int(data['a_owner_id'])
        )

        if 'a_image' in files:
            image_file = files['a_image']
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join('images/assets', image_filename)
            image_file.save(image_path)
            new_asset.a_image = image_path

        for attachment in ['a_attachment1', 'a_attachment2', 'a_attachment3']:
            if attachment in files:
                file = files[attachment]
                filename = secure_filename(file.filename)
                file_path = os.path.join('images/assets', filename)
                file.save(file_path)
                setattr(new_asset, attachment, file_path)

        db.session.add(new_asset)
        db.session.commit()

        return jsonify(new_asset.as_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
