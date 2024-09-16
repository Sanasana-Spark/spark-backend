from flask import (
    Blueprint,  jsonify, request
)
from werkzeug.utils import secure_filename
import os
from .. import db
from sanasana.models.fuel import Fuel_request
from sanasana.models import trips as qtrip
from sanasana.models import assets as qasset
from sanasana.models import fuel as qfuel_request
from flask_restful import Api, Resource

from .assets import get_asset_column
from .trips import get_trip_column

bp = Blueprint('fuel', __name__, url_prefix='/fuel')
api_fuel = Api(bp)


class AllFuelRequest(Resource):
    def get(self):
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


class FuelRequest(Resource):
    def post(self, trip_id):
        trip = qtrip.get_trip_by_id(trip_id)
        asset = qasset.get_asset_by_id(trip.t_asset_id)  
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        try:
            data = request.json
            trip_id = data["f_trip_id"]
            t_status = data["t_status"]
            # return jsonify(trip.as_dict()), 200
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
            data = {
                "f_organization_id": trip.t_organization_id,
                "f_created_by": data["f_created_by"],
                "f_trip_id": trip_id,
                "f_asset_id": trip.t_asset_id,
                "f_operator_id": trip.t_operator_id,
                "f_card_id": data["f_card_id"]if "f_card_id" in data else None,
                "f_litres": f_litres,
                "f_cost": f_cost,
                "f_total_cost": f_total_cost,
                "f_distance": f_distance,
                "f_type": asset.a_fuel_type
            }
            result = qfuel_request.add(trip_id, data)
            if result:
                t_status = "Requested"
                qtrip.update_status(trip_id, t_status)
            return jsonify(result.as_dict())
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500


api_fuel.add_resource(AllFuelRequest, '/')
api_fuel.add_resource(FuelRequest, '/<trip_id>/')