from sanasana import db
from sanasana.models import User
from sanasana import models

def get_user_by_id(org_id, id):
    return User.query.filter_by(
        id=id, organization_id=org_id).first()


def get_users_by_org(org_id):
    return User.query.filter_by(organization_id=org_id).order_by(models.User.default_id.desc()).all()


def add_user(data):

    user = models.User()
    user.organization_id = data["organization_id"]
    user.email = data["email"]
    user.role = data["role"]
    user.phone = data["phone"]
    user.status = data["status"]
    user.name = data["name"]
    user.username = data["username"]

    db.session.add(user)
    db.session.commit()
    return user


def setup_org(data):
    org = models.Organization()
    for attr in data:
        setattr(org, attr, data[attr])  # Set attributes dynamically
    db.session.add(org)
    db.session.commit()
    return org


def setup_user(data):
    user = models.User()
    for attr in data:
        setattr(user, attr, data[attr])
    db.session.add(user)
    db.session.commit()
    return user
