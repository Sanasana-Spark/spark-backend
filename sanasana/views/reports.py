from flask import (
    Blueprint,  jsonify, request
)
from flask_restful import Api, Resource
from sanasana import models
from sanasana.utils.excel_exporter import export_to_excel
from sanasana.utils.pdf_exporter import export_to_pdf


bp = Blueprint('reports', __name__, url_prefix='/reports')
api_summaries = Api(bp)


class TripListingReport(Resource):
    def get(self, org_id):
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        export = request.args.get('export', 'excel').lower()

        query = (
            models.Trip.query
            .filter_by(t_organization_id=org_id)
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
 

api_summaries.add_resource(TripListingReport, '/<org_id>/trip-listing/')