from sanasana import db
from sanasana import models


def get_all_trips():
    return Trip.query.all()

def add_trip(data):
    trip = models.Trip()
    trip.t_created_by = data["t_created_by"]
    trip.t_organization_id = data["t_organization_id"]
    trip.t_type = data["t_type"]
    trip.t_start_lat = data["t_start_lat"]
    trip.t_start_long = data["t_start_long"]
    trip.t_start_elavation = data["t_start_elavation"]
    trip.t_end_lat = data["t_end_lat"]
    trip.t_end_long = data["t_end_long"]
    trip.t_end_elavation = data["t_end_elavation"]
    trip.t_start_date = data["t_start_date"]
    trip.t_end_date = data["t_end_date"]
    trip.t_operator_id = data["t_operator_id"]
    trip.t_asset_id = data["t_asset_id"]
    trip.t_status = data["t_status"]
    trip.t_load = data["t_load"]
    trip.t_origin_place_id = data["t_origin_place_id"]
    trip.t_origin_place_query = data["t_origin_place_query"]
    trip.t_destination_place_id = data["t_destination_place_id"]
    trip.t_destination_place_query = data["t_destination_place_query"]
    # trip.t_directionsResponse = data["t_directionsResponse"]
    trip.t_distance = data.get("t_distance")
    trip.t_duration = data["t_duration"]

    db.session.add(trip)
    db.session.commit()
    return trip


def get_trip_by_id(trip_id):
    return models.Trip.query.filter_by(
        id=trip_id).first()


def get_trip_by_org(org_id):  
    return models.Trip.query.filter_by(
        t_organization_id=org_id
        ).all()


def get_trip_by_user(org_id, user_id):  
    return models.Trip.query.filter_by(
        t_organization_id=org_id,
        t_operator_id=user_id
        ).all()


def get_trip_by_status(org_id, t_status):
    act = models.Trip.query.filter_by(
     t_organization_id=org_id, t_status=t_status
    ).all()
    return act


def get_trip_by_id_status(trip_id, t_status):
    act =models. Trip.query.filter_by(
        id=trip_id, t_status=t_status
    ).first()
    return act


def update_status(trip_id, t_status):
    trip = models.Trip.query.filter_by(
        id=trip_id
    ).first()
    trip.t_status = t_status
    db.session.add(trip)
    db.session.commit()
    return trip


def update(trip_id, data):
    trip = models.Trip.query.filter_by(
        id=trip_id
    ).first()
    # if data['attr'] == "resolved" and data["value"]:
    #     issue.resolved_date = datetime.datetime.utcnow()
    setattr(trip, data['attr'], data['value'])
    db.session.add(trip)
    db.session.commit()
    return trip