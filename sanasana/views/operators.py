from flask import Blueprint, jsonify, request, current_app, g
from werkzeug.utils import secure_filename
import os
import requests
from .. import db
from flask_restful import Api, Resource
from sanasana import models
from sanasana.query import operators as qoperator
from sanasana.query import users as qusers

bp = Blueprint("operators", __name__, url_prefix="/operators")
api_operators = Api(bp)


class AllOperators(Resource):
    def get(self):
        data = [
            operator.as_dict() for operator in qoperator.get_operator_by_org(g.current_user.organization_id)
        ]
        return jsonify(data)

    def post(self):
        data = request.get_json()
        data = {k.strip().lower(): v for k, v in data.items()}

        data["o_organisation_id"] = g.current_user.organization_id
        data["o_created_by"] = g.current_user.id
        result = qoperator.add_operator(data)

        operator = result.as_dict()
        
        #check if user already exists
        existing_user = qusers.get_user_by_email(data["o_email"])
        if existing_user:
            pass
        else:
            userdata = {
                "organization_id": g.current_user.organization_id,
                "email": data["o_email"],
                "role": "Driver",
                "phone": data["o_phone"],
                "name": data["o_name"],
                "username": data["o_name"],
                "status": "active",
            }
            qusers.add_user(userdata)

        # Send invitation to Clerk
        # Ensure the role is in lowercase and matches Clerk's expected format
        data["o_role"] = data["o_role"].strip().lower()
        if data["o_role"] == "driver":
            data["o_role"] = "org:operator"
        response = requests.post(
            f"https://api.clerk.com/v1/organizations/{g.current_user.organization_id}/invitations",
            headers={
                "Authorization": f"Bearer {current_app.config['CLERK_SECRET_KEY']}",
                "Content-Type": "application/json"
            },
            json={
                "email_address": data["o_email"],
                "role": data["o_role"],
                "inviter_user_id": g.current_user.id,
                "expires_in_days": 30,
                "redirect_url": "https://sanasanapwa.netlify.app/" 
                })
        return jsonify(operator=operator)


class OperatorById(Resource):
    def get(self, id):
        data = qoperator.get_operator_by_id(g.current_user.organization_id, id).as_dict()
        return jsonify(data)

    def put(self, id):
        print("getting operatorById")
        data = request.get_json()
        data = {k.strip().lower(): v for k, v in data.items()}

        # Add required fields to the existing data dictionary instead of overwriting
        data["o_organisation_id"] = g.current_user.organization_id
        data["id"] = id

        result = qoperator.update_operator(data)
        if not result:
            return jsonify(error="Operator not found"), 404

        operator = result.as_dict()
        return jsonify(operator=operator)

    def delete(self, id):
        """Delete operator"""
        result = qoperator.delete_operator(id)
        if result:
            return jsonify(message="Operator deleted successfully")
        else:
            return jsonify(message="Operator not found"), 404


class OperatorStatus(Resource):
    def get(self):
        statuses = models.Ostatus.query.all()
        status_list = [status.as_dict() for status in statuses]
        return jsonify(status_list)

    def post(self):
        data_request = request.get_json()
        data = {
            "o_name": data_request["o_name"],
            "o_name_code": data_request["o_name_code"],
        }
        result = qoperator.add_operator_status(data)
        status = result.as_dict()
        return jsonify(status=status)


api_operators.add_resource(AllOperators, "/")
api_operators.add_resource(OperatorById, "/<id>/")
api_operators.add_resource(OperatorStatus, "/status")
