from datetime import datetime
from sanasana.models import Organization, User, Operator, Trip, Maintenance, Asset
from sanasana import db
from sqlalchemy import func, cast, Float
from flask import jsonify


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


def get_report(org_id, start_date, end_date):

    # Validate date inputs
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
    except Exception:
        return jsonify(error="Invalid date format. Use YYYY-MM-DD."), 400

    # Query with joins and filtering
    results = (
        db.session.query(Maintenance, User.name, Asset.a_license_plate)
        .join(User, User.id == Maintenance.m_created_by)
        .join(Asset, Asset.id == Maintenance.m_asset_id)
        .filter(
            Maintenance.m_organisation_id == org_id,
            Maintenance.m_date.between(start, end)
        )
        .order_by(Maintenance.m_date.desc())
        .all()
    )

    # Format results
    maintenance_list = []
    for maintenance, created_by_name, license_plate in results:
        maintenance_list.append({
            "created_by": created_by_name,
            "asset_License": license_plate,
            "type": maintenance.m_type,
            "description": maintenance.m_description,
            "date": maintenance.m_date.strftime('%d/%m/%Y') if maintenance.m_date else None,
            "total_cost": maintenance.m_total_cost,
            "insurance_coverage": maintenance.m_insurance_coverage,
            "status": maintenance.m_status,
        })

    return maintenance_list


