from flask import (
    Blueprint,  jsonify, request
)
from werkzeug.utils import secure_filename
import os
from .. import  db
from sanasana.models.trips import Trip, Tstatus

bp = Blueprint('trips', __name__, url_prefix='/trips')


@bp.route('/')
def get_trips():
    trips = Trip.query.all()
    trips_list = [trip.as_dict() for trip in trips]
    return jsonify(trips_list)

@bp.route('/<userEmail>', methods=['GET'])
def get_tripByUser(userEmail):
    trip = Trip.query(Trip).filter(Trip.t_o_email == userEmail).first()
    return jsonify(trip)


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
        required_fields = ['t_organization_id', 't_created_by', 't_directionsResponse']
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
            t_directionsResponse=data.get('t_directionsResponse'),      
            t_distance=data.get('t_distance') if 't_distance' in data else None,
            t_duration=data.get('t_duration'),

        )

        db.session.add(new_trip)
        db.session.commit()

        return jsonify(new_trip.as_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:trip_id>', methods=['PUT'])
def update_trip(trip_id):
    trip = Trip.query.get(trip_id)   
    if not trip:
        return jsonify({'error': 'Trip not found'}), 404
    try:
        data = request.get_json()
        # Loop through each attribute and value in the JSON data
        for attribute, value in data.items():
            if hasattr(trip, attribute):
                setattr(trip, attribute, value)
            else:
                return jsonify({'error': f'Invalid attribute: {attribute}'}), 400
        db.session.commit()
        return jsonify({'message': 'Trip updated successfully'}), 200
    except Exception as e:
        db.session.rollback()  # Rollback in case of any errors
        return jsonify({'error': 'Failed to update trip' + str(e)}), 500
    


@bp.route('/distance')
def calculate_distance():
    return 1


@bp.route('/fuel')
def calculate_fuel():
    return 1