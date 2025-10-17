from flask import (
    Blueprint,  jsonify, request, g
)
from werkzeug.utils import secure_filename
import os
from .. import db
from sanasana.query import trips as qtrip
from sanasana.query import assets as qasset
from sanasana.query import operators as qoperator
from sanasana.query import fuel as qfuel_request
from sanasana.query.fuel import Fuel_request
from flask_restful import Api, Resource


bp = Blueprint('summaries', __name__, url_prefix='/summaries')
api_summaries = Api(bp)


class DashboardSummary(Resource):
    def get(self):
        org_id = g.current_user.organization_id
        totalAssets = qasset.get_asset_count_by_org(org_id)
        totalOperators = qoperator.get_operator_count_by_org(org_id)
        totalTrips = qtrip.get_recent_trips_count_by_org(org_id)
        overallAssetsValue = qasset.get_asset_value_sum_by_org(org_id)
        totalFuelCost = qfuel_request.get_fuel_cost_sum_by_org(org_id)
        carbonReduction = 0
        response = {
            "totalAssets": totalAssets if totalAssets is not None else 0,
            "totalOperators": totalOperators if totalOperators is not None else 0,
            "totalTrips": totalTrips if totalTrips is not None else 0,
            "overallAssetsValue": overallAssetsValue if overallAssetsValue is not None else 0,
            "totalFuelCost": totalFuelCost if totalFuelCost is not None else 0,
            "carbonReduction": carbonReduction
        }
        return response, 200
    

class TripCountByCategory(Resource):
    def get(self):
        org_id = g.current_user.organization_id
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        trips = qtrip.get_trips_count_by_category(
            org_id, start_date=start_date, end_date=end_date
            )
        return jsonify(trips)
    

class TripsExpenseByCategory(Resource):
    def get(self):
        org_id = g.current_user.organization_id
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        expense = qtrip.get_trips_expense_by_category(
            org_id, start_date=start_date, end_date=end_date
            )
        return jsonify(expense)

   
class TripsIncomeByCategory(Resource):
    def get(self):
        org_id = g.current_user.organization_id
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        income = qtrip.get_trips_income_by_category(
            org_id, start_date=start_date, end_date=end_date
            )
        return jsonify(income)


api_summaries.add_resource(DashboardSummary, '/')
api_summaries.add_resource(TripCountByCategory, '/trip-count-summary/')
api_summaries.add_resource(TripsExpenseByCategory, '/trip-expense-summary/')
api_summaries.add_resource(TripsIncomeByCategory, '/trip-income-summary/')