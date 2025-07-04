from sanasana import db
from sqlalchemy import func
from datetime import datetime, timedelta
from sanasana.models import Fuel_request


def add(data):
    fuel_request = Fuel_request()
    fuel_request.f_trip_id = data["f_trip_id"],
    fuel_request.f_organization_id = data["f_organization_id"]
    fuel_request.f_created_by = data["f_created_by"]
    fuel_request.f_asset_id = data["f_asset_id"]
    fuel_request.f_operator_id = data["f_operator_id"]
    fuel_request.f_litres = data["f_litres"]
    fuel_request.f_cost = data["f_cost"]
    fuel_request.f_total_cost = data["f_total_cost"]
    fuel_request.f_distance = data["f_distance"]
    fuel_request.f_type = data["f_type"]
    fuel_request.f_request_type = data["f_request_type"]
    db.session.add(fuel_request)  
    db.session.commit()
    return fuel_request


def get_fuel_cost_sum_by_org(org_id):
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    sum_of_values = db.session.query(
        func.sum(Fuel_request.f_total_cost)
    ).filter(
        Fuel_request.f_organization_id == org_id,
        Fuel_request.f_created_at >= seven_days_ago
        ).scalar()

    return sum_of_values


def get_fuel_request_by_org(org_id):
    act = Fuel_request.query.filter_by(
        f_organization_id=org_id
    ).all()
    return act