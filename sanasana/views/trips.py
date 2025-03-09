from flask import (
    Blueprint,  jsonify, request, abort
)
from werkzeug.utils import secure_filename
import os
from .. import  db
from sanasana.query import trips as qtrip
from sanasana import models
from sanasana.query import resources as qresources
from flask_restful import Api, Resource
from flask_cors import CORS
# import pandas as pd


bp = Blueprint('trips', __name__, url_prefix='/trips')

api_trips = Api(bp)


class TripsByOrg(Resource):
    def get(self, org_id, user_id):
        """ list all trips """
        trips = [trips.as_dict() for trips in 
                 qtrip.get_trip_by_org(org_id)]
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
            "t_duration": request_data["t_duration"]
        }

        result = qtrip.add_trip(data)
        trip = result.as_dict()
        return jsonify(trip=trip)


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
        trip = qtrip.get_trip_by_id(trip_id)    
        return jsonify(trip.as_dict())
    
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
                "t_start_od_reading_url": or_image_url
            }
            for attribute, value in request_data.items():
                if attribute in ["t_status", "t_start_date"]:
                    data[attribute] = value
                qtrip.update(trip_id, data)
        elif description == "complete_trip":
            data = {
                "t_end_od_reading": float(request_data["or_by_drivers"]),
                "t_end_od_reading_url": or_image_url
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


class TripReport(Resource):
    def get(self, org_id):
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = models.Trip.query.filter_by(t_organization_id=org_id)

        if start_date and end_date:
            query = query.filter(models.Trip.t_created_at.between(start_date, end_date))

        trips = query.all()
        return jsonify([trip.as_dict() for trip in trips])


# class ExportTripReport(Resource):
#     def get(self):
#         org_id = request.args.get('organization_id')
#         start_date = request.args.get('start_date')
#         end_date = request.args.get('end_date')

#         query = Trip.query.filter(Trip.t_organization_id == org_id)
#         if start_date and end_date:
#             query = query.filter(Trip.t_created_at.between(start_date, end_date))

#         trips = [trip.as_dict() for trip in query.all()]
#         df = pd.DataFrame(trips)

#         file_path = "trip_report.xlsx"
#         df.to_excel(file_path, index=False)

#         return jsonify({"message": "Report generated", "file": file_path})

api_trips.add_resource(TripsByOrg, '/<org_id>/<user_id>/')
api_trips.add_resource(TripsByUser, '/by_user/<org_id>/<user_id>/')
api_trips.add_resource(TripByStatus, '/status/<org_id>/<user_id>/<t_status>/')
api_trips.add_resource(TripById, '/<org_id>/<user_id>/<trip_id>/')
api_trips.add_resource(OdometerReading, '/odometer/<org_id>/<user_id>/')
api_trips.add_resource(TripReport, '/reports/<org_id>/')
# api_trips.add_resource(ExportTripReport, '/reports/export/')



def get_trip_column(trip_id, column_name):
    trip = Trip.query.get(trip_id)
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