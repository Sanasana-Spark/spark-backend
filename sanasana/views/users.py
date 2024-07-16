from flask import (
    Blueprint,  jsonify, request
)
from werkzeug.utils import secure_filename
import os
from sanasana.views.db import get_db as db
from sanasana.models.users import User, Organization

bp = Blueprint('organizations', __name__, url_prefix='/organizations')

@bp.route('/create-organization', methods=['POST'])
def create_organization():
    data = request.json
    user_id = data['userId']
    user_name = data['userName']
    email = data['email']
    organization_id = data['organizationId']
    organization_name = data['organizationName']

    organization = Organization(id=organization_id, name=organization_name)
    db.add(organization)
    
    user = User(id=user_id, username=user_name, email=email, firm_id=organization_id )
    db.add(user)
    db.commit()

    return jsonify({'message': 'Organization created successfully'})

@bp.route('/api/invite-user', methods=['POST'])
def invite_user():
    data = request.json
    email = data['email']
    organization_id = data['organizationId']

    # Logic to send invitation email with organization_id

    return jsonify({'message': 'User invited successfully'})


@bp.route('/organizations/<user_id>', methods=['GET'])
def get_organization(user_id):
    user = User.query(User).filter(User.id == user_id).first()
    if user and user.firm_id:
        organization = Organization.query(Organization).filter(Organization.id == user.firm_id).first()
        if organization:
            return jsonify({
                'id': Organization.id,
                'name': Organization.f_name,
            })
    return jsonify({'error': 'Organization not found'}), 404