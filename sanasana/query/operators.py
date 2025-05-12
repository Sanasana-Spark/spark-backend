from sanasana import db
from sqlalchemy import func
from sanasana import models
from sanasana.models import Operator, Ostatus


def get_operator_by_id(org_id, id):
    act = Operator.query.filter_by(id=id, o_organisation_id=org_id).first()
    return act


def get_operator_by_org(org_id):
    act = Operator.query.filter_by(o_organisation_id=org_id).all()
    return act


def add_operator(data):
    operator = Operator()
    operator.o_assigned_asset = data["o_assigned_asset"]
    operator.o_created_by = data["o_created_by"]
    operator.o_cum_mileage = data["o_cum_mileage"]
    operator.o_email = data["o_email"]
    operator.o_expirence = data["o_expirence"]
    operator.o_lincense_expiry = data["o_lincense_expiry"]
    operator.o_lincense_id = data["o_lincense_id"]
    operator.o_lincense_type = data["o_lincense_type"]
    operator.o_name = data["o_name"]
    operator.o_national_id = data["o_national_id"]
    operator.o_organisation_id = data["o_organisation_id"]
    operator.o_phone = data["o_phone"]
    operator.o_role = data["o_role"]
    operator.o_status = data["o_status"]

    db.session.add(operator)
    db.session.commit()
    return operator


def delete_operator(operator_id):
    operator = models.Operator.query.get(operator_id)
    if not operator:
        raise ValueError(f"Asset with ID {operator_id} not found")
    db.session.delete(operator)
    db.session.commit()
    return operator


def add_operator_status(data):
    status = Ostatus()
    status.o_name = data["o_name"]
    status.o_name_code = data["o_name_code"]
    db.session.add(status)
    db.session.commit()
    return status


def update_operator(data):
    operator = Operator.query.filter_by(
        id=data["id"], o_organisation_id=data["o_organisation_id"]
    ).first()

    if operator:
        for key, value in data.items():
            if hasattr(operator, key) and key != "id":
                setattr(operator, key, value)
        db.session.commit()
    return operator
