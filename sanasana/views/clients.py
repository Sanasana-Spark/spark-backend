import datetime
from flask import (
    Blueprint,  jsonify, request, abort
)
from sanasana import models
from sanasana.query import clients as qclients
from flask_restful import Api, Resource
from flask_cors import CORS
from sqlalchemy import and_
# import pandas as pd


bp = Blueprint('clients', __name__, url_prefix='/clients')

api_clients = Api(bp)


class ClientsByOrg(Resource):
    def get(self, org_id, user_id):
        """ list all clients """
        clients = models.Client.query.filter_by(
            c_organization_id=org_id
        ).all()
        clients = [client.as_dict() for client in clients]
        return jsonify(clients=clients)
    
    def post(self, org_id, user_id):
        """ Add a client """
        request_data = request.get_json()

        data = {
            "c_created_by": user_id,
            "c_organization_id": org_id,
            "c_name": request_data["c_name"],
            "c_email": request_data["c_email"],
            "c_phone": request_data["c_phone"],
        }

        result = qclients.add_client(data)
        client = result.as_dict()
        return jsonify(client=client)
    

class Invoices(Resource):
    def get(self, org_id, user_id):
        """ list all clients """
        invoices = models.TripIncome.query.filter_by(
            ti_organization_id=org_id
        ).all()
        invoices = [invoice.as_dict() for invoice in invoices]
        return jsonify(invoices=invoices)
     

class InvoicesByClientId(Resource):
    def get(self, org_id, user_id, client_id):
        """ list all clients """

        invoices = models.TripIncome.query.filter(
            and_(
                models.TripIncome.ti_organization_id == org_id,
                models.TripIncome.ti_client_id == client_id,
                models.TripIncome.ti_status != "deleted"
            )
        ).all()
        invoices = [invoice.as_dict() for invoice in invoices]
        return jsonify(invoices=invoices)
    
    def post(self, org_id, user_id, client_id):
        """ Add a client """
        request_data = request.get_json()

        data = {
            "ti_created_by": user_id,
            "ti_organization_id": org_id,
            "ti_client_id": client_id,
            "ti_type": request_data["ti_type"],
            "ti_description" : request_data["ti_description"],
            "ti_amount": request_data["ti_amount"],
            "ti_status": request_data["ti_status"]
        }

        result = qclients.add_invoice(client_id, data)
        invoice = result.as_dict()
        return jsonify(invoice=invoice)
    
    def put(self, org_id, user_id, client_id):
        """ Update a client """
        request_data = request.get_json()

        data = {
            "ti_created_by": user_id,
            "ti_organization_id": org_id,
            "ti_client_id": client_id,
            "ti_amount": request_data["ti_amount"],
            "ti_date": request_data["ti_date"],
            "ti_status": request_data["ti_status"]
        }

        result = qclients.update_invoice(data)
        invoice = result.as_dict()
        return jsonify(invoice=invoice)


api_clients.add_resource(ClientsByOrg, '/<org_id>/<user_id>/')
api_clients.add_resource(Invoices, '/invoices/<org_id>/<user_id>/')
api_clients.add_resource(InvoicesByClientId, '/invoices/<org_id>/<user_id>/<client_id>/')