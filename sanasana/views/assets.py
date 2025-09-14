from flask import (
    Blueprint,  jsonify, request, g
)
from flask_restful import Api, Resource
from sqlalchemy import func, and_, cast, Numeric, Float
from werkzeug.utils import secure_filename
from dateutil.relativedelta import relativedelta
import os
import datetime
from datetime import datetime
from .. import db
from sanasana.query import assets as qasset
from sanasana.query import clients as qclients
from sanasana.models import Status, Asset, Trip,  TripIncome, TripExpense
from sanasana import models

bp = Blueprint('assets', __name__, url_prefix='/assets')

api_assets = Api(bp)


class Assets(Resource):
    def get(self):
        org_id = g.current_user.organization_id
        assets = [asset.as_dict() for asset in qasset.get_asset_by_org(org_id)]
        return jsonify(assets=assets)

    def post(self):
        data = request.get_json()
        data = {k.strip().lower(): v for k, v in data.items()}

        data = {
            "a_created_by": g.current_user.id,
            "a_organisation_id": g.current_user.organization_id,
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


class AssetById(Resource):
    def get(self, asset_id):
        assets = qasset.get_asset_by_id(g.current_user.organization_id, asset_id).as_dict()
        return jsonify(assets)

    def put(self, asset_id):
        """ Update a asset """
        data = request.get_json()
        data = {k.strip().lower(): v for k, v in data.items()}

        data["a_organisation_id"] = g.current_user.organization_id

        result = qasset.update_asset(asset_id, data)
        if not result:
            return jsonify(error="Asset not found"), 404

        asset = result.as_dict()
        return jsonify(asset=asset)

    def delete(self, asset_id):
        """ Delete a asset """
        result = qasset.delete_asset(asset_id)
        if result:
            return jsonify(message="Asset deleted successfully")
        else:
            return jsonify(message="Asset not found"), 404
    

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
    def get(self):
        org_id = g.current_user.organization_id
        print("Organization ID:", org_id)  # Debugging line
        # Get query parameters for date filtering
        start_date = request.args.get("start_date")  # Format: 'YYYY-MM-DD'
        end_date = request.args.get("end_date")  # Format: 'YYYY-MM-DD'

        # Convert dates if they exist
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # TripIncome subquery
        income_subq = db.session.query(
            TripIncome.ti_asset_id.label("asset_id"),
            func.coalesce(func.sum(cast(TripIncome.ti_amount, Float)), 0).label("total_revenue")
        ).group_by(TripIncome.ti_asset_id)

        if start_date and end_date:
            income_subq = income_subq.filter(
                and_(
                    TripIncome.ti_created_at >= start_date,
                    TripIncome.ti_created_at <= end_date
                )
            )

        income_subq = income_subq.subquery()

        # TripExpense subquery
        expense_subq = db.session.query(
            TripExpense.te_asset_id.label("asset_id"),
            func.coalesce(func.sum(cast(TripExpense.te_amount, Float)), 0).label("total_expense")
        ).group_by(TripExpense.te_asset_id)

        if start_date and end_date:
            expense_subq = expense_subq.filter(
                and_(
                    TripExpense.te_created_at >= start_date,
                    TripExpense.te_created_at <= end_date
                )
            )

        expense_subq = expense_subq.subquery()

        # Main asset + trip query
        query = (
            db.session.query(
                Asset.id.label("id"),
                Asset.a_license_plate.label("a_license_plate"),
                Asset.a_make.label("a_make"),
                Asset.a_model.label("a_model"),
                Asset.a_year.label("a_year"),
                Asset.a_efficiency_rate.label("a_efficiency_rate"),
                func.count(Trip.id).label("trip_count"),
                func.sum(
                    cast(func.regexp_replace(Trip.t_distance, '[^0-9.]', '', 'g'), Numeric)
                ).label("total_miles"),
                func.sum(Trip.t_actual_fuel).label("total_fuel"),
                func.sum(Trip.t_actual_cost).label("total_cost"),
                func.coalesce(income_subq.c.total_revenue, 0).label("total_revenue"),
                func.coalesce(expense_subq.c.total_expense, 0).label("total_expense"),
            )
            .filter(Asset.a_organisation_id == org_id)
            .join(Trip, Asset.id == Trip.t_asset_id)
            .outerjoin(income_subq, income_subq.c.asset_id == Asset.id)
            .outerjoin(expense_subq, expense_subq.c.asset_id == Asset.id)
            .group_by(
                Asset.id,
                Asset.a_license_plate,
                Asset.a_make,
                Asset.a_model,
                Asset.a_year,
                Asset.a_efficiency_rate,
                income_subq.c.total_revenue,
                expense_subq.c.total_expense
            )
            .order_by(func.sum(cast(func.regexp_replace(Trip.t_distance, '[^0-9.]', '', 'g'), Numeric)).desc())
        )

        # Apply date filtering if both dates are provided
        if start_date and end_date:
            query = query.filter(
                and_(
                    func.date(Trip.t_start_date) >= start_date,
                    func.date(Trip.t_start_date) <= end_date
                )
            )

        results = query.all()

        # Convert to JSON format
        fleet_data = [
            {
                "id": row.id,
                "a_license_plate": row.a_license_plate,
                "a_make": row.a_make,
                "a_model": row.a_model,
                "a_year": row.a_year,
                "a_efficiency_rate": row.a_efficiency_rate,
                "trip_count": row.trip_count,
                "total_miles": float(row.total_miles or 0),
                "total_fuel": float(row.total_fuel or 0),
                "total_cost": float(row.total_cost or 0),
                "total_revenue": float(row.total_revenue or 0),
                "total_expense": float(row.total_expense or 0),
                "profit": float((row.total_revenue or 0) - (row.total_expense or 0))
            }
            for row in results
        ]

        return jsonify(fleet_data=fleet_data)


class IncomeByAssetId(Resource):
    def get(self, asset_id):
        invoices = models.TripIncome.query.filter(
            and_(
                models.TripIncome.ti_organization_id == g.current_user.organization_id,
                models.TripIncome.ti_asset_id.isnot(None),
                models.TripIncome.ti_asset_id == asset_id,
                models.TripIncome.ti_status != "deleted"
            )
        ).all()
        invoices = [invoice.as_dict() for invoice in invoices]
        return jsonify(invoices=invoices)

    def post(self, asset_id):
        """ Add a invoice """
        request_data = request.get_json()

        data = {
            "ti_created_by": g.current_user.id,
            "ti_organization_id": g.current_user.organization_id,
            "ti_client_id": request_data["client_id"],
            "ti_asset_id": asset_id,
            "ti_type": request_data["ti_type"],
            "ti_description" : request_data["ti_description"],
            "ti_amount": request_data["ti_amount"],
            "ti_status": request_data["ti_status"]
        }

        result = qasset.add_invoice(asset_id, data)
        invoice = result.as_dict()
        return jsonify(invoice=invoice)
    
    def put(self, client_id):
        """ Update a client """
        request_data = request.get_json()

        data = {
            "ti_created_by": g.current_user.id,
            "ti_organization_id": g.current_user.organization_id,
            "ti_client_id": client_id,
            "ti_amount": request_data["ti_amount"],
            "ti_date": request_data["ti_date"],
            "ti_status": request_data["ti_status"]
        }

        result = qclients.update_invoice(data)
        invoice = result.as_dict()
        return jsonify(invoice=invoice)


class ExpenseByAssetId(Resource):
    def get(self, asset_id):
        expenses = models.TripExpense.query.filter(
            and_(
                models.TripExpense.te_organization_id == g.current_user.organization_id,
                models.TripExpense.te_asset_id.isnot(None),
                models.TripExpense.te_asset_id == asset_id,
                models.TripExpense.te_status != "deleted"
                
            )
        ).all()
        expenses = [expense.as_dict() for expense in expenses]
        return jsonify(expenses=expenses)
    
    def post(self, asset_id):
        """ Add asset expense """
        request_data = request.get_json()
        data = {
            "te_created_by": g.current_user.id,
            "te_organization_id": g.current_user.organization_id,
            "te_trip_id": request_data["trip_id"],
            "te_asset_id": asset_id,
            "te_operator_id": request_data["te_operator_id"],
            "te_type": request_data["te_type"],
            "te_description": request_data["te_description"],
            "te_amount": request_data["te_amount"]
        }
        result = qasset.add_asset_expense(asset_id, data)
        asset_expense = result.as_dict()
        return jsonify(asset_expense=asset_expense)

    def put(self, asset_id):
        """ Update a client """
        request_data = request.get_json()

        data = {
            "ti_created_by": g.current_user.id,
            "ti_organization_id": g.current_user.organization_id,
            "ti_asset_id": asset_id,
            "ti_amount": request_data["ti_amount"],
            "ti_date": request_data["ti_date"],
            "ti_status": request_data["ti_status"]
        }

        result = qclients.update_invoice(data)
        invoice = result.as_dict()
        return jsonify(invoice=invoice)


class AssetPerformance(Resource):
    def get(self):
        report_type = request.args.get("report_type")
        if not report_type:
            report_type = "monthly"

        end_date = datetime.datetime.now()
        start_date = None

        if report_type == "daily":
            start_date = end_date - datetime.timedelta(days=1)
        elif report_type == "weekly":
            start_date = end_date - datetime.timedelta(weeks=1)
        elif report_type == "monthly":
            start_date = end_date - relativedelta(months=1)

        report = qasset.get_asset_performance(g.current_user.organization_id, start_date, end_date)
        return jsonify(report)
    

api_assets.add_resource(Assets, '/')
api_assets.add_resource(AssetById, '/<asset_id>/')
api_assets.add_resource(AssetStatus, '/status')
api_assets.add_resource(AssetPerformance, '/asset_performance/')
api_assets.add_resource(FleetPerformance, '/fleet_performance/')
api_assets.add_resource(IncomeByAssetId, '/income/<asset_id>/')
api_assets.add_resource(ExpenseByAssetId, '/expense/<asset_id>/')
