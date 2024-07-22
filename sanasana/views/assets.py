from flask import (
    Blueprint,  jsonify, request
)
from werkzeug.utils import secure_filename
import os
from .. import db
from sanasana.models.assets import Asset, Status

bp = Blueprint('assets', __name__, url_prefix='/assets')


@bp.route('/')
def get_assets():
    assets = Asset.query.all()
    assets_list = [asset.as_dict() for asset in assets]
    return jsonify(assets_list)

@bp.route('/<assetId>', methods=['GET'])
def get_asset(assetId):
    asset = Asset.query(Asset).filter(Asset.id == assetId).first()
    return jsonify(asset)


@bp.route('/status')
def get_assets_status():
    assets_status = Status.query.all()
    status_list = [status.as_dict() for status in assets_status]
    return jsonify(status_list)


@bp.route('/create', methods=['POST'])
def add_asset():
    try:
        data = request.json
        files = request.files

        required_fields = [
            "a_name", 'a_make', 'a_model', 'a_year', 'a_license_plate',
             'a_engine_size', 'a_tank_size', 'a_fuel_type', 'a_cost',
            'a_value', 'a_status',  'a_efficiency_rate', 'a_created_by',
            'a_organisation_id'
        ]
        data = {k.strip().lower(): v for k, v in data.items()}
        required_fields_normalized = [field.lower() for field in required_fields]
        missing_fields = [field for field in required_fields_normalized if field not in data]

        if missing_fields:
            return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

        new_asset = Asset(
            a_name=data.get('a_name', ''),
            a_make=data.get('a_make', ''),
            a_model=data.get('a_model', ''),
            a_year=int(data.get('a_year', 0)),
            a_license_plate=data.get('a_license_plate', ''),
            a_type=data.get('a_type', ''),        
            a_chasis_no=data.get('a_chasis_no', ''),
            a_msrp=float(data.get('a_msrp', 0)),
            a_engine_size=float(data.get('a_engine_size', 0)),
            a_tank_size=float(data.get('a_tank_size', 0)),
            a_efficiency_rate=float(data.get('a_efficiency_rate', 0)),
            a_fuel_type=data.get('a_fuel_type', ''),
            a_cost=float(data.get('a_cost', 0)),
            a_value=float(data.get('a_value', 0)),
            a_depreciation_rate=float(data.get('a_depreciation_rate', 0)),
            a_apreciation_rate=float(data.get('a_apreciation_rate', 0)),
            a_accumulated_dep=float(data.get('a_accumulated_dep', 0)),
            a_status=data.get('a_status', ''),
            a_created_by=data.get('a_created_by', ''),
            a_organisation_id=data.get('a_organisation_id', '')
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
