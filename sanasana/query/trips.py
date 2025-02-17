from sanasana import db
from sanasana.models import Trip


def get_all_trips():
    return Trip.query.all()


def get_trip_by_id(trip_id):
    return Trip.query.filter_by(
        id=trip_id).first()


def get_trip_by_org(org_id):  
    return Trip.query.filter_by(
        t_organization_id=org_id
        ).all()


def get_trip_by_user(org_id, user_id):  
    return Trip.query.filter_by(
        t_organization_id=org_id,
        t_operator_id=user_id
        ).all()


def get_trip_by_status(org_id, t_status):
    act = Trip.query.filter_by(
     t_organization_id=org_id, t_status=t_status
    ).all()
    return act


def get_trip_by_id_status(trip_id, t_status):
    act = Trip.query.filter_by(
        id=trip_id, t_status=t_status
    ).first()
    return act


def update_status(trip_id, t_status):
    trip = Trip.query.filter_by(
        id=trip_id
    ).first()
    trip.t_status = t_status
    db.session.add(trip)
    db.session.commit()
    return trip


def update(trip_id, data):
    trip = Trip.query.filter_by(
        id=trip_id
    ).first()
    # if data['attr'] == "resolved" and data["value"]:
    #     issue.resolved_date = datetime.datetime.utcnow()
    setattr(trip, data['attr'], data['value'])
    db.session.add(trip)
    db.session.commit()
    return trip