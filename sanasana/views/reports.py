from flask import (
    Blueprint,  jsonify, request, g
)
from flask_restful import Api, Resource
from sanasana import models
from sanasana.utils.excel_exporter import export_to_excel
from sanasana.utils.pdf_exporter import export_to_pdf
from sanasana.query import reports as qreports
from sanasana.query import fuel as qfuel_request


bp = Blueprint('reports', __name__, url_prefix='/reports')
api_summaries = Api(bp)


class TripListingReport(Resource):
    def get(self):
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        export = request.args.get('export', 'excel').lower()

        query = (
            models.Trip.query
            .filter_by(t_organization_id=g.current_user.organization_id)
            .order_by(models.Trip.t_created_at.desc())
        )

        if start_date and end_date:
            query = query.filter(models.Trip.t_created_at.between(start_date, end_date))

        trips = query.all()

        trips_list = [
            {
                "Description": trip.t_type,
                "Operator": trip.operator.o_name,
                "Asset": trip.asset.a_license_plate,
                "Make-model": (trip.asset.a_make + "- " + trip.asset.a_model),
                "Start-date": trip.t_start_date.strftime("%d.%m.%Y") if trip.t_start_date else None,
                "End-date": trip.t_end_date.strftime("%d.%m.%Y") if trip.t_end_date else None,
                "Origin": trip.t_origin_place_query,
                "Destination": trip.t_destination_place_query,
                "Status": trip.t_status,
                "Est-duration": trip.t_duration,
                "Actual-duration": (
                    str(trip.t_completed_at - trip.t_started_at)
                    if trip.t_completed_at is not None and trip.t_started_at is not None
                    else None
                ),
                "Origin-Lat": trip.t_start_lat,
                "Origin-Lng": trip.t_start_long,
                "Destination-Lat": trip.t_end_lat,
                "Destination-Lng": trip.t_end_long,
                "Tonnage": trip.t_load,
                "Fuel-type": trip.asset.a_fuel_type,
                "Fuel-in-Ltr": trip.t_actual_fuel,
                "Total Cost": trip.t_actual_cost,
                "End-od-reading": trip.t_end_od_reading,
                "Start-Od_reading": trip.t_start_od_reading,
                "Actual-distance": (
                    trip.t_end_od_reading - trip.t_start_od_reading
                    if trip.t_end_od_reading is not None and
                    trip.t_start_od_reading is not None else None),
                "Expected-distance": trip.t_distance,
            }
            for trip in trips
        ]
        if export == "excel":
            return export_to_excel(
                trips_list,
                filename=f"trip_listing_report.xlsx",
                sheet_name="Trip Listing Report"
            )
        elif export == "pdf":
            return export_to_pdf(
                trips_list,
                filename=f"trip_listing_report.pdf",
                title="Trip Listing Report"
            )
        

class internal_customer_metrics(Resource):
    def get(self):
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        export = request.args.get('export', 'pdf').lower()

        if not start_date or not end_date:
            return {
                "error": "start_date and end_date are required"
            }, 400

        report = qreports.get_internal_customer_metric_report(start_date, end_date)
        report_list = [report]
        if export == "excel":
            return export_to_excel(
                report_list,
                filename=f"internal_customer_metrics_report.xlsx",
                sheet_name="Internal Customer Metrics Report"
            )
        elif export == "pdf":
            return export_to_pdf(
                report_list,
                filename=f"internal_customer_metrics_report.pdf",
                title="Internal Customer Metrics Report"
            )


class AssetListingReport(Resource):
    def get(self):
        export = request.args.get('export', 'excel').lower()

        assets = models.Asset.query.filter_by(a_organisation_id=g.current_user.organization_id).all()
        assets_list = [asset.as_dict() for asset in assets]

        if export == "excel":
            return export_to_excel(
                assets_list,
                filename=f"assets_listing_report.xlsx",
                sheet_name="Assets Listing Report"
            )
        elif export == "pdf":
            return export_to_pdf(
                assets_list,
                filename=f"assets_listing_report.pdf",
                title="Assets Listing Report"
            )
        

class NewAssetListingReport(Resource):
    def get(self):
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        export = request.args.get('export', 'excel').lower()

        query = models.Asset.query.filter_by(a_organisation_id=g.current_user.organization_id)

        if start_date and end_date:
            query = query.filter(models.Asset.a_created_at.between(start_date, end_date))

        assets = query.all()
        assets_list = [asset.as_dict() for asset in assets]

        if export == "excel":
            return export_to_excel(
                assets_list,
                filename=f"new_assets_report.xlsx",
                sheet_name="New Assets Report"
            )
        elif export == "pdf":
            return export_to_pdf(
                assets_list,
                filename=f"new_assets_report.pdf",
                title="New Assets Report"
            )


class FuelRequestReport(Resource):
    def get(self):
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        export = request.args.get('export', 'excel').lower()

        user_org = models.Organization.query.filter_by(id=g.current_user.organization_id).first()
        fuel_expenses = qfuel_request.get_fuel_expenses_by_org(g.current_user.organization_id, start_date, end_date)

        fuel_requests_list = [
            {
                "vehicle": expense.asset.a_license_plate,
                "operator": expense.operator.o_name,
                "created_at": expense.te_created_at.strftime('%Y-%m-%d'),
                "fuel_type": expense.asset.a_fuel_type,
                "amount": f"{expense.te_amount} {user_org.org_currency}",
                "description": expense.te_description,
                "distance": expense.trip.t_distance,
                "litres": round(expense.trip.t_actual_fuel, 2),
                "Trip status": expense.trip.t_status,
              
            }
            for expense in fuel_expenses
        ]
        if export == "excel":
            return export_to_excel(
                fuel_requests_list,
                filename=f"fuel_requests_expense_report.xlsx",
                sheet_name="Fuel Requests Expense Report"
            )
        elif export == "pdf":
            return export_to_pdf(
                fuel_requests_list,
                filename=f"fuel_requests_expense_report.pdf",
                title="Fuel Requests Expense Report"
            )
        

class MaintenanceListingReport(Resource):
    def get(self):
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        export = request.args.get('export', 'excel').lower()

        maintenance_list = qreports.get_report(g.current_user.organization_id, start_date, end_date)

        if export == "excel":
            return export_to_excel(
                maintenance_list,
                filename=f"maintenance_listing_report.xlsx",
                sheet_name="Maintenance Listing Report"
            )
        elif export == "pdf":
            return export_to_pdf(
                maintenance_list,
                filename=f"maintenance_listing_report.pdf",
                title="Maintenance Listing Report"
            )
        

class OperatorsListingReport(Resource):
    def get(self):
        export = request.args.get('export', 'excel').lower()

        operators = models.Operator.query.filter_by(o_organisation_id=g.current_user.organization_id).all()

        operators_list = [
            {
                "o_created_at": (
                    operator.o_created_at.strftime("%d.%m.%Y")
                    if operator.o_created_at
                    else None
                ),
                "Name": operator.o_name,
                "Assigned Asset": operator.asset.a_license_plate,
                "National ID": operator.o_national_id,
                "Phone": operator.o_phone,
                "Email": operator.o_email,
                "Role": operator.o_role,
                "Status": operator.o_status,
                "Cumulative Mileage": operator.o_cum_mileage,
                "Experience": operator.o_expirence,
                "License ID": operator.o_lincense_id,
                "License Type": operator.o_lincense_type,
                "License Expiry": (
                    operator.o_lincense_expiry.strftime("%d.%m.%Y")
                    if operator.o_lincense_expiry
                    else None
                ),
            }
            for operator in operators
        ]

        if export == "excel":
            return export_to_excel(
                operators_list,
                filename=f"operators_listing_report.xlsx",
                sheet_name="Operators Listing Report"
            )
        elif export == "pdf":
            return export_to_pdf(
                operators_list,
                filename=f"operators_listing_report.pdf",
                title="Operators Listing Report"
            )

        
class NewOperatorsListingReport(Resource):
    def get(sel):
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        export = request.args.get('export', 'excel').lower()

        query = models.Operator.query.filter_by(o_organisation_id=g.current_user.organization_id)

        if start_date and end_date:
            query = query.filter(
                models.Operator.o_created_at.between(start_date, end_date)
            )

        operators = query.all()

        operators_list = [
            {
                "o_created_at": (
                    operator.o_created_at.strftime("%d.%m.%Y")
                    if operator.o_created_at
                    else None
                ),
                "Name": operator.o_name,
                "Assigned Asset": operator.asset.a_license_plate,
                "National ID": operator.o_national_id,
                "Phone": operator.o_phone,
                "Email": operator.o_email,
                "Role": operator.o_role,
                "Status": operator.o_status,
                "Cumulative Mileage": operator.o_cum_mileage,
                "Experience": operator.o_expirence,
                "License ID": operator.o_lincense_id,
                "License Type": operator.o_lincense_type,
                "License Expiry": (
                    operator.o_lincense_expiry.strftime("%d.%m.%Y")
                    if operator.o_lincense_expiry
                    else None
                ),
            }
            for operator in operators
        ]

        if export == "excel":
            return export_to_excel(
                operators_list,
                filename=f"new_operators_listing_report.xlsx",
                sheet_name="New Operators Listing Report"
            )
        elif export == "pdf":
            return export_to_pdf(
                operators_list,
                filename=f"new_operators_listing_report.pdf",
                title="New Operators Listing Report"
            )


api_summaries.add_resource(TripListingReport, '/trip-listing/')
api_summaries.add_resource(internal_customer_metrics, '/internal-customer-metrics/')
api_summaries.add_resource(AssetListingReport, '/asset-listing/')
api_summaries.add_resource(NewAssetListingReport, '/new-asset-listing/')
api_summaries.add_resource(FuelRequestReport, '/fuel-requests-expense/')
api_summaries.add_resource(MaintenanceListingReport, '/maintenance-listing/')
api_summaries.add_resource(OperatorsListingReport, '/operators-listing/')
api_summaries.add_resource(NewOperatorsListingReport, '/new-operators-listing/')