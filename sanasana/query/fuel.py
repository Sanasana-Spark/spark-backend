from sanasana import db
from sqlalchemy import func
from datetime import datetime, timedelta
from sanasana.models import Fuel_request
from sanasana import models
from sanasana.query import trips as qtrip


def add(data):
    fuel_request = Fuel_request()
    fuel_request.f_trip_id = (data["f_trip_id"],)
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
    fuel_request.f_estimated_litres = data.get("f_estimated_litres", None)
    fuel_request.f_estimated_cost = data.get("f_estimated_cost", None)
    db.session.add(fuel_request)
    db.session.commit()
    return fuel_request


def get_fuel_request_by_trip(trip_id):
    fuel_request = Fuel_request.query.filter_by(f_trip_id=trip_id).first()
    return fuel_request


def get_fuel_cost_sum_by_org(org_id):
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    sum_of_values = (
        db.session.query(func.sum(Fuel_request.f_total_cost))
        .filter(
            Fuel_request.f_organization_id == org_id,
            Fuel_request.f_created_at >= seven_days_ago,
        )
        .scalar()
    )

    return sum_of_values


def get_fuel_request_by_org(org_id):
    act = Fuel_request.query.filter_by(f_organization_id=org_id).all()
    return act


def get_fuel_expenses_by_org(org_id, start_date=None, end_date=None):
    query = models.TripExpense.query.filter_by(
        te_organization_id=org_id, te_type="Fuel"
    )

    if start_date:
        query = query.filter(models.TripExpense.te_created_at >= start_date)
    if end_date:
        query = query.filter(models.TripExpense.te_created_at <= end_date)

    return query.all()


def calculate_carbon_emission(fuel_type, fuel_amount_litres):
    """
    Calculate CO₂ emissions based on fuel used.

    Parameters:
        distance_km (float): Distance travelled in kilometers.
        fuel_type (str): Type of fuel ('petrol', 'diesel', or 'lpg').
        fuel_amount_litres (float): Amount of fuel consumed in litres.

    Returns:
        float: CO₂ emissions in kilograms.
    """

    # Emission factors in kg CO₂ per litre
    emission_factors = {"petrol": 2.31, "diesel": 2.68, "lpg": 1.51}

    # Normalize fuel type and validate
    fuel_type = fuel_type.strip().lower()
    if fuel_type not in emission_factors:
        raise ValueError(
            f"Unsupported fuel type: {fuel_type}. Choose from 'petrol', 'diesel', 'lpg'."
        )

    emission_factor = emission_factors[fuel_type]
    print(f"Fuel type: {fuel_type}, Amount in litres: {fuel_amount_litres}, Emission factor: {emission_factor}")
    co2_emissions = float(fuel_amount_litres) * emission_factor

    return round(co2_emissions, 2)


def calculate_carbon_emission_distance_based(
    distance_km, fuel_consumption_rate, fuel_type
):
    """
    Calculate CO₂ emissions based on distance and fuel consumption rate.

    Parameters:
        distance_km (float): Distance travelled in kilometers.
        fuel_consumption_rate (float): Fuel consumption rate in liters/km (or L/100km ÷ 100).
        fuel_type (str): Type of fuel ('petrol', 'diesel', or 'lpg').

    Returns:
        float: CO₂ emissions in kilograms.
    """
    emission_factors = {"petrol": 2.31, "diesel": 2.68, "lpg": 1.51}

    fuel_type = fuel_type.strip().lower()
    if fuel_type not in emission_factors:
        raise ValueError(
            f"Unsupported fuel type: {fuel_type}. Choose from 'petrol', 'diesel', 'lpg'."
        )
    if isinstance(distance_km, str):
        distance_km = distance_km.lower().replace("km", "").strip()
        distance_km = float(distance_km)
    print(f"Distance in km: {distance_km}, Fuel consumption rate: {fuel_consumption_rate}, Fuel type: {fuel_type}") 

    fuel_used = distance_km * fuel_consumption_rate
    co2_emissions = fuel_used * emission_factors[fuel_type]

    return round(co2_emissions, 2)


def calculate_carbon_emission_efficiency_based(
    distance_km, fuel_efficiency_kmpl, fuel_type
):
    """
    Calculate CO₂ emissions based on distance and fuel efficiency.

    Parameters:
        distance_km (float): Distance travelled in kilometers.
        fuel_efficiency_kmpl (float): Fuel efficiency in km/liter.
        fuel_type (str): Type of fuel ('petrol', 'diesel', or 'lpg').

    Returns:
        float: CO₂ emissions in kilograms.
    """
    emission_factors = {"petrol": 2.31, "diesel": 2.68, "lpg": 1.51}

    fuel_type = fuel_type.strip().lower()
    if fuel_type not in emission_factors:
        raise ValueError(
            f"Unsupported fuel type: {fuel_type}. Choose from 'petrol', 'diesel', 'lpg'."
        )

    # Handle distance_km as string with "km" or as a number
    if isinstance(distance_km, str):
        distance_km = distance_km.lower().replace("km", "").strip()
        distance_km = float(distance_km)
    fuel_used = distance_km / float(fuel_efficiency_kmpl)
    co2_emissions = fuel_used * emission_factors[fuel_type]

    return round(co2_emissions, 2)


def calculate_f_litres(org_id, trip_id):
    trip = qtrip.get_trip_by_id(trip_id).as_dict()
    efficiency_rate = float(trip['a_efficiency_rate']) if trip['a_efficiency_rate'] else 4.0  # Default to 4.0 if not set
    if isinstance(trip['t_distance'], str):
        distance_km = trip['t_distance'].lower().replace("km", "").strip()
        distance_km = float(distance_km)

    # Assuming a simple calculation where fuel consumption might be affected by the load
    base_estimated_litres = round(distance_km / efficiency_rate, 2)
    # additional_consumption = load * (0.05 * base_estimated_litres)
    # consumption = base_estimated_litres - additional_consumption
    cost_per_litre = get_fuel_price(org_id, trip['a_fuel_type'])

    estimated_litres = base_estimated_litres
    estimated_cost = round(estimated_litres * cost_per_litre, 2)
    return estimated_litres, estimated_cost


def get_fuel_price(org_id, f_type):
    org = models.Organization.query.filter_by(id=org_id).first()
    petrol_price = org.org_petrol_price if org else 0
    diesel_price = org.org_diesel_price if org else 0

    f_type = f_type.strip().lower()
    if f_type == "petrol":
        fuel_price = petrol_price
    elif f_type == "diesel":
        fuel_price = diesel_price
    else:
        fuel_price = diesel_price
    return fuel_price if fuel_price else None
