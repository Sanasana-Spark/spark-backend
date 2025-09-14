from flask import (
    Blueprint,  jsonify, request, current_app, g
)
from flask_mail import Message
from flask_restful import Api, Resource
from werkzeug.utils import secure_filename
import requests
import os
from sanasana import db, mail
from sanasana.models import User, Organization
from sanasana.query import users as qusers
from sanasana.query import send_email as qsend_email


bp = Blueprint('public', __name__, url_prefix='/public')
api_public = Api(bp)


class Org(Resource):
    def get(self):
        Organizations = Organization.query.order_by(Organization.id.desc()).all()
        Organizations_list = [Organization.as_dict() for
                              Organization in Organizations]
        return jsonify(Organizations_list)
    
    def post(self):
        """ set up organisation and organisation admin
        """
        data = request.json

        orgdata = {
            "id": data.get('org_id'),
            "org_email": data.get('org_email'),
            "org_name": data.get('org_name'),
            "org_country": data.get('org_country'),
            "org_currency": data.get('org_currency'),
            "org_created_by": data.get('org_created_by'),
        }
        org = qusers.setup_org(orgdata)

        userdata = {
            "id": data.get('user_id'),
            "organization_id": data.get('organization_id'),
            "username": data.get('username'),
            "name": data.get('username'),
            "status": "Active",
            "email": data.get('email'),
            "is_organization_admin": data.get('is_organization_admin'),
            "role": data.get('role'),
            
        }
        user = qusers.setup_user(userdata)

        if user and org:
            # Send email to the user
            qsend_email.send_organization_creation_success_email(
                user.email, org.org_name
            )
    
        return jsonify(org.as_dict())
    
    
api_public.add_resource(Org, '/organization/')