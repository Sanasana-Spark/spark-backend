from flask import (
    Blueprint,  jsonify, request, abort
)
from werkzeug.utils import secure_filename
import os
from .. import  db
from sanasana.query import trips as qtrip
from sanasana.views import users as vuser
from sanasana.query.trips import Trip, get_trip_by_status, get_trip_by_id
from sanasana import models
from flask_restful import Api, Resource


bp = Blueprint('trips', __name__, url_prefix='/trips')

api_trips = Api(bp)


class TripsByOrg(Resource):
    def get(self, org_id):
        """ list all trips """
        trips = [trips.as_dict() for trips in 
                 qtrip.get_trip_by_org(org_id)]
        return jsonify(trips)
    

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
    
    def post(self):
        """ Add an trip """
        data = request.get_json()
        new_trip = qtrip.Trip(
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
            t_directionsResponse=data.get('t_directionsResponse'),      
            t_distance=data.get('t_distance') if 't_distance' in data else None,
            t_duration=data.get('t_duration'),
        )
        db.session.add(new_trip)
        db.session.commit()
        trip = new_trip.as_dict()
        return jsonify(**trip), 201


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
        data = request.json
        t_status = data.get('t_status')
        # if t_status is None:
        #     t_status = "In-Progress"
        trip = qtrip.update_status(trip_id, t_status)
        return jsonify(trip.as_dict())


api_trips.add_resource(TripsByOrg, '/<org_id>/')
api_trips.add_resource(TripsByUser, '/<org_id>/<user_id>/')
api_trips.add_resource(TripByStatus, '/status/<org_id>/<user_id>/<t_status>/')
api_trips.add_resource(TripById, '/<org_id>/<user_id>/<trip_id>/')



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
            t_start_elavation=data.get('t_start_elavation') if 't_start_elavation' in data else None,
            t_end_lat=data.get('t_end_lat'),
            t_end_long=data.get('t_end_long'),
            t_end_elavation=data.get('t_end_elavation')if 't_end_elavation' in data else None,
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