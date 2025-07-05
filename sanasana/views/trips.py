import datetime
from flask import (
    Blueprint,  jsonify, request, abort
)
from werkzeug.utils import secure_filename
import os
from sanasana.query import resources as qresources
from flask_restful import Api, Resource
from flask_cors import CORS
from dateutil.relativedelta import relativedelta
import datetime
from sqlalchemy import func
from sqlalchemy.orm import aliased
from .. import  db
from sanasana.query import trips as qtrip
from sanasana import models
from sanasana.query import send_email as qsend_email

# import pandas as pd


bp = Blueprint('trips', __name__, url_prefix='/trips')

api_trips = Api(bp)


class TripsByOrg(Resource):
    def get(self, org_id, user_id):
        """ list all trips """
        trips = [trip.as_dict() for trip in qtrip.get_trip_by_org(org_id)]
        return jsonify(trips)
    
    def post(self, org_id, user_id):
        """ Add an trip """
        request_data = request.get_json()

        data = {
            "t_created_by": user_id,
            "t_organization_id": org_id,
            "t_type": request_data["t_type"],
            "t_start_lat": request_data["t_start_lat"],
            "t_start_long": request_data["t_start_long"],
            "t_start_elavation": request_data["t_start_elavation"] if "t_start_elavation" in request_data else None,
            "t_end_lat": request_data["t_end_lat"],
            "t_end_long": request_data["t_end_long"],
            "t_end_elavation": request_data["t_end_elavation"] if "t_end_elavation" in request_data else None,
            "t_start_date": request_data["t_start_date"],
            "t_end_date": request_data["t_end_date"],
            "t_operator_id": request_data["t_operator_id"],
            "t_asset_id": request_data["t_asset_id"],
            "t_status": request_data["t_status"],
            "t_load": request_data["t_load"],
            "t_origin_place_id": request_data["t_origin_place_id"],
            "t_origin_place_query": request_data["t_origin_place_query"],
            "t_destination_place_id": request_data["t_destination_place_id"],
            "t_destination_place_query": request_data["t_destination_place_query"], 
            # "t_directionsResponse": request_data["t_directionsResponse"], ignore for now
            "t_distance": request_data["t_distance"] if "t_distance" in request_data else None,
            "t_duration": request_data["t_duration"],
            "t_client_id": request_data.get("t_client_id", None)  # Optional field
        }

        result = qtrip.add_trip(data)
        trip = result.as_dict()
        if trip:
            message_recipient = trip["o_email"]
            user_name = trip["o_name"]
            print('name', user_name, 'email>>', message_recipient)
            qsend_email.send_trip_assigned_email(message_recipient, user_name)
        return jsonify(trip=trip)


class TripsByAsset(Resource):
    def get(self, org_id, user_id, asset_id):
        """ list all trips """
        # trips = models.Trip.query.filter_by(t_organization_id=org_id,
        #                                     t_asset_id=asset_id).all()
        TripIncomeAlias = aliased(models.TripIncome)
        TripExpenseAlias = aliased(models.TripExpense)

        trips_data = db.session.query(
            models.Trip,
            func.coalesce(func.sum(TripIncomeAlias.ti_amount), 0.0).label("t_income"),
            func.coalesce(func.sum(TripExpenseAlias.te_amount), 0.0).label("t_expense")
        ).outerjoin(
            TripIncomeAlias, models.Trip.id == TripIncomeAlias.ti_trip_id
        ).outerjoin(
            TripExpenseAlias, models.Trip.id == TripExpenseAlias.te_trip_id
        ).filter(models.Trip.t_organization_id==org_id,models.Trip.t_asset_id==asset_id
        ).group_by(
            models.Trip.id
        ).order_by(
            models.Trip.t_created_at.desc()
        ).all()

        # Clean __dict__ to remove non-serializable attributes
        trips = []
        for trip, t_income, t_expense in trips_data:
            trip.t_income = t_income
            trip.t_expense = t_expense
            trips.append(trip)
        trips_list = [trip.as_dict() for trip in trips]
        return jsonify(trips_list)


class TripsByUser(Resource):
    def get(self, org_id, user_id):
        """ list all trips """
        # trips = models.Trip.query.filter_by(t_organization_id=org_id,
        #                                     user_id=user_id).all()
        
        trips = (
            models.Trip.query
            .join(models.Operator, models.Trip.t_operator_id == models.Operator.id)  # Join Operator table
            .join(models.User, models.User.email == models.Operator.o_email)  # Join User table through email
            .filter(models.User.id == user_id, models.Trip.t_organization_id == org_id)  # Apply filters
            .order_by(models.Trip.t_created_at.desc())
            .all() 
        )

        trips_list = [trip.as_dict() for trip in trips]
        return jsonify(trips_list)


class TripByStatus(Resource):
    def get(self, org_id, user_id, t_status):
        """ list all trips """
        trips = [trips.as_dict() for trips in
                 qtrip.get_trip_by_status(org_id, t_status)]
        return jsonify(trips)


class TripById(Resource):
    def get(self, org_id, user_id, trip_id):
        """ get trip by id """
        if trip_id is None:
            return abort(404)
        trip = qtrip.get_trip_by_id(trip_id).as_dict()    
        return jsonify(trip)
    
    def post(self, org_id, user_id, trip_id):
        request_data = request.json
        or_image_data = request_data['or_image']
        or_trip_id = trip_id
        or_image_url = qresources.save_image(or_image_data, or_trip_id)
        data = {
            "or_created_by": user_id,
            "or_organization_id": org_id,
            "or_trip_id": request_data["or_trip_id"],
            "or_asset_id": request_data["or_asset_id"],
            "or_operator_id": request_data["or_operator_id"],
            "or_image": or_image_url,
            "or_by_drivers": float(request_data["or_by_drivers"]),
            "or_reading": (request_data["or_reading"]),
            "or_latitude": request_data["or_latitude"],
            "or_longitude": request_data["or_longitude"],
            "or_description": request_data["or_description"]
        }
        qtrip.add_odometer_reading(data)
        
        description = request_data["or_description"]
        if description == "start_trip":
            data = {
                "t_start_od_reading": float(request_data["or_by_drivers"]),
                "t_start_od_reading_url": or_image_url,
                "t_started_at": datetime.datetime.utcnow()
            }
            for attribute, value in request_data.items():
                if attribute in ["t_status", "t_start_date"]:
                    data[attribute] = value
                qtrip.update(trip_id, data)
        elif description == "complete_trip":
            data = {
                "t_end_od_reading": float(request_data["or_by_drivers"]),
                "t_end_od_reading_url": or_image_url,
                "t_completed_at": datetime.datetime.utcnow()
            }
            for attribute, value in request_data.items():
                if attribute in ["t_status", "t_start_date"]:
                    data[attribute] = value
                qtrip.update(trip_id, data)
        
        t_status = request_data['t_status']
        if t_status:
            trip = qtrip.update_status(trip_id, t_status)
            return jsonify(trip.as_dict())


class OdometerReading(Resource):  
    def post(self, org_id, user_id):
        """ Add odometer reading """
        request_data = request.get_json()
        or_image_data = request_data['or_image']
        or_trip_id = request_data["or_trip_id"]

        or_image_url = qresources.save_image(or_image_data, or_trip_id)

        data = {
            "or_created_by": user_id,
            "or_organization_id": org_id,
            "or_trip_id": request_data["or_trip_id"],
            "or_asset_id": request_data["or_asset_id"],
            "or_operator_id": request_data["or_operator_id"],
            "or_image": or_image_url,
            "or_by_drivers": float(request_data["or_by_drivers"]),
            "or_reading": (request_data["or_reading"]),
            "or_latitude": request_data["or_latitude"],
            "or_longitude": request_data["or_longitude"],
            "or_description": request_data["or_description"]
        }

        result = qtrip.add_odometer_reading(data)
        od_reading = result.as_dict()
        return jsonify(od_reading=od_reading)  


class Approve_Request(Resource):  
    def post(self, org_id, user_id):
        user_org = models.Organization.query.filter_by(id=org_id).first()
        request_data = request.json
        t_id = request_data['t_id']
        fuel_type = request_data['a_fuel_type']
        t_actual_cost = float(request_data['t_actual_cost'])

        if fuel_type.lower() == "petrol":
            fuel_price = user_org.org_petrol_price
        elif fuel_type.lower() == "diesel":
            fuel_price = user_org.org_diesel_price
        else:
            fuel_price = 1

        t_actual_fuel = t_actual_cost/fuel_price

        trip = models.Trip.query.filter_by(id=t_id).first()
        if trip:
            trip.t_actual_fuel = t_actual_fuel
            trip.t_actual_cost = t_actual_cost
            db.session.commit()

        fuel_request = models.Fuel_request.query.filter_by(f_trip_id=t_id).first()
        if fuel_request:
            fuel_request.f_status = "Approved"
            fuel_request.f_litres = t_actual_fuel
            fuel_request.f_cost = fuel_price
            fuel_request.f_total_cost = t_actual_cost

            if 'image' in request_data:
                image_data = request_data['image']
                or_image_url = qresources.save_receipt_image(image_data, fuel_request.id)
                fuel_request.f_receipt_image = or_image_url
            db.session.commit()

            expense_data = {
                "te_created_by": user_id,
                "te_organization_id": org_id,
                "te_trip_id": t_id,
                "te_asset_id": trip.t_asset_id,
                "te_operator_id": trip.t_operator_id,
                "te_type": "Fuel",
                "te_description": "Fuel request approved",
                "te_amount": t_actual_cost
                }
            qtrip.add_trip_expense(expense_data)


class Trip_income(Resource):
    def get(self, org_id, user_id, trip_id):
        income = models.TripIncome.query.filter_by(
            ti_organization_id=org_id, ti_trip_id=trip_id).order_by(
                models.TripIncome.id.desc()).all()
        income_list = [income.as_dict() for income in income]
        return jsonify(income_list)
 
    def post(self, org_id, user_id, trip_id):
        """ Add trip income """
        request_data = request.get_json()
        data = {
            "ti_created_by": user_id,
            "ti_organization_id": org_id,
            "ti_trip_id": trip_id,
            "ti_asset_id": request_data["ti_asset_id"],
            "ti_operator_id": request_data["ti_operator_id"],
            "ti_client_id": request_data["ti_client_id"],
            "ti_type": request_data["ti_type"],
            "ti_description": request_data["ti_description"],
            "ti_amount": request_data["ti_amount"]
        }
        result = qtrip.add_trip_income(data)
        trip_income = result.as_dict()
        return jsonify(trip_income=trip_income)


class TripIncomeByAsset(Resource):
    def get(self, org_id, user_id, asset_id):
        income = models.TripIncome.query.filter_by(
            ti_organization_id=org_id,
            ti_asset_id=asset_id
        ).order_by(models.TripIncome.id.desc()).all()
        income_list = [income.as_dict() for income in income]
        return jsonify(income_list)
    
    def post(self, org_id, user_id, asset_id):
        """ Add trip income by asset """
        request_data = request.get_json()
        data = {
            "ti_created_by": user_id,
            "ti_organization_id": org_id,
            "ti_asset_id": asset_id,
            "ti_operator_id": request_data["ti_operator_id"],
            "ti_client_id": request_data["ti_client_id"],
            "ti_type": request_data["ti_type"],
            "ti_description": request_data["ti_description"],
            "ti_amount": request_data["ti_amount"]
        }
        result = qtrip.add_trip_income(data)
        trip_income = result.as_dict()
        return jsonify(trip_income=trip_income)


class TripExpense(Resource):
    def get(self, org_id, user_id, trip_id):
        expense = models.TripExpense.query.filter_by(
            te_organization_id=org_id, te_trip_id=trip_id).order_by(
                models.TripExpense.id.desc()
            ).all()
        expense_list = [expense.as_dict() for expense in expense]
        return jsonify(expense_list)
 
    def post(self, org_id, user_id, trip_id):
        """ Add trip income """
        request_data = request.get_json()
        data = {
            "te_created_by": user_id,
            "te_organization_id": org_id,
            "te_trip_id": trip_id,
            "te_asset_id": request_data["te_asset_id"],
            "te_operator_id": request_data["te_operator_id"],
            "te_type": request_data["te_type"],
            "te_description": request_data["te_description"],
            "te_amount": request_data["te_amount"]
        }
        result = qtrip.add_trip_expense(data)
        trip_expense = result.as_dict()
        return jsonify(trip_expense=trip_expense)


class TripExpenseByAsset(Resource):
    def get(self, org_id, user_id, asset_id):
        expense = models.TripExpense.query.filter_by(
            te_organization_id=org_id,
            te_asset_id=asset_id
        ).order_by(models.TripExpense.id.desc()).all()
        expense_list = [expense.as_dict() for expense in expense]
        return jsonify(expense_list)
    
    def post(self, org_id, user_id, asset_id):
        """ Add trip income by asset """
        request_data = request.get_json()
        data = {
            "te_created_by": user_id,
            "te_organization_id": org_id,
            "te_asset_id": asset_id,
            "te_operator_id": request_data["te_operator_id"],
            "te_type": request_data["te_type"],
            "te_description": request_data["te_description"],
            "te_amount": request_data["te_amount"]
        }
        result = qtrip.add_trip_expense(data)
        trip_expense = result.as_dict()
        return jsonify(trip_expense=trip_expense)


class TripReport(Resource):
    def get(self, org_id):
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

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
                    (trip.t_completed_at - trip.t_started_at).bit_length()
                    if trip.t_completed_at is not None and trip.t_started_at 
                    is not None else None
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

        return jsonify(trips_list)


class internal_customer_metrics(Resource):
    def get(self):
        report_type = request.args.get('report_type').lower()
        if report_type is None:
            report_type = 'weekly'  # Default to daily if not specified

        end_date = datetime.datetime.now()
        start_date = None

        if report_type == "daily":
            start_date = end_date - datetime.timedelta(days=1)
        if report_type == "weekly":
            start_date = end_date - datetime.timedelta(weeks=1)
        if report_type == "monthly":
            # Handle month start - safe for month boundaries
            start_date = end_date - relativedelta(months=1)
        report = qtrip.get_internal_customer_metric_report(start_date, end_date)
        return jsonify(report)


api_trips.add_resource(TripsByOrg, '/<org_id>/<user_id>/')
api_trips.add_resource(TripsByAsset, '/by_asset/<org_id>/<user_id>/<asset_id>/')
api_trips.add_resource(TripsByUser, '/by_user/<org_id>/<user_id>/')
api_trips.add_resource(TripByStatus, '/status/<org_id>/<user_id>/<t_status>/')
api_trips.add_resource(TripById, '/<org_id>/<user_id>/<trip_id>/')
api_trips.add_resource(OdometerReading, '/odometer/<org_id>/<user_id>/')
api_trips.add_resource(Approve_Request, '/approve_request/<org_id>/<user_id>/')
api_trips.add_resource(Trip_income, '/income/<org_id>/<user_id>/<trip_id>/')
api_trips.add_resource(TripIncomeByAsset, '/asset_income/<org_id>/<user_id>/<asset_id>/')
api_trips.add_resource(TripExpense, '/expense/<org_id>/<user_id>/<trip_id>/')
api_trips.add_resource(TripExpenseByAsset, '/asset_expense/<org_id>/<user_id>/<asset_id>/')
api_trips.add_resource(TripReport, '/reports/<org_id>/')
api_trips.add_resource(internal_customer_metrics, '/reports/internal_customer_metrics/')



def get_trip_column(trip_id, column_name):
    trip = models.Trip.query.get(trip_id)
    return getattr(trip, column_name, None) if trip else None


@bp.route('/status')
def get_trip_status():
    trip_status = Tstatus.query.all()
    status_list = [status.as_dict() for status in trip_status]
    return jsonify(status_list)


@bp.route('/create', methods=['POST'])
def add_trip():
    try:
        data = request.json
        required_fields = ['t_organization_id', 't_created_by']
        data = {k.strip().lower(): v for k, v in data.items()}
        required_fields_normalized = [field.lower() for field in required_fields]
        missing_fields = [field for field in required_fields_normalized if field not in data]

        if missing_fields:
            return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

        new_trip = Trip(
            t_organization_id=data.get('t_organization_id'),
            t_created_by=data.get('t_created_by'),
            t_type=data.get('t_type'),
            t_start_lat=data.get('t_start_lat'),
            t_start_long=data.get('t_start_long'),
            t_start_elavation=data.get('t_start_elavation'),
            t_end_lat=data.get('t_end_lat'),
            t_end_long=data.get('t_end_long'),
            t_end_elavation=data.get('t_end_elavation'),
            t_start_date=data.get('t_start_date'),
            t_end_date=data.get('t_end_date'),
            t_operator_id=data.get('t_operator_id'),
            t_asset_id=data.get('t_asset_id'),
            t_status=data.get('t_status'),
            t_load=data.get('t_load'),
            t_origin_place_id=data.get('t_origin_place_id'),
            t_origin_place_query=data.get('t_origin_place_query'),
            t_destination_place_id=data.get('t_destination_place_id'),
            t_destination_place_query=data.get('t_destination_place_query'),
            # t_directionsResponse=data.get('t_directionsResponse'),      
            t_distance=data.get('t_distance') if 't_distance' in data else None,
            t_duration=data.get('t_duration'),

        )

        db.session.add(new_trip)
        db.session.commit()

        return jsonify(new_trip.as_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# @bp.route('/<int:trip_id>', methods=['PUT'])
# def update_trip(trip_id):
#     trip = get_trip_by_id(trip_id)
#     if not trip:
#         return jsonify({'error': 'Trip not found'}), 404
#     try:
#         data = request.get_json()
#         # Loop through each attribute and value in the JSON data
#         for attribute, value in data.items():
#             if hasattr(trip, attribute):
#                 setattr(trip, attribute, value)
#             else:
#                 return jsonify({'error': f'Invalid attribute: {attribute}'}), 400
#         db.session.commit()
#         return jsonify({'message': 'Trip updated successfully'}), 200
#     except Exception as e:
#         db.session.rollback()  # Rollback in case of any errors
#         return jsonify({'error': 'Failed to update trip' + str(e)}), 500
    


@bp.route('/distance')
def calculate_distance():
    return 1


@bp.route('/fuel')
def calculate_fuel():
    return 1