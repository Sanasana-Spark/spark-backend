from sanasana import db
from sqlalchemy import func
from .operators import Operator
from .assets import Asset
from .trips import Trip
from sanasana.models import trips as qtrip
from .card import Card


class Fuel_request(db.Model):
    __tablename__ = 'fuel_request'  # Name of the table
    __table_args__ = {'schema': 'assets'}  # Specify the schema

    id = db.Column(db.Integer, primary_key=True) 
    f_created_by = db.Column(db.String, db.ForeignKey('users.users.id'), nullable=False)
    f_created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    f_organization_id = db.Column(db.String,  db.ForeignKey('users.organization.id'), nullable=False) 

    f_operator_id = db.Column(db.Integer, db.ForeignKey('assets.operators.id'), nullable=False)
    f_asset_id = db.Column(db.Integer, db.ForeignKey('assets.assets.id'), nullable=True)
    f_trip_id = db.Column(db.Integer, db.ForeignKey('assets.trips.id'), nullable=True)
    f_card_id = db.Column(db.Integer, db.ForeignKey('assets.cards.id'), nullable=True)

    f_status = db.Column(db.String, default='PENDING', nullable=False)
    f_type = db.Column(db.String, nullable=True)
    f_litres = db.Column(db.Float, nullable=False)
    f_cost = db.Column(db.Float, nullable=True)
    f_total_cost = db.Column(db.Float, nullable=False)
    f_distance = db.Column(db.Float, nullable=True)
    f_vendor = db.Column(db.String, nullable=True)
    f_odometer_image = db.Column(db.String(200), nullable=True)
    f_odometer_reading = db.Column(db.Float, nullable=True)
    f_receipt_image = db.Column(db.String(200), nullable=True)
    f_receipt_pdf = db.Column(db.String(200), nullable=True)

    operator = db.relationship('Operator', backref='fuel_request')
    asset = db.relationship('Asset', backref='fuel_request')
    trip = db.relationship('Trip', backref='fuel_request')
    card = db.relationship('Card', backref='fuel_request')

    def __repr__(self):
        return f'<Fuel_request {self.id}>' 
   
    def as_dict(self):
        result = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        result['o_name'] = self.operator.o_name if self.operator else None
        result['a_license_plate'] = self.asset.a_license_plate if self.asset else None
        result['f_card_no'] = self.card.c_number if self.card else None
        result['t_status'] = self.trip.t_status if self.trip else None
        result['a_fuel_type'] = self.asset.a_fuel_type if self.asset else None
        result['t_distance'] = self.trip.t_distance if self.trip else None
        return result


def add(trip_id, data):
    fuel_request = Fuel_request()
    fuel_request.f_trip_id = trip_id,
    fuel_request.f_organization_id = data["f_organization_id"]
    fuel_request.f_created_by = data["f_created_by"]
    fuel_request.f_asset_id = data["f_asset_id"]
    fuel_request.f_operator_id = data["f_operator_id"]
    fuel_request.f_card_id = data["f_card_id"]
    fuel_request.f_litres = data["f_litres"]
    fuel_request.f_cost = data["f_cost"]
    fuel_request.f_total_cost = data["f_total_cost"]
    fuel_request.f_distance = data["f_distance"]
    fuel_request.f_type = data["f_type"]

    for key, value in data.items():
        setattr(fuel_request, key, value)
    _classifications = []
    db.session.add(fuel_request)  

    db.session.commit()
    return fuel_request