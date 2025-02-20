from flask import (
    Blueprint,  jsonify, request
)
from flask_restful import Api, Resource
from werkzeug.utils import secure_filename
import os
from .. import db
from sanasana.models import User, Organization
from sanasana.query import users as qusers
import logging

bp = Blueprint('organizations', __name__, url_prefix='/organizations')
api_users = Api(bp)


class AllOrg(Resource):
    def get(self):
        Organizations = Organization.query.all()
        Organizations_list = [Organization.as_dict() for Organization in Organizations]
        return jsonify(Organizations_list)
    
    def post(self):
        data = request.json
        org_name = data.get('org_name')
        org_country = data.get('org_country')
        org_email = data.get('org_email')
        id = data.get('id')

        if not org_name:
            return jsonify({'error': 'Organization name is required'}), 400

        new_org = Organization(org_name=org_name, org_country=org_country, org_email=org_email, id=id)
        db.session.add(new_org)
        db.session.commit()

        return jsonify(new_org.as_dict())


class UserOrg(Resource):
    def get(self):
        user_id = request.args.get('user_id')
        email = request.args.get('user_email')
        user = User.query.filter_by(email=email, id=user_id).first()
        invited_user = User.query.filter_by(email=email).first()

        if user:
            user_org = Organization.query.filter_by(id=user.organization_id).first()
            return user_org.as_dict(), 200
        
        elif invited_user:
            invited_user.id = user_id
            db.session.add(invited_user)
            db.session.commit()

            user_org = Organization.query.filter_by(
                id=invited_user.organization_id
            ).first()
            return user_org.as_dict(), 200
        else:
            return ({'error': 'User does not have invite to any organization'}), 404       


class UsersByOrg(Resource):
    def get(self, org_id, admin_id):
        """ get users by id """
        users = [users.as_dict() for users in 
                 qusers.get_users_by_org(org_id)]
        return jsonify(users)
    
    def post(self, org_id, admin_id):
        """ invite user into an organisation """
        data = request.json
        email = data.get('email')
        username = data.get('username')
        organization_id = org_id
        user = User(email=email, username=username, organization_id=organization_id)

        db.session.add(user)
        db.session.commit()
        return jsonify(user.as_dict())


class UserById(Resource):
    def get(self, org_id, user_id):
        """ get users by id """
        users = [users.as_dict() for users in 
                 qusers.get_users_by_org(org_id)]
        return jsonify(users)


class UpdateUser(Resource):
    def put(self, org_id, email):
        data = request.json
        email = data.get('email')
        id = data.get('id')
        username = data.get('username')

        if not email or not username:
            return jsonify({'error': 'Email and username are required'}), 400

        user = User.query.filter_by(email=email, organization_id=org_id).first()

        if not user:
            return jsonify({'error': 'User does not have invite'}), 404

        user.id = id
        user.username = username
        db.session.commit()
 
        return jsonify({'message': 'User updated successfully'}), 200


api_users.add_resource(AllOrg, '/')
api_users.add_resource(UserOrg, '/user_org/')
api_users.add_resource(UsersByOrg, '/users/<org_id>/<admin_id>/')
api_users.add_resource(UpdateUser, '/update_user/<org_id>/<email>')