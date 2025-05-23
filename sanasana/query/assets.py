from sanasana import db
from sqlalchemy import func, and_, cast, Float, String
from sanasana.models import Asset, Status, Trip, TripIncome, TripExpense
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



def get_asset_performance(org_id, start_date, end_date):
    """
    Returns performance summary of each asset within the specified date range.
    """
    org_currency = db.session.query(
        models.Organization.org_currency
    ).filter(
        models.Organization.id == org_id
    ).first()
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

    # Subqueries with CAST
    trip_subq = db.session.query(
        Trip.t_asset_id.label("asset_id"),
        func.count(Trip.id).label("trip_count"),
        func.coalesce(
            func.sum(
                cast(
                    func.regexp_replace(Trip.t_distance, r'[^0-9\.]', '', 'g'),
                    Float
                )
            ), 0
        ).label("mileage_km"),
        func.coalesce(func.sum(cast(Trip.t_actual_fuel, Float)), 0).label("fuel_consumed_ltr"),
        func.coalesce(func.sum(cast(Trip.t_actual_cost, Float)), 0).label("fuel_cost")
    ).filter(
        and_(
            Trip.t_created_at >= start_date,
            Trip.t_created_at <= end_date,
            Trip.t_organization_id == org_id
        )
    ).group_by(Trip.t_asset_id).subquery()
    
    income_subq = db.session.query(
        TripIncome.ti_asset_id.label("asset_id"),
        func.coalesce(func.sum(cast(TripIncome.ti_amount, Float)), 0).label("total_revenue")
    ).filter(
        and_(
            TripIncome.ti_created_at >= start_date,
            TripIncome.ti_created_at <= end_date
        )
    ).group_by(TripIncome.ti_asset_id).subquery()

    expense_subq = db.session.query(
        TripExpense.te_asset_id.label("asset_id"),
        func.coalesce(func.sum(cast(TripExpense.te_amount, Float)), 0).label("total_expense")
    ).filter(
        and_(
            TripExpense.te_created_at >= start_date,
            TripExpense.te_created_at <= end_date
        )
    ).group_by(TripExpense.te_asset_id).subquery()

    # Main query joining all subqueries
    results = db.session.query(
        Asset.id.label("asset_id"),
        Asset.a_make.label("a_make"),
        Asset.a_model.label("a_model"),
        Asset.a_year.label("a_year"),
        Asset.a_license_plate.label("a_license_plate"),
        Asset.a_fuel_type.label("a_fuel_type"),
        func.coalesce(trip_subq.c.trip_count, 0).label("trip_count"),
        func.coalesce(trip_subq.c.mileage_km, 0.0).label("mileage_km"),
        func.coalesce(trip_subq.c.fuel_consumed_ltr, 0.0).label("fuel_consumed_ltr"),
        func.coalesce(trip_subq.c.fuel_cost, 0.0).label("fuel_cost"),
        func.coalesce(income_subq.c.total_revenue, 0.0).label("total_revenue"),
        func.coalesce(expense_subq.c.total_expense, 0.0).label("total_expense")
    ).outerjoin(trip_subq, trip_subq.c.asset_id == Asset.id)\
     .outerjoin(income_subq, income_subq.c.asset_id == Asset.id)\
     .outerjoin(expense_subq, expense_subq.c.asset_id == Asset.id)\
     .all()

    # Format results
    report = []
    for row in results:
        mileage = row.mileage_km or 0
        fuel = row.fuel_consumed_ltr or 0
        fuel_economy = round(fuel / mileage, 2) if mileage > 0 else 0

        report.append({
            "asset id": row.asset_id,
            "Make": row.a_make,
            "Model": row.a_model,
            "Year": row.a_year,
            "License Plate": row.a_license_plate,
            "Fuel Type": row.a_fuel_type,
            "No of trips": row.trip_count,
            "Mileage (Km)": f"{float(row.mileage_km or 0)} km",
            "Fuel Consumed (Ltr)": f"{float(row.fuel_consumed_ltr)} ltr",
            "fuel_economy": fuel_economy,
            f"fuel_cost-{org_currency}": float(row.fuel_cost),
            f"total_revenue-{org_currency}": float(row.total_revenue),
            f"total_expense-{org_currency}": float(row.total_expense),
            f"profit-{org_currency}": float(row.total_revenue - row.total_expense)
        })

    return report
