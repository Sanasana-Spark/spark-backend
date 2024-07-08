from flask import (
    Blueprint,  jsonify, request
)
from sanasana.views.db import get_db
from sanasana.models.assets import Asset

bp = Blueprint('assets', __name__, url_prefix='/assets')

@bp.route('/old')
def get_assetsss():
    assets = Asset.query.all()
    assets_list = [{'id': asset.id, 'name': asset.a_name} for asset in assets]  # Adjust based on your Asset model attributes
    return jsonify(assets_list)

@bp.route('/')
def get_assets():
    assets = Asset.query.all()
    assets_list = [asset.as_dict() for asset in assets]
    return jsonify(assets_list)


@bp.route('/create', methods=['POST'])
def create():
    if request.method == 'POST':
        data = request.json

        a_name = data.get('a_name')
        a_make = data.get('a_')
        a_model = data.get('a_')
        a_year = data.get('a_')
        a_license_plate = data.get('a_')
        a_type = data.get('a_')
        a_msrp = data.get('a_')
        a_chasis_no = data.get('a_')
        a_engine_size = data.get('a_')
        a_tank_size = data.get('a_')
        a_efficiency_rate = data.get('a_')
        a_fuel_type = data.get('a_')
        a_cost = data.get('a_')
        a_value = data.get('a_')
        a_depreciation_rate = data.get('a_')
        a_apreciation_rate = data.get('a_')
        a_accumulated_dep = data.get('a_')
        a_image = data.get('a_')
        a_attachment1 = data.get('a_')
        a_attachment2 = data.get('a_')
        a_attachment3 = data.get('a_')
        a_status = data.get('a_')


        error = None

        if not a_name:
            error = 'Asset name is required.'

        if error is not None:
            return jsonify({'error': error}), 400  # Return error response
        else:
            try:
                db = get_db()
                cursor = db.cursor()
                cursor.execute(
                    'INSERT INTO assets.assets (p_name, p_num_units,'
                    'p_manager_id, p_country, p_city, p_address, p_zipcode,'
                    ' p_state, p_latitude, p_longitude, p_elevation, p_f_id)'
                    ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    (p_name, p_num_units, p_manager_id, p_country,
                     p_city, p_address, p_zipcode, p_state, p_latitude,
                     p_longitude, p_elevation, p_f_id)
                )
                db.commit()
            except Exception as e:
                return jsonify({'error': str(e)}), 500  # Return error response
            finally:
                cursor.close()  # Close the cursor
                db.close()  # Close the database connection

        return jsonify({'message': 'Asset added successfully'}), 201

    return jsonify({'error': 'Method not allowed'}), 405
