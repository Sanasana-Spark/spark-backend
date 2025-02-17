from sanasana import db
from sqlalchemy import func
from sanasana.models import Asset 


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
