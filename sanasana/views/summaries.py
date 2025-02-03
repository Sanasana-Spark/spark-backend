from flask import (
    Blueprint,  jsonify, request
)
from werkzeug.utils import secure_filename
import os
from .. import db
from sanasana.models import trips as qtrip
from sanasana.models import assets as qasset
from sanasana.models import fuel as qfuel_request
from sanasana.models.fuel import Fuel_request
from flask_restful import Api, Resource


bp = Blueprint('summaries', __name__, url_prefix='/summaries')
api_summaries = Api(bp)


class DashboardSummary(Resource):
    def get(self, org_id, user_id):
        totalAssets = qasset.get_asset_count_by_org(org_id)
        overallAssetsValue = qasset.get_asset_value_sum_by_org(org_id)
        totalFuelCost = qfuel_request.get_fuel_cost_sum_by_org(org_id)
        carbonReduction = 3
        response = {
            "totalAssets": totalAssets if totalAssets is not None else 0,
            "overallAssetsValue": overallAssetsValue if overallAssetsValue is not None else 0,
            "totalFuelCost": totalFuelCost if totalFuelCost is not None else 0,
            "carbonReduction": carbonReduction
        }
        return response, 200


api_summaries.add_resource(DashboardSummary, '/<org_id>/')