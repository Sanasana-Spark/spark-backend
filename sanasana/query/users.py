from sanasana import db
from sanasana.models import User

def get_user_by_id(org_id, id):
    return User.query.filter_by(
        id=id, organization_id=org_id).first()


def get_users_by_org(org_id):
    return User.query.filter_by(organization_id=org_id).all()


