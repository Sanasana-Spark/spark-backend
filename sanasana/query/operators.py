from sanasana import db
from sqlalchemy import func
from sanasana.models import Operator


def get_operator_by_id(org_id, id):
    act = Operator.query.filter_by(
        id=id, o_organisation_id=org_id
    ).first()
    return act


def get_operator_by_org(org_id):
    act = Operator.query.filter_by(
        o_organisation_id=org_id
    ).all()
    return act