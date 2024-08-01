from flask import (
    Blueprint,  jsonify, request
)
from werkzeug.utils import secure_filename
import os
from .. import db
from sanasana.models.fuel import Fuel_request
from .assets import get_asset_column
from .trips import get_trip_column

bp = Blueprint('fuel', __name__, url_prefix='/fuel')


@bp.route('/')
def get_fuel_request():
    fuel_requests = Fuel_request.query.all()
    data = [fuel_request.as_dict() for fuel_request in fuel_requests]
    return jsonify(data)


def calculate_f_litres(distance, efficiency_rate, load):
    # Assuming a simple calculation where fuel consumption might be affected by the load
    base_consumption = distance * efficiency_rate
    additional_consumption = load * 0.1  # Example: 10% more consumption per unit load
    return base_consumption + additional_consumption


def get_fuel_price(f_type):
    if f_type == "Petrol":
        fuel_price = 200
    else:
        fuel_price = 180
    # fuel_price = FuelPrice.query.filter_by(f_type=f_type).first()
    # return fuel_price.price if fuel_price else None
    return fuel_price if fuel_price else None


@bp.route('/create', methods=['POST'])
def add_fuel_request():
    try:
        data = request.json
        files = request.files

        required_fields = [
            'f_created_by', 'f_organization_id', 'f_operator_id', 'f_asset_id',
            'f_trip_id'
        ]
        data = {k.strip().lower(): v for k, v in data.items()}
        required_fields_normalized = [field.lower() for field in required_fields]
        missing_fields = [field for field in required_fields_normalized if field not in data]

        if missing_fields:
            return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

        f_asset_id = data.get('f_asset_id')
        f_trip_id = data.get('f_trip_id')
        f_distance = get_trip_column(f_trip_id, 't_distance')
        f_load = get_trip_column(f_trip_id, 't_load')

        # Retrieve necessary details for calculations
        f_efficiency_rate = get_asset_column(f_asset_id, 'a_efficiency_rate')
        f_type = get_asset_column(f_asset_id, 'a_fuel_type')
        if not f_type:
            return jsonify({"error": "Invalid asset id or asset does not have fuel type defined"}), 400

        f_cost = get_fuel_price(f_type)
        if f_cost is None:
            return jsonify({"error": f"Fuel price not found for type: {f_type}"}), 400

        f_litres = calculate_f_litres(f_distance, f_efficiency_rate, f_load)
        f_total_cost = f_litres * f_cost

        new_fuel_request = Fuel_request(
            f_organization_id=data.get('f_organization_id', ''),
            f_created_by=data.get('f_created_by', ''),
            f_operator_id=data.get('f_operator_id', ''),
            f_asset_id=f_asset_id,
            f_trip_id=data.get('f_trip_id'),
            f_card_id=data.get('f_card_id'),
            f_type=f_type,
            f_litres=f_litres,
            f_cost=f_cost,
            f_total_cost=f_total_cost,
            f_distance=f_distance,
            f_vendor=data.get('f_vendor', 'Total')
        )

        if 'f_odometer_image' in files:
            image_file = files['f_odometer_image']
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join('images/assets', image_filename)
            image_file.save(image_path)
            new_fuel_request.f_odometer_image = image_path

        if 'f_receipt_image' in files:
            image_file = files['f_receipt_image']
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join('images/assets', image_filename)
            image_file.save(image_path)
            new_fuel_request.f_receipt_image = image_path

        for attachment in ['f_receipt_pdf', 'a_attachment2', 'a_attachment3']:
            if attachment in files:
                file = files[attachment]
                filename = secure_filename(file.filename)
                file_path = os.path.join('images/assets', filename)
                file.save(file_path)
                setattr(new_fuel_request, attachment, file_path)

        db.session.add(new_fuel_request)
        db.session.commit()

        return jsonify(new_fuel_request.as_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


