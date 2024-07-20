from flask import (
    Blueprint,  jsonify, request
)
from werkzeug.utils import secure_filename
import os
from .. import db
from sanasana.models.users import User, Organization
import logging

bp = Blueprint('organizations', __name__, url_prefix='/organizations')


@bp.route('/')
def get_organizations():
    Organizations = Organization.query.all()
    Organizations_list = [Organization.as_dict() for Organization in Organizations]
    return jsonify(Organizations_list)


@bp.route('/users')
def get_users():
    users = User.query.all()
    users_list = [user.as_dict() for user in users]
    return jsonify(users_list)


@bp.route('/create-organization', methods=['POST'])
def create_organization():
    try:
        data = request.json
        user_id = data['userId']
        user_name = data['userName']
        email = data['email']
        organization_id = data['organizationId']
        organization_name = data['organizationName']

        # Check if organization already exists
        organization = Organization.query.filter_by(id=organization_id).first()
        
        if not organization:
            # Create new organization if it doesn't exist
            organization = Organization(id=organization_id, org_name=organization_name)
            db.session.add(organization)
            db.session.commit()

        # Check if user already exists
        existing_user = User.query.filter_by(id=user_id).first()
        if existing_user:
            return jsonify({'error': 'User already exists'}), 400

        # Create user and associate with the organization
        user = User(id=user_id, username=user_name, email=email, organization_id=organization_id)
        db.session.add(user)
        db.session.commit()

        return jsonify({'message': 'Organization and user created successfully'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/invite-user', methods=['POST'])
def invite_user():
    data = request.json
    email = data['email']
    organization_id = data['organizationId']

    # Logic to send invitation email with organization_id

    return jsonify({'message': 'User invited successfully'})


@bp.route('/organizations/<userId>', methods=['GET'])
def get_organization(userId):
    user = User.query(User).filter(User.id == userId).first()
    if user and user.organization_id:
        organization = Organization.query(Organization).filter(Organization.id == user.organization_id).first()
        # if organization:
        #     return jsonify({
        #         'id': organization.id,
        #         'org_name': organization.org_name
        #     })
        if organization:
            response = {
                'id': organization.id,
                'org_name': organization.org_name
            }
            logging.info(f'Response: {response}')  # Add logging
            return 3
    return jsonify({'error': 'Organization not found'}), 404