from flask import (
    Blueprint,  jsonify, request
)
from werkzeug.utils import secure_filename
import os
from .. import  db
from sanasana.models.trips import Trip

bp = Blueprint('trips', __name__, url_prefix='/trips')


@bp.route('/')
def get_trips():
    trips = Trip.query.all()
    trips_list = [trip.as_dict() for trip in trips]
    return jsonify(trips_list)


@bp.route('/create', methods=['POST'])
def add_trip():
    try:
        data = request.form.to_dict()
        required_fields = ['t_start_lat', 't_start_long', 't_end_lat', 't_end_long']

        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

        new_trip = Trip(
            t_firm_id=data['t_firm_id'],
            t_type=data['t_type'],
            t_start_lat=(data['t_start_lat']),
            t_start_long=data['t_start_long'],
            t_start_elavation=data['t_start_elavation'],
            t_end_lat=(data['t_end_lat']),
            t_end_long=data['t_end_long'],
            t_end_elavation=(data['t_end_elavation']),
            t_distance=float(data['t_distance']),
            t_start_date=(data['t_start_date']),
            t_end_date=data['t_end_date'],
            t_operator_id=(data['t_operator_id']),
            t_asset_id=(data['t_asset_id']),
            t_status=(data['t_status']),
            t_load=(data['t_load']),
        )

        db.session.add(new_trip)
        db.session.commit()

        return jsonify(new_trip.as_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


