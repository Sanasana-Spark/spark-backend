from flask import (
    Blueprint,  jsonify, request, g
)
from werkzeug.utils import secure_filename
import os
from .. import db
from flask_restful import Api, Resource
from sanasana.query import trips as qtrip
from sanasana.query import assets as qasset
from sanasana.query import fuel as qfuel_request
from sanasana.query.fuel import Fuel_request
from sanasana import models



bp = Blueprint('fuel', __name__, url_prefix='/fuel')
api_fuel = Api(bp)

UPLOAD_FOLDER = '/sanasana/upload'  # Change this to your desired upload directory
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


class AllFuelRequest(Resource):
    def get(self):
        data = [fuel_request.as_dict() for fuel_request in qfuel_request.get_fuel_request_by_org(g.current_user.organization_id)]
        return jsonify(data)


class FuelRequest(Resource):
    def post(self, trip_id):
        data = request.get_json()
        trip = qtrip.get_trip_by_id(trip_id).as_dict()

        cost_per_litre = qfuel_request.get_fuel_price(g.current_user.organization_id, trip['a_fuel_type'])
        estimated_litres, estimated_cost = qfuel_request.calculate_f_litres(
            g.current_user.organization_id, trip_id)
        request_data = {
            "f_created_by": g.current_user.id,
            "f_organization_id": g.current_user.organization_id,
            "f_trip_id": trip_id,
            "f_asset_id": trip['t_asset_id'],
            "f_operator_id": trip['t_operator_id'],
            "f_estimated_litres": estimated_litres,
            "f_litres": None,
            "f_estimated_cost": estimated_cost,
            "f_cost": cost_per_litre,
            "f_total_cost": None,
            "f_distance": trip['t_distance'],
            "f_type": trip['a_fuel_type'],
            "f_request_type": data["f_request_type"],
            }
        result = qfuel_request.add(request_data)
        fuel_result = result.as_dict()
        qtrip.update_status(trip_id, "Requested")
        return jsonify(fuel_result=fuel_result)
    

class CarbonEmissionCalculator(Resource):
    def get(self):
        distance_km = request.args.get('distance_km')
        fuel_type = request.args.get('fuel_type')
        fuel_amount_litres = request.args.get('fuel_amount_litres')
        efficiency_rate = request.args.get('efficiency_rate')

        if efficiency_rate and fuel_type:
            t_carbon_emission = qfuel_request.calculate_carbon_emission_efficiency_based(distance_km, efficiency_rate, fuel_type)
        elif fuel_amount_litres:
            t_carbon_emission = qfuel_request.calculate_carbon_emission(fuel_type, fuel_amount_litres)
        else:
            t_carbon_emission = 0.0

        return jsonify({"t_carbon_emission": t_carbon_emission})


api_fuel.add_resource(AllFuelRequest, '/')
api_fuel.add_resource(FuelRequest, '/<trip_id>/')
api_fuel.add_resource(CarbonEmissionCalculator, '/carbon-emission-calculator/')
