from flask import (
    Blueprint,  jsonify, request
)
from werkzeug.utils import secure_filename
import os
from .. import db
from sanasana.query import trips as qtrip
from sanasana.query import assets as qasset
from sanasana.query import fuel as qfuel_request
from sanasana.query.fuel import Fuel_request
from flask_restful import Api, Resource


bp = Blueprint('fuel', __name__, url_prefix='/fuel')
api_fuel = Api(bp)

UPLOAD_FOLDER = '/sanasana/upload'  # Change this to your desired upload directory
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


class AllFuelRequest(Resource):
    def get(self, org_id, user_id):
        data = [fuel_request.as_dict() for fuel_request in qfuel_request.get_fuel_request_by_org(org_id)]
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


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class FuelRequest(Resource):
    def post(self, org_id, user_id, trip_id):
        data = request.json
        trip_id = data["f_trip_id"]
        trip = qtrip.get_trip_by_id(trip_id)
        asset = qasset.get_asset_by_id(trip.t_asset_id)  
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        try:
            data = request.json
            trip_id = data["f_trip_id"]
            t_status = data["t_status"]

            # Handle the file upload (image)
            # if 'f_odometer_image' not in request.files:
            #     return jsonify({'error': 'No image file provided'}), 400
            
            file = request.files['f_odometer_image']
            
            # Check if the file is valid
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)  # Sanitize the file name
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)  # Save the file to the specified folder
                
                # Optionally, you can now store 'file_path' in the database or cloud storage as needed
            else:
                return jsonify({'error': 'Invalid file type. Only images are allowed.'}), 400

            f_distance = float(trip.t_distance if trip.t_distance else "1")
            f_load = trip.t_load
            # Retrieve necessary details for calculations
            f_type = asset.a_fuel_type
            f_efficiency_rate = asset.a_efficiency_rate
            f_cost = get_fuel_price(f_type)
            if f_cost is None:
                return jsonify({"error": f"Fuel price not found for type: {f_type}"}), 400
            f_litres = calculate_f_litres(f_distance, f_efficiency_rate, f_load)
            f_total_cost = f_litres * f_cost
            request_data = {
                "f_organization_id": trip.t_organization_id,
                "f_created_by": data["f_created_by"],
                "f_trip_id": trip_id,
                "f_asset_id": trip.t_asset_id,
                "f_operator_id": trip.t_operator_id,
                # "f_card_id": data.get("f_card_id") if "f_card_id" in data else None,
                "f_litres": f_litres,
                "f_cost": f_cost,
                "f_total_cost": f_total_cost,
                "f_distance": f_distance,
                "f_type": asset.a_fuel_type
            }
            result = qfuel_request.add(trip_id, request_data)
            # if result:
            #     t_status = "Requested"
            #     qtrip.update_status(trip_id, t_status)
            return jsonify(result), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500


api_fuel.add_resource(AllFuelRequest, '/<org_id>/<user_id>/')
api_fuel.add_resource(FuelRequest, '/<trip_id>/')


@bp.route('/create', methods=['POST'])
def post_fuel():
    trip_id = 3
    trip = qtrip.get_trip_by_id(trip_id)
 
    if not trip:
        return jsonify({'error': 'Trip not found'}), 404
    try:
        data = request.json

        trip_id = data.get("f_trip_id")
        t_status = data.get("t_status")

        # Handle the file upload (image)
        # if 'f_odometer_image' not in request.files:
        #     return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['f_odometer_image']
        
        # Check if the file is valid
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)  # Sanitize the file name
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)  # Save the file to the specified folder
            
            # Optionally, you can now store 'file_path' in the database or cloud storage as needed
        else:
            return jsonify({'error': 'Invalid file type. Only images are allowed.'}), 400

        f_distance = float(trip.t_distance if trip.t_distance else "1")
        f_load = trip.t_load
        # Retrieve necessary details for calculations
        asset = qasset.get_asset_by_id(trip.t_asset_id) 
        f_type = asset.a_fuel_type
        f_efficiency_rate = asset.a_efficiency_rate
        f_cost = get_fuel_price(f_type)
        if f_cost is None:
            return jsonify({"error": f"Fuel price not found for type: {f_type}"}), 400
        f_litres = calculate_f_litres(f_distance, f_efficiency_rate, f_load)
        f_total_cost = f_litres * f_cost
        new_fuel = Fuel_request(
            f_organization_id=trip.t_organization_id,
            f_created_by=data.get("f_created_by"),
            f_trip_id=trip_id,
            f_asset_id=trip.t_asset_id,
            f_operator_id=trip.t_operator_id,
            # "f_card_id": data.get("f_card_id") if "f_card_id" in data else None,
            f_litres=f_litres,
            f_cost=f_cost,
            f_total_cost=f_total_cost,
            f_distance=f_distance,
            f_type=asset.a_fuel_type
        )
        db.session.add(new_fuel)
        db.session.commit()
        # if result:
        # t_status = "Requested"
        # qtrip.update_status(trip_id, t_status)
        result = new_fuel.as_dict()
        return jsonify(**result), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500