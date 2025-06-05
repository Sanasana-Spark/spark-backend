from sanasana import db
from sanasana import models
from datetime import datetime
from sqlalchemy import func, cast, Float
from sanasana.models import Organization, User, Operator, Trip
from sqlalchemy.orm import aliased


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
    TripIncomeAlias = aliased(models.TripIncome)
    TripExpenseAlias = aliased(models.TripExpense)

    result = db.session.query(
        models.Trip,
        func.coalesce(func.sum(TripIncomeAlias.ti_amount), 0.0).label("t_income"),
        func.coalesce(func.sum(TripExpenseAlias.te_amount), 0.0).label("t_expense")
    ).outerjoin(
        TripIncomeAlias, models.Trip.id == TripIncomeAlias.ti_trip_id
    ).outerjoin(
        TripExpenseAlias, models.Trip.id == TripExpenseAlias.te_trip_id
    ).filter(
        models.Trip.id == trip_id
    ).group_by(
        models.Trip.id
    ).first()

    if result:
        trip, t_income, t_expense = result
        trip.t_income = t_income
        trip.t_expense = t_expense
        return trip


def get_trip_by_org(org_id):
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
    ).filter(
        models.Trip.t_organization_id == org_id
    ).group_by(
        models.Trip.id
    ).order_by(
        models.Trip.t_created_at.desc()
    ).all()
    trips = []
    for trip, t_income, t_expense in trips_data:
        trip.t_income = t_income
        trip.t_expense = t_expense
        trips.append(trip)
    return trips


def get_trip_by_user(org_id, user_id):  
    return models.Trip.query.filter_by(
        t_organization_id=org_id,
        t_operator_id=user_id
        ).order_by(models.Trip.id.desc()).all()


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
    for key, value in data.items():
        if not hasattr(trip_income, key):
            raise ValueError(f"Invalid attribute '{key}' for TripExpense model")
        setattr(trip_income, key, value)
    
    db.session.add(trip_income)
    db.session.commit()
    return trip_income


def add_trip_expense(data):
    trip_expense = models.TripExpense()

    for key, value in data.items():
        if not hasattr(trip_expense, key):
            raise ValueError(f"Invalid attribute '{key}' for TripExpense model")
        setattr(trip_expense, key, value)

    db.session.add(trip_expense)
    db.session.commit()
    return trip_expense


def get_internal_customer_metric_report(start_date, end_date):
    """
    Returns internal customer growth metrics within the specified date range.
    """
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

    # # New Organizations
    new_organizations = db.session.query(func.count(Organization.id))\
        .filter(Organization.org_created_at >= start_date,
                Organization.org_created_at <= end_date).scalar()

    # # New Users
    new_users = db.session.query(func.count(User.id))\
        .filter(User.created_at >= start_date,
                User.created_at <= end_date).scalar()

    # New Driver Organizations (Operators)
    new_operators = db.session.query(func.count(Operator.id))\
        .filter(Operator.o_created_at >= start_date,
                Operator.o_created_at <= end_date).scalar()

    # Total Trips Made
    total_trips = db.session.query(func.count(Trip.id))\
        .filter(Trip.t_created_at >= start_date,
                Trip.t_created_at <= end_date).scalar()

    # Total Miles Covered (clean and sum t_distance)
    total_distance = db.session.query(
        func.coalesce(
            func.sum(
                cast(
                    func.regexp_replace(Trip.t_distance, r'[^0-9\.]', '', 'g'),
                    Float
                )
            ), 0.0)
    ).filter(Trip.t_created_at >= start_date,
             Trip.t_created_at <= end_date).scalar()

    # Unique Vehicles Used (by t_asset_id)
    unique_vehicles = db.session.query(func.count(func.distinct(Trip.t_asset_id)))\
        .filter(Trip.t_created_at >= start_date,
                Trip.t_created_at <= end_date).scalar()

    # Unique Operators in Trips (by t_operator_id)
    unique_operators = db.session.query(func.count(func.distinct(Trip.t_operator_id)))\
        .filter(Trip.t_created_at >= start_date,
                Trip.t_created_at <= end_date).scalar()

    return {
        "new_organizations": new_organizations,
        "new_users": new_users,
        "new_driver_organizations": new_operators,
        "total_trips": total_trips,
        "total_miles_covered": float(total_distance),
        "unique_vehicles": unique_vehicles,
        "unique_operators": unique_operators
    }

