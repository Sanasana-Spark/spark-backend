from sanasana import db
from sqlalchemy import func
from .assets import Asset
from .operators import Operator
from sqlalchemy.dialects.postgresql import JSONB


class Trip(db.Model):
    __tablename__ = 'trips'  # Name of the table
    __table_args__ = {'schema': 'assets'}  # Specify the schema

    id = db.Column(db.Integer, primary_key=True) 
    t_origin_place_id = db.Column(db.String(255), nullable=True)
    t_origin_place_query = db.Column(db.String(255), nullable=True)
    t_destination_place_id = db.Column(db.String(255), nullable=True)
    t_destination_place_query = db.Column(db.String(255), nullable=True)
    t_distance = db.Column(db.String(50), nullable=True)
    t_duration = db.Column(db.String(50), nullable=True)
    t_directionsResponse = db.Column(JSONB, nullable=True)

    t_created_by = db.Column(db.String, db.ForeignKey('users.users.id'), nullable=False)
    t_created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    t_organization_id = db.Column(db.String,  db.ForeignKey('users.organization.id'), nullable=False) 
    t_type = db.Column(db.String(100), nullable=True)
    t_start_lat = db.Column(db.Numeric, nullable=True)
    t_start_long = db.Column(db.Numeric, nullable=True)
    t_start_elavation = db.Column(db.Numeric, nullable=True)
    t_end_lat = db.Column(db.Numeric, nullable=True)
    t_end_long = db.Column(db.Numeric, nullable=True)
    t_end_elavation = db.Column(db.Numeric, nullable=True)
    t_start_date = db.Column(db.DateTime, nullable=True)
    t_end_date = db.Column(db.DateTime, nullable=True)
    t_operator_id = db.Column(db.Integer, db.ForeignKey('assets.operators.id'), nullable=True)
    t_asset_id = db.Column(db.Integer, db.ForeignKey('assets.assets.id'), nullable=True)
    t_status = db.Column(db.String, default='PENDING', nullable=False,)
    t_load = db.Column(db.Float, nullable=True)
    t_est_fuel = db.Column(db.Float, nullable=True)
    t_actual_fuel = db.Column(db.Float, nullable=True)
    t_est_cost = db.Column(db.Float, nullable=True)
    t_actual_cost = db.Column(db.Float, nullable=True)
    t_consumption_variance = db.Column(db.Float, nullable=True)
    t_cost_variance = db.Column(db.Float, nullable=True)
    t_odometer_reading1 = db.Column(db.Float, nullable=True)
    t_dometer_reading2 = db.Column(db.Float, nullable=True)
    t_dometer_reading3 = db.Column(db.Float, nullable=True)
    t_dometer_reading4 = db.Column(db.Float, nullable=True)
    t_dometer_reading5 = db.Column(db.Float, nullable=True)
    t_odometer_image1 = db.Column(db.String(200), nullable=True)
    t_odometer_image2 = db.Column(db.String(200), nullable=True)
    t_odometer_image3 = db.Column(db.String(200), nullable=True)
    t_odometer_image3 = db.Column(db.String(200), nullable=True)
    t_odometer_image4 = db.Column(db.String(200), nullable=True)
    t_odometer_image5 = db.Column(db.String(200), nullable=True)
    operator = db.relationship('Operator', backref='trips')
    asset = db.relationship('Asset', backref='trips')

    def __repr__(self):
        return f'<Trips {self.id}>' 

    # def as_dict(self):
    #     return {column.name: getattr(self, column.name) for column in self.__table__.columns}
    
    def as_dict(self):
        result = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        result['o_name'] = self.operator.o_name if self.operator else None
        result['o_email'] = self.operator.o_email if self.operator else None
        result['a_make'] = self.asset.a_make if self.asset else None
        result['a_model'] = self.asset.a_model if self.asset else None
        result['a_license_plate'] = self.asset.a_license_plate if self.asset else None
        result['a_fuel_type'] = self.asset.a_fuel_type if self.asset else None
        result['a_efficiency_rate'] = self.asset.a_efficiency_rate if self.asset else None
        return result
  

class Tstatus(db.Model):
    __tablename__ = 'tstatus'  # Name of the table
    __table_args__ = {'schema': 'assets'}  # Specify the schema

    id = db.Column(db.Integer, primary_key=True)
    t_name = db.Column(db.String(200), nullable=True)
    t_name_code = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<Status {self.t_name}>' 

    # This method converts the model instance to a dictionary
    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
  

def get_all_trips():
    return Trip.query.all()


def get_trip_by_id(trip_id):
    return Trip.query.filter_by(
        id=trip_id).first()


def get_trip_by_org(org_id):
    return Trip.query.filter_by(
        t_organization_id=org_id).all()


def get_trip_by_status(org_id, t_status):
    act = Trip.query.filter_by(
     t_organization_id=org_id, t_status=t_status
    ).all()
    return act


def get_trip_by_id_status(trip_id, t_status):
    act = Trip.query.filter_by(
        id=trip_id, t_status=t_status
    ).first()
    return act


def update_status(trip_id, t_status):
    trip = Trip.query.filter_by(
        id=trip_id
    ).first()
    trip.t_status = t_status
    db.session.add(trip)
    db.session.commit()
    return trip


def update(trip_id, data):
    trip = Trip.query.filter_by(
        id=trip_id
    ).first()
    # if data['attr'] == "resolved" and data["value"]:
    #     issue.resolved_date = datetime.datetime.utcnow()
    setattr(trip, data['attr'], data['value'])
    db.session.add(trip)
    db.session.commit()
    return trip