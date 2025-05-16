from sanasana import db
from sqlalchemy import func, cast, Float
from sanasana.models import Asset, Status, Organization, User, Operator, Trip
from sanasana import models
from datetime import datetime


def get_asset_by_id(org_id, id):
    act = Asset.query.filter_by(
        id=id, a_organisation_id=org_id
    ).first()
    return act


def get_asset_by_org(org_id):
    act = Asset.query.filter_by(
        a_organisation_id=org_id
    ).all()
    return act


def get_asset_count_by_org(org_id):
    count_of_assets = db.session.query(
        func.count(Asset.id)  # Replace Asset.id with the appropriate column if needed
    ).filter(Asset.a_organisation_id == org_id).scalar()

    return count_of_assets

def get_asset_value_sum_by_org(org_id):
    sum_of_values = db.session.query(
        func.sum(Asset.a_value)
    ).filter(Asset.a_organisation_id == org_id).scalar()

    return sum_of_values


def add_asset(data):
    asset = models.Asset()
    asset.a_created_by = data["a_created_by"]
    asset.a_organisation_id = data["a_organisation_id"]
    # asset.a_name = data["a_license_plate"]
    asset.a_make = data["a_make"]
    asset.a_model = data["a_model"]
    asset.a_year = data["a_year"]
    asset.a_license_plate = data["a_license_plate"]
    asset.a_fuel_type = data["a_fuel_type"]
    asset.a_tank_size = data["a_tank_size"]
    asset.a_displacement = data["a_displacement"]
    asset.a_mileage = data["a_mileage"]
    asset.a_horsepower = data["a_horsepower"]
    asset.a_acceleration = data["a_acceleration"]
    asset.a_insurance_expiry = data["a_insurance_expiry"]
    asset.a_status = data["a_status"]

    db.session.add(asset)
    db.session.commit()
    return asset


def add_status(data):
    status = Status()
    status.s_name = data["s_name"]
    status.s_name_code = data["s_name_code"]
    db.session.add(status)
    db.session.commit()
    return status


def update_asset(asset_id, data):
    asset = models.Asset.query.get(asset_id)
    if not asset:
        raise ValueError(f"Asset with ID {asset_id} not found")
    for key, value in data.items():
        if hasattr(asset, key):
            setattr(asset, key, value)
        else:
            raise ValueError(f"Invalid attribute '{key}' for asset model")
    db.session.commit()
    return asset


def delete_asset(asset_id):
    asset = models.Asset.query.get(asset_id)
    if not asset:
        raise ValueError(f"Asset with ID {asset_id} not found")
    db.session.delete(asset)
    db.session.commit()
    return asset


def add_invoice(asset_id, data):
    """
    Add a new invoice for a client.
    """
    invoice = models.TripIncome(ti_client_id=asset_id)
    for key, value in data.items():
        if hasattr(invoice, key):
            setattr(invoice, key, value)
        else:
            raise ValueError(f"Invalid attribute '{key}' for Invoice model")
    db.session.add(invoice)
    db.session.commit()
    return invoice


def add_asset_expense(asset_id, data):
    """
    Add a new invoice for a client.
    """
    invoice = models.TripIncome(ti_client_id=asset_id)
    for key, value in data.items():
        if hasattr(invoice, key):
            setattr(invoice, key, value)
        else:
            raise ValueError(f"Invalid attribute '{key}' for Invoice model")
    db.session.add(invoice)
    db.session.commit()
    return invoice



def get_internal_customer_metric_report(start_date, end_date):
    """
    Returns internal customer growth metrics within the specified date range.
    """
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

    # New Organizations
    # new_organizations = db.session.query(func.count(Organization.id))\
    #     .filter(Organization.created_at >= start_date,
    #             Organization.created_at <= end_date).scalar()

    # New Users
    # new_users = db.session.query(func.count(User.id))\
    #     .filter(User.created_at >= start_date,
    #             User.created_at <= end_date).scalar()

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
        # "new_organizations": new_organizations,
        # "new_users": new_users,
        "new_driver_organizations": new_operators,
        "total_trips": total_trips,
        "total_miles_covered": float(total_distance),
        "unique_vehicles": unique_vehicles,
        "unique_operators": unique_operators
    }
