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
        ).order_by(models.Trip.t_created_at.desc()).all()


def get_trip_by_user(org_id, user_id):  
    return models.Trip.query.filter_by(
        t_organization_id=org_id,
        t_operator_id=user_id
        ).all()


def get_trip_by_status(org_id, t_status):
    act = models.Trip.query.filter_by(
     t_organization_id=org_id, t_status=t_status
    ).order_by(models.Trip.t_created_at.desc()).all()
    return act


def get_trip_by_id_status(trip_id, t_status):
    act =models.Trip.query.filter_by(
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
    if not trip:
        return None
    # if data['attr'] == "resolved" and data["value"]:
    #     issue.resolved_date = datetime.datetime.utcnow()
    for attr, value in data.items():
        setattr(trip, attr, value)
    db.session.commit()
    return trip


def add_odometer_reading(data):
    odometer_reading = models.Odometer_readings()

    odometer_reading.or_created_by = data["or_created_by"]
    odometer_reading.or_organization_id = data["or_organization_id"]
    odometer_reading.or_trip_id = data["or_trip_id"]
    odometer_reading.or_asset_id = data["or_asset_id"]
    odometer_reading.or_operator_id = data["or_operator_id"]
    odometer_reading.or_image = data["or_image"]
    odometer_reading.or_by_drivers = data["or_by_drivers"]
    odometer_reading.or_reading = data["or_reading"]
    odometer_reading.or_latitude = data["or_latitude"]
    odometer_reading.or_longitude = data["or_longitude"]
    odometer_reading.or_description = data["or_description"]

    db.session.add(odometer_reading)
    db.session.commit()
    return odometer_reading


def add_trip_income(data):
    trip_income = models.TripIncome()
    trip_income.ti_created_by = data["ti_created_by"]
    trip_income.ti_organization_id = data["ti_organization_id"]
    trip_income.ti_trip_id = data["ti_trip_id"]
    trip_income.ti_operator_id = data["ti_operator_id"]
    trip_income.ti_asset_id = data["ti_asset_id"]
    trip_income.ti_client_id = data["ti_client_id"]
    trip_income.ti_type = data["ti_type"]
    trip_income.ti_amount = data["ti_amount"]
    trip_income.ti_description = data["ti_description"]

    db.session.add(trip_income)
    db.session.commit()
    return trip_income


def add_trip_expense(data):
    trip_expense = models.TripExpense()
    trip_expense.te_created_by = data["te_created_by"]
    trip_expense.te_organization_id = data["te_organization_id"]
    trip_expense.te_trip_id = data["te_trip_id"]
    trip_expense.te_operator_id = data["te_operator_id"]
    trip_expense.te_asset_id = data["te_asset_id"]
    trip_expense.te_type = data["te_type"]
    trip_expense.te_amount = data["te_amount"]
    trip_expense.te_description = data["te_description"]

    db.session.add(trip_expense)
    db.session.commit()
    return trip_expense
