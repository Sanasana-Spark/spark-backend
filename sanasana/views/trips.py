import datetime
from flask import (
    Blueprint,  jsonify, request, abort, g
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
from sanasana.query import fuel as qfuel_request

# import pandas as pd


bp = Blueprint('trips', __name__, url_prefix='/trips')

api_trips = Api(bp)


class TripsByOrg(Resource):
    def get(self):
        """ list all trips """
        org_id = g.current_user.organization_id
        state = request.args.get('state', None) # new or pending-approval or completed
        if state not in ["new", "pending-approval", "completed", None]:
            return abort(400, description="Invalid state. Use 'new', 'pending-approval', 'completed' or leave empty for all trips.")
        if state is None:
            trips = [trip.as_dict() for trip in qtrip.get_trip_by_org(org_id)]
            return jsonify(trips)
        else:
            trips = [trip.as_dict() for trip in qtrip.get_specific_trips(state, org_id)]
            return jsonify(trips)
    
    def post(self):
        """ Add an trip """
        request_data = request.get_json()

        data = {
            "t_created_by": g.current_user.id,
            "t_organization_id": g.current_user.organization_id,
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

        trip_result = qtrip.add_trip(data)
        print('trip_result id', trip_result.id)
        stops = request_data.get("stops", [])
        for stop in stops:
            new_stop = {
                "s_trip_id": trip_result.id,
                "s_place_id": stop["s_place_id"],
                "s_place_query": stop["s_place_query"],
                "s_lat": stop["s_lat"],
                "s_long": stop["s_long"],
                "s_client_id": stop["s_client_id"]
            }
            stop_result = qtrip.add_stop(new_stop)
            print('stop_result', stop_result)

        trip = trip_result.as_dict()
        if trip:
            message_recipient = trip["o_email"]
            user_name = trip["o_name"]
            print('name', user_name, 'email>>', message_recipient)
            qsend_email.send_trip_assigned_email(message_recipient, user_name)
        return jsonify(trip=trip)
    
    
class TripsByOrgOperator(Resource):
    def get(self):
        """ list all trips """
        state = request.args.get('state', "current") # new or current or completed
        if state not in ["current", "completed", "new"]:
            return abort(400, description="Invalid state. Use 'current' or 'completed' or 'new'.")
        trips = [trip.as_dict() for trip in qtrip.get_driver_specific_trips(
            state, g.current_user.organization_id, g.current_user.id
            )]
        return jsonify(trips)


class TripsByAsset(Resource):
    def get(self, asset_id):
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
        ).filter(models.Trip.t_organization_id==g.current_user.organization_id,models.Trip.t_asset_id==asset_id
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
    def get(self):
        """ list all trips """
        # trips = models.Trip.query.filter_by(t_organization_id=org_id,
        #                                     user_id=user_id).all()
        
        trips = (
            models.Trip.query
            .join(models.Operator, models.Trip.t_operator_id == models.Operator.id)  # Join Operator table
            .join(models.User, models.User.email == models.Operator.o_email)  # Join User table through email
            .filter(models.User.id == g.current_user.id, models.Trip.t_organization_id == g.current_user.organization_id)  # Apply filters
            .order_by(models.Trip.t_created_at.desc())
            .all() 
        )

        trips_list = [trip.as_dict() for trip in trips]
        return jsonify(trips_list)


class TripByStatus(Resource):
    def get(self, t_status):
        """ list all trips """
        trips = [trips.as_dict() for trips in
                 qtrip.get_trip_by_status(g.current_user.organization_id, t_status)]
        return jsonify(trips)


class TripById(Resource):
    def get(self, trip_id):
        """ get trip by id """
        if trip_id is None:
            return abort(404)
        trip = qtrip.get_trip_by_id(trip_id).as_dict()    
        return jsonify(trip)

    def post(self, trip_id):
        request_data = request.json
        or_image_data = request_data['or_image']
        or_trip_id = trip_id
        or_image_url = qresources.save_image(or_image_data, or_trip_id)
        data = {
            "or_created_by": g.current_user.id,
            "or_organization_id": g.current_user.organization_id,
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


class TripLocationByPhone(Resource):
    def post(self, trip_id):
        request_data = request.json
        data = {
            "or_created_by": g.current_user.id,
            "or_organization_id": g.current_user.organization_id,
            "or_trip_id": request_data["or_trip_id"],
            "or_asset_id": request_data["or_asset_id"],
            "or_operator_id": request_data["or_operator_id"],
            "or_latitude": request_data["or_latitude"],
            "or_longitude": request_data["or_longitude"],
            "or_description": request_data["or_description"]
        }
        qtrip.add_drivers_location(data) 


class OdometerReading(Resource):  
    def post(self):
        """ Add odometer reading """
        request_data = request.get_json()
        or_image_data = request_data['or_image']
        or_trip_id = request_data["or_trip_id"]
        org_id = g.current_user.organization_id
        or_image_url = qresources.save_image(or_image_data, or_trip_id)

        data = {
            "or_created_by": g.current_user.id,
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


class Trip_Original_Fuel_Request(Resource):
    def get(self, trip_id):
        """ Get original fuel request by trip id """
        fuel_request = qfuel_request.get_fuel_request_by_trip(trip_id)
        if not fuel_request:
            return jsonify({"message": "No fuel request found for this trip"}), 404
        return jsonify(fuel_request.as_dict())


class Approve_Request(Resource):
    def post(self):
        user_org = models.Organization.query.filter_by(id=g.current_user.organization_id).first()
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
        t_carbon_emission = qfuel_request.calculate_carbon_emission(fuel_type, t_actual_fuel)

        trip = models.Trip.query.filter_by(id=t_id).first()
        if trip:
            trip.t_actual_fuel = t_actual_fuel
            trip.t_actual_cost = t_actual_cost
            trip.t_carbon_emission = t_carbon_emission
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
                "te_created_by": g.current_user.id,
                "te_organization_id": g.current_user.organization_id,
                "te_trip_id": t_id,
                "te_asset_id": trip.t_asset_id,
                "te_operator_id": trip.t_operator_id,
                "te_type": "Fuel",
                "te_description": "Fuel request approved",
                "te_amount": t_actual_cost
                }
            qtrip.add_trip_expense(expense_data)


class Trip_income(Resource):
    def get(self, trip_id):
        income = models.TripIncome.query.filter_by(
            ti_organization_id=g.current_user.organization_id, ti_trip_id=trip_id).order_by(
                models.TripIncome.id.desc()).all()
        income_list = [income.as_dict() for income in income]
        return jsonify(income_list)

    def post(self, trip_id):
        """ Add trip income """
        request_data = request.get_json()
        data = {
            "ti_created_by": g.current_user.id,
            "ti_organization_id": g.current_user.organization_id,
            "ti_trip_id": trip_id,
            "ti_asset_id": request_data["ti_asset_id"],
            "ti_operator_id": request_data["ti_operator_id"],
            "ti_client_id": request_data["ti_client_id"],
            "ti_type": request_data["ti_type"],
            "ti_description": request_data["ti_description"],
            "ti_amount": request_data["ti_amount"],
            "ti_paid_amount": request_data.get("ti_paid_amount", 0),
            "ti_balance": request_data.get("ti_balance", request_data["ti_amount"])  # Optional field
        }
        result = qtrip.add_trip_income(data)
        trip_income = result.as_dict()
        return jsonify(trip_income=trip_income)


class TripIncomeByAsset(Resource):
    def get(self, asset_id):
        income = models.TripIncome.query.filter_by(
            ti_organization_id=g.current_user.organization_id,
            ti_asset_id=asset_id
        ).order_by(models.TripIncome.id.desc()).all()
        income_list = [income.as_dict() for income in income]
        return jsonify(income_list)

    def post(self, asset_id):
        """ Add trip income by asset """
        request_data = request.get_json()
        data = {
            "ti_created_by": g.current_user.id,
            "ti_organization_id": g.current_user.organization_id,
            "ti_asset_id": asset_id,
            "ti_operator_id": request_data["ti_operator_id"],
            "ti_client_id": request_data["ti_client_id"],
            "ti_type": request_data["ti_type"],
            "ti_description": request_data["ti_description"],
            "ti_amount": request_data["ti_amount"],
            "ti_paid_amount": request_data.get("ti_paid_amount", 0),
        }
        result = qtrip.add_trip_income(data)
        trip_income = result.as_dict()
        return jsonify(trip_income=trip_income)


class TripExpense(Resource):
    def get(self, trip_id):
        expense = models.TripExpense.query.filter_by(
            te_organization_id=g.current_user.organization_id, te_trip_id=trip_id).order_by(
                models.TripExpense.id.desc()
            ).all()
        expense_list = [expense.as_dict() for expense in expense]
        return jsonify(expense_list)

    def post(self, trip_id):
        """ Add trip income """
        request_data = request.get_json()
        data = {
            "te_created_by": g.current_user.id,
            "te_organization_id": g.current_user.organization_id,
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
    def get(self, asset_id):
        expense = models.TripExpense.query.filter_by(
            te_organization_id=g.current_user.organization_id,
            te_asset_id=asset_id
        ).order_by(models.TripExpense.id.desc()).all()
        expense_list = [expense.as_dict() for expense in expense]
        return jsonify(expense_list)

    def post(self, asset_id):
        """ Add trip income by asset """
        request_data = request.get_json()
        data = {
            "te_created_by": g.current_user.id,
            "te_organization_id": g.current_user.organization_id,
            "te_asset_id": asset_id,
            "te_operator_id": request_data["te_operator_id"],
            "te_type": request_data["te_type"],
            "te_description": request_data["te_description"],
            "te_amount": request_data["te_amount"]
        }
        result = qtrip.add_trip_expense(data)
        trip_expense = result.as_dict()
        return jsonify(trip_expense=trip_expense)


class TripLocation(Resource):
    def get(self, trip_id):
        """ Get trip location by id """
        trip_locations = qtrip.get_trip_location_by_id(trip_id)
        trip_locations = [location.as_dict() for location in trip_locations] if trip_locations else []
        return jsonify(trip_locations=trip_locations)


class TripStops(Resource):
    def get(self, trip_id):
        """ Get stops by trip id """
        stops = qtrip.get_trip_stops_by_id(trip_id)
        stops_list = [stop.as_dict() for stop in stops] if stops else []
        return jsonify(stops=stops_list)


api_trips.add_resource(TripsByOrg, '/')
api_trips.add_resource(TripsByOrgOperator, '/operator/')
api_trips.add_resource(TripsByAsset, '/by_asset/')
api_trips.add_resource(TripsByUser, '/by_user/')
api_trips.add_resource(TripByStatus, '/status/')
api_trips.add_resource(TripById, '/<trip_id>/')
api_trips.add_resource(TripLocationByPhone, '/location_phone/<trip_id>/')
api_trips.add_resource(OdometerReading, '/odometer/')
api_trips.add_resource(Trip_Original_Fuel_Request, '/fuel_request/<trip_id>/')
api_trips.add_resource(Approve_Request, '/approve_request/')
api_trips.add_resource(Trip_income, '/income/<trip_id>/')
api_trips.add_resource(TripIncomeByAsset, '/asset_income/<asset_id>/')
api_trips.add_resource(TripExpense, '/expense/<trip_id>/')
api_trips.add_resource(TripExpenseByAsset, '/asset_expense/<asset_id>/')
api_trips.add_resource(TripLocation, '/location/<trip_id>/')
api_trips.add_resource(TripStops, '/stops/<trip_id>/')
