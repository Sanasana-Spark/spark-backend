from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource
from sanasana.query import maintenances as qmaintenance
from sanasana.models import Maintenance

bp = Blueprint('maintenances', __name__, url_prefix='/maintenances')
api_maintenance = Api(bp)

class MaintenanceByOrganization(Resource):
    def get(self, org_id):
        maintenances = qmaintenance.get_maintenance_by_organization(org_id)
        maintenance_list = [m.as_dict() for m in maintenances]
        return jsonify(maintenance_list)

class MaintenanceByAsset(Resource):
    def get(self, asset_id):
        maintenances = qmaintenance.get_maintenance_by_asset(asset_id)
        maintenance_list = [m.as_dict() for m in maintenances]
        return jsonify(maintenance_list)

class Maintenance(Resource):
    def post(self, org_id, user_id):
        data = request.get_json()
        data = {k.strip().lower(): v for k, v in data.items()}
        data["m_created_by"] = user_id

        result = qmaintenance.add_maintenance(data)
        return jsonify(maintenance=result.as_dict())

class MaintenanceById(Resource):
    def put(self, org_id, user_id, maintenance_id):
        data = request.get_json()
        data = {k.strip().lower(): v for k, v in data.items()}

        result = qmaintenance.edit_maintenance(maintenance_id, data)
        if not result:
            return jsonify(error="Maintenance record not found"), 404

        return jsonify(maintenance=result.as_dict())

# Register resources
api_maintenance.add_resource(MaintenanceByOrganization, '/org/<org_id>/')
api_maintenance.add_resource(MaintenanceByAsset, '/asset/<asset_id>/')
api_maintenance.add_resource(Maintenance, '/<org_id>/<user_id>/')
api_maintenance.add_resource(MaintenanceById, '/maintenance/<org_id>/<user_id>/<maintenance_id>/')
