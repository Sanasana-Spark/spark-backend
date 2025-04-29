from sanasana import db
from sqlalchemy import func
from sanasana.models import Asset, Status
from sanasana import models


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


def update_asset(data):
    asset = Asset.query.filter_by(
        id=data["id"],
        a_organisation_id=data["a_organisation_id"]
        ).first()
    if asset:
        for key, value in data.items():
            if hasattr(asset, key) and key != "id":
                setattr(asset, key, value)
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
