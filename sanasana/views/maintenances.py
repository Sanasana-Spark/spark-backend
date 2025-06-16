from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource
from sanasana.query import maintenances as qmaintenance

bp = Blueprint('maintenances', __name__, url_prefix='/maintenances/')
api_maintenance = Api(bp)


class MaintenanceByOrganization(Resource):
    def get(self, org_id, user_id):
        maintenances = qmaintenance.get_maintenance_by_organization(org_id)
        maintenance_list = [maintenance.as_dict() for maintenance in maintenances]
        return jsonify(maintenance_list=maintenance_list)

    def post(self, org_id, user_id):
        data = request.form.to_dict()
        data = {k.strip().lower(): v for k, v in data.items()}
        data["m_created_by"] = user_id
        data["m_organisation_id"]=org_id
        file = request.files.get('m_attachment')  # optional
        result = qmaintenance.add_maintenance(data, file=file)
        return jsonify(maintenance=result.as_dict())


class MaintenanceByAsset(Resource):
    def get(self, org_id, user_id, asset_id):
        maintenances = qmaintenance.get_maintenance_by_asset(org_id, asset_id)
        maintenance_list = [m.as_dict() for m in maintenances]
        return jsonify(maintenance_list=maintenance_list)


class MaintenanceById(Resource):
    def put(self, org_id, user_id, maintenance_id):
        data = request.form.to_dict()
        data = {k.strip().lower(): v for k, v in data.items()}
        file = request.files.get('m_attachment')  # optional

        result = qmaintenance.edit_maintenance(maintenance_id, data, file=file)
        if not result:
            return jsonify(error="Maintenance record not found"), 404
        return jsonify(maintenance=result.as_dict())

    def delete(self, org_id, user_id, maintenance_id):
        result = qmaintenance.delete_maintenance(maintenance_id)
        if not result:
            return jsonify(error="Maintenance record not found"), 404
        return jsonify(message="Maintenance record deleted successfully")



# Register resources
api_maintenance.add_resource(MaintenanceByOrganization, '/<org_id>/<user_id>/')
api_maintenance.add_resource(MaintenanceByAsset, '/by-asset/<org_id>/<user_id>/<asset_id>/')
api_maintenance.add_resource(MaintenanceById, '/<org_id>/<user_id>/<maintenance_id>/')
