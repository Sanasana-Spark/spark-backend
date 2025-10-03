from flask import Blueprint, jsonify, request, g
from flask_restful import Api, Resource
from sanasana.query import maintenances as qmaintenance
from sanasana.models import Maintenance

bp = Blueprint('maintenances', __name__, url_prefix='/maintenances/')
api_maintenance = Api(bp)


class MaintenanceByOrganization(Resource):
    def get(self):
        maintenances = qmaintenance.get_maintenance_by_organization(g.current_user.organization_id)
        maintenance_list = [maintenance.as_dict() for maintenance in maintenances]
        return jsonify(maintenance_list=maintenance_list)

    def post(self):
        data = request.get_json()
        data = {k.strip().lower(): v for k, v in data.items()}
        maintenance = Maintenance(
            m_created_by=g.current_user.id,
            m_organisation_id=g.current_user.organization_id,
            m_asset_id=data.get('m_asset_id'),
            m_type=data.get('m_type'),
            m_description=data.get('m_description'),
            m_date=data.get('m_date'),
            m_total_cost=data.get('m_total_cost'),
            m_insurance_coverage=data.get('m_insurance_coverage'),
            m_status=data.get('m_status'),
            m_estimated_cost=data.get('m_estimated_cost'),
        )
        file = data.get('m_attachment')
        result = qmaintenance.add_maintenance(maintenance, file=file)
        return jsonify(maintenance=result.as_dict())


class MaintenanceHistoryByOrganization(Resource):
    def get(self):
        maintenances = qmaintenance.get_maintenance_history_by_organization(g.current_user.organization_id)
        maintenance_list = [maintenance.as_dict() for maintenance in maintenances]
        return jsonify(maintenance_list=maintenance_list)


class MaintenanceByAsset(Resource):
    def get(self, asset_id):
        maintenances = qmaintenance.get_maintenance_by_asset(g.current_user.organization_id, asset_id)
        maintenance_list = [m.as_dict() for m in maintenances]
        return jsonify(maintenance_list=maintenance_list)


class MaintenanceById(Resource):
    def put(self, maintenance_id):
        data = request.form.to_dict()
        data = {k.strip().lower(): v for k, v in data.items()}
        file = request.files.get('m_attachment')  # optional

        result = qmaintenance.edit_maintenance(maintenance_id, data, file=file)
        if not result:
            return jsonify(error="Maintenance record not found"), 404
        return jsonify(maintenance=result.as_dict())

    def delete(self, maintenance_id):
        result = qmaintenance.delete_maintenance(maintenance_id)
        if not result:
            return jsonify(error="Maintenance record not found"), 404
        return jsonify(message="Maintenance record deleted successfully")


# Register resources
api_maintenance.add_resource(MaintenanceByOrganization, '/')
api_maintenance.add_resource(MaintenanceHistoryByOrganization, '/history/')
api_maintenance.add_resource(MaintenanceByAsset, '/by-asset/')
api_maintenance.add_resource(MaintenanceById, '/<maintenance_id>/')

