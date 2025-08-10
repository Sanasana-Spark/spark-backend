from datetime import datetime, timedelta
from sanasana.models import Organization, User, Operator, Trip
from sanasana import db
from sqlalchemy import func, cast, Float


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

