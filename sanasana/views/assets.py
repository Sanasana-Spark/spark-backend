from flask import (
    Blueprint,  jsonify, request
)
from flask_restful import Api, Resource
from sqlalchemy import func, and_, cast, Numeric
from werkzeug.utils import secure_filename
import os
from .. import db
from sanasana.query import assets as qasset
from sanasana.models import Status, Asset, Trip
from sanasana import models

bp = Blueprint('assets', __name__, url_prefix='/assets')

api_assets = Api(bp)


class Assets(Resource):
    def get(self, org_id, user_id):
        assets = [asset.as_dict() for asset in qasset.get_asset_by_org(org_id)]
        return jsonify(assets)
    
    def post(self, org_id, user_id):
        data = request.get_json()
        # files = request.files

        # required_fields = [
        #     "a_name", 'a_make', 'a_model', 'a_year', 'a_license_plate',
        #      'a_fuel_type'
        # ]
        data = {k.strip().lower(): v for k, v in data.items()}
        # required_fields_normalized = [field.lower() for field in required_fields]
        # missing_fields = [field for field in required_fields_normalized if field not in data]

        # if missing_fields:
        #     return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

        data = {
            "a_created_by": user_id,
            "a_organisation_id": org_id,
            "a_make": data["a_make"],
            "a_model": data["a_model"],
            "a_year": data["a_year"],
            "a_license_plate": data["a_license_plate"],
            "a_fuel_type": data["a_fuel_type"],
            "a_tank_size": data["a_tank_size"],
            "a_displacement": data["a_displacement"],
            "a_mileage": data["a_mileage"],
            "a_horsepower": data["a_horsepower"],
            "a_acceleration": data["a_acceleration"],
            "a_insurance_expiry": data["a_insurance_expiry"],
            "a_status": data["a_status"]
        }
        result = qasset.add_asset(data)
        asset = result.as_dict()
        return jsonify(asset=asset)

#To Fix
                # a_type=data.get('a_type', ''),        
                # a_chasis_no=data.get('a_chasis_no', ''),
                # a_msrp=float(data.get('a_msrp', 0)),
                # a_engine_size=float(data.get('a_engine_size', 0)),
                # a_efficiency_rate=float(data.get('a_efficiency_rate', 0)),
                # a_cost=float(data.get('a_cost', 0)),
                # a_value=float(data.get('a_value', 0)),
                # a_depreciation_rate=float(data.get('a_depreciation_rate', 0)),
                # a_apreciation_rate=float(data.get('a_apreciation_rate', 0)),
                # a_accumulated_dep=float(data.get('a_accumulated_dep', 0)),
                # a_status=data.get('a_status', ''),
                # a_attached_card=data.get('a_attached_card')

            # if 'a_image' in files:
            #     image_file = files['a_image']
            #     image_filename = secure_filename(image_file.filename)
            #     image_path = os.path.join('images/assets', image_filename)
            #     image_file.save(image_path)
            #     new_asset.a_image = image_path

            # for attachment in ['a_attachment1', 'a_attachment2', 'a_attachment3']:
            #     if attachment in files:
            #         file = files[attachment]
            #         filename = secure_filename(file.filename)
            #         file_path = os.path.join('images/assets', filename)
            #         file.save(file_path)
            #         setattr(new_asset, attachment, file_path)


class AssetById(Resource):
    def get(self, org_id, user_id, id):
        assets = qasset.get_asset_by_id(org_id, id).as_dict()
        return jsonify(assets)
    

class AssetStatus(Resource):
    def get(self):
        statuses = Status.query.all()
        status_list = [status.as_dict() for status in statuses]
        return jsonify(status_list)

    def post(self):
        data = request.get_json()
        data = {
            "s_name": data["s_name"],
            "s_name_code": data["s_name_code"] 
            }
        result = qasset.add_status(data)
        status = result.as_dict()
        return jsonify(status=status)
    

class FleetPerformance(Resource):
    def get(self, org_id):
         # Get query parameters for date filtering
        start_date = request.args.get("start_date")  # Format: 'YYYY-MM-DD'
        end_date = request.args.get("end_date")  # Format: 'YYYY-MM-DD'

        assets = (
            db.session.query(
                Asset.id.label("id"),
                Asset.a_license_plate.label("a_license_plate"),
                Asset.a_make.label("a_make"),
                Asset.a_model.label("a_model"),
                Asset.a_year.label("a_year"),
                Asset.a_efficiency_rate.label("a_efficiency_rate"),
                func.count(Trip.id).label("trip_count"),
                func.sum(
                    cast(
                        func.regexp_replace(Trip.t_distance, '[^0-9.]', '', 'g'),  # Remove non-numeric characters
                        Numeric
                    )).label("total_miles"),  # Cast t_distance to Numeric
                func.sum(Trip.t_actual_fuel).label("total_fuel"),
                func.sum(Trip.t_actual_cost).label("total_cost"),

            )
            .filter(Asset.a_organisation_id == org_id)
            .join(Trip, Asset.id == Trip.t_asset_id)
            .group_by(Asset.id) 
            .order_by(func.sum(cast(func.regexp_replace(Trip.t_distance, '[^0-9.]', '', 'g'), Numeric)).desc())
        )
           # Apply date filtering if both start_date and end_date are provided
        if start_date and end_date:
            query = assets.filter(
                and_(
                    func.date(Trip.t_start_date) >= start_date,
                    func.date(Trip.t_start_date) <= end_date,
                )
            )

        results = query.all()
        # Convert query results to JSON
        fleet_data = [
            {
                "id": row.id,
                "a_license_plate": row.a_license_plate,
                "a_make": row.a_make,
                "a_model": row.a_model,
                "a_year": row.a_year,
                "a_efficiency_rate": row.a_efficiency_rate,
                "trip_count": row.trip_count,
                "total_miles": row.total_miles,
                "total_fuel": row.total_fuel,
                "total_cost": row.total_cost,
            }
            for row in results
        ]

        return jsonify(fleet_data=fleet_data)    


class AssetsReport(Resource):
    def get(self, org_id):
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = models.Asset.query.filter_by(a_organisation_id=org_id)

        if start_date and end_date:
            query = query.filter(models.Asset.a_created_at.between(start_date, end_date))

        assets = query.all()
        return jsonify([asset.as_dict() for asset in assets])


api_assets.add_resource(Assets, '/<org_id>/<user_id>/')
api_assets.add_resource(AssetById, '/<org_id>/<user_id>/<id>')
api_assets.add_resource(AssetStatus, '/status')
api_assets.add_resource(AssetsReport, '/reports/<org_id>/')
api_assets.add_resource(FleetPerformance, '/fleet_performance/<org_id>/')

@bp.route('/')
def get_assets():
    assets = Asset.query.all()
    assets_list = [asset.as_dict() for asset in assets]
    return jsonify(assets_list)

@bp.route('/<assetId>', methods=['GET'])
def get_asset(assetId):
    asset = Asset.query(Asset).filter(Asset.id == assetId).first()
    return jsonify(asset)


@bp.route('/status')
def get_assets_status():
    assets_status = Status.query.all()
    status_list = [status.as_dict() for status in assets_status]
    return jsonify(status_list)


def get_asset_column(asset_id, column_name):
    asset = Asset.query.get(asset_id)
    return getattr(asset, column_name, None) if asset else None


@bp.route('/create', methods=['POST'])
def add_asset():
    try:
        data = request.json
        files = request.files

        required_fields = [
            "a_name", 'a_make', 'a_model', 'a_year', 'a_license_plate',
             'a_engine_size', 'a_tank_size', 'a_fuel_type', 'a_cost',
            'a_value', 'a_status',  'a_efficiency_rate', 'a_created_by',
            'a_organisation_id'
        ]
        data = {k.strip().lower(): v for k, v in data.items()}
        required_fields_normalized = [field.lower() for field in required_fields]
        missing_fields = [field for field in required_fields_normalized if field not in data]

        if missing_fields:
            return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

        new_asset = Asset(
            a_name=data.get('a_name', ''),
            a_make=data.get('a_make', ''),
            a_model=data.get('a_model', ''),
            a_year=int(data.get('a_year', 0)),
            a_license_plate=data.get('a_license_plate', ''),
            a_type=data.get('a_type', ''),        
            a_chasis_no=data.get('a_chasis_no', ''),
            a_msrp=float(data.get('a_msrp', 0)),
            a_engine_size=float(data.get('a_engine_size', 0)),
            a_tank_size=float(data.get('a_tank_size', 0)),
            a_efficiency_rate=float(data.get('a_efficiency_rate', 0)),
            a_fuel_type=data.get('a_fuel_type', ''),
            a_cost=float(data.get('a_cost', 0)),
            a_value=float(data.get('a_value', 0)),
            a_depreciation_rate=float(data.get('a_depreciation_rate', 0)),
            a_apreciation_rate=float(data.get('a_apreciation_rate', 0)),
            a_accumulated_dep=float(data.get('a_accumulated_dep', 0)),
            a_status=data.get('a_status', ''),
            a_created_by=data.get('a_created_by', ''),
            a_organisation_id=data.get('a_organisation_id', ''),
            a_attached_card=data.get('a_attached_card')
        ) 
        if 'a_image' in files:
            image_file = files['a_image']
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join('images/assets', image_filename)
            image_file.save(image_path)
            new_asset.a_image = image_path

        for attachment in ['a_attachment1', 'a_attachment2', 'a_attachment3']:
            if attachment in files:
                file = files[attachment]
                filename = secure_filename(file.filename)
                file_path = os.path.join('images/assets', filename)
                file.save(file_path)
                setattr(new_asset, attachment, file_path)

        db.session.add(new_asset)
        db.session.commit()

        return jsonify(new_asset.as_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
