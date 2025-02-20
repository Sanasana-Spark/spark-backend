from sanasana import db
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB


class Organization(db.Model):
    __tablename__ = 'organization'  # Name of the table
    __table_args__ = {'schema': 'users'}  # Specify the schema

    id = db.Column(db.String, unique=True)
    default_id = db.Column(db.Integer, primary_key=True)
    org_name = db.Column(db.String(80), unique=True, nullable=False)
    org_industry = db.Column(db.String(80), nullable=True)
    org_country = db.Column(db.String(80), nullable=True)
    org_email = db.Column(db.String(120), nullable=True)
    org_size = db.Column(db.Integer, nullable=True)
    org_fiscal_start = db.Column(db.Date, nullable=True)
    org_fiscal_stop = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return f'<Organization {self.org_name}>'
    
    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

class User(db.Model):
    __tablename__ = 'users'  # Name of the table
    __table_args__ = {'schema': 'users'}  # Specify the schema

    id = db.Column(db.String, unique=True)
    default_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    organization_id = db.Column(db.String(), nullable=False)
    name = db.Column(db.String(), nullable=True)
    

    def __repr__(self):
        return f'<User {self.username}>'
    
    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class Asset(db.Model):
    __tablename__ = 'assets'  # Name of the table
    __table_args__ = {'schema': 'assets'}  # Specify the schema

    id = db.Column(db.Integer, primary_key=True)
    a_organisation_id = db.Column(db.String, db.ForeignKey('users.organization.id'), nullable=False)
    a_created_by = db.Column(db.String, db.ForeignKey('users.users.id'), nullable=False)
    a_created_at = db.Column(db.DateTime, nullable=False, default=func.now())
    a_name = db.Column(db.String(100), nullable=False)
    a_make = db.Column(db.String(100), nullable=False)
    a_model = db.Column(db.String(100), nullable=False)
    a_year = db.Column(db.Integer, nullable=False)
    a_license_plate = db.Column(db.String(50), nullable=False)
    a_type = db.Column(db.String(50), nullable=True)
    a_msrp = db.Column(db.Float, nullable=True)
    a_chasis_no = db.Column(db.String(100), nullable=True)
    a_engine_size = db.Column(db.Float, nullable=False)
    a_tank_size = db.Column(db.Float, nullable=False)
    a_efficiency_rate = db.Column(db.Float, nullable=False)
    a_fuel_type = db.Column(db.String(50), nullable=False)
    a_cost = db.Column(db.Float, nullable=False)
    a_value = db.Column(db.Float, nullable=False)
    a_depreciation_rate = db.Column(db.Float, nullable=False)
    a_apreciation_rate = db.Column(db.Float, nullable=False)
    a_accumulated_dep = db.Column(db.Float, nullable=True)
    a_image = db.Column(db.String(200), nullable=True)
    a_attachment1 = db.Column(db.String(200), nullable=True)
    a_attachment2 = db.Column(db.String(200), nullable=True)
    a_attachment3 = db.Column(db.String(200), nullable=True)
    a_status = db.Column(db.String(50), nullable=False)
    a_displacement = db.Column(db.Float, nullable=True)
    a_mileage = db.Column(db.Float, nullable=True)
    a_horsepower = db.Column(db.Float, nullable=True)
    a_acceleration = db.Column(db.Float, nullable=True)
    a_insurance_expiry = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return f'<Asset {self.a_name}>' 

    # This method converts the model instance to a dictionary
    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
    

class Status(db.Model):
    __tablename__ = 'status'  # Name of the table
    __table_args__ = {'schema': 'assets'}  # Specify the schema

    id = db.Column(db.Integer, primary_key=True)
    s_name = db.Column(db.String(200), nullable=True)
    s_name_code = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<Status {self.s_name}>' 

    # This method converts the model instance to a dictionary
    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
    

class Operator(db.Model):
    __tablename__ = 'operators'  # Name of the table
    __table_args__ = {'schema': 'assets'}  # Specify the schema

    id = db.Column(db.Integer, primary_key=True)
    o_organisation_id = db.Column(db.String, db.ForeignKey('users.organization.id'), nullable=False)
    o_created_by = db.Column(db.String, db.ForeignKey('users.users.id'), nullable=False)
    o_created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    o_name = db.Column(db.String(100), nullable=False)
    o_email = db.Column(db.String(120), unique=True, nullable=False)
    o_phone = db.Column(db.String(100), nullable=True)
    o_national_id = db.Column(db.String(100), nullable=True)
    o_lincense_id = db.Column(db.String(100), nullable=True)
    o_lincense_type = db.Column(db.String(100), nullable=True)
    o_lincense_expiry = db.Column(db.DateTime, nullable=True)
    o_assigned_asset = db.Column(db.Integer, db.ForeignKey('assets.assets.id'), nullable=True)
    o_payment_card_id = db.Column(db.Integer, nullable=True)
    o_Payment_card_no = db.Column(db.String(100), nullable=True)
    o_role = db.Column(db.String(100), nullable=True)
    o_image = db.Column(db.String(200), nullable=True)
    o_status = db.Column(db.String(100), nullable=False)
    o_cum_mileage = db.Column(db.Numeric(), nullable=True)
    o_expirence = db.Column(db.Numeric(), nullable=True)
    o_attachment1 = db.Column(db.String(200), nullable=True)
    asset = db.relationship('Asset', backref='operator')

    def __repr__(self):
        return f'<Operators {self.o_national_id}>' 

    # This method converts the model instance to a dictionary
    def as_dict(self):
        result = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        result['a_license_plate'] = self.asset.a_license_plate if self.asset else None
        result['a_make'] = self.asset.a_make if self.asset else None
        result['a_model'] = self.asset.a_model if self.asset else None
        return result
    

class Ostatus(db.Model):
    __tablename__ = 'ostatus'  # Name of the table
    __table_args__ = {'schema': 'assets'}  # Specify the schema

    id = db.Column(db.Integer, primary_key=True)
    o_name = db.Column(db.String(200), nullable=True)
    o_name_code = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<Status {self.o_name}>' 

    # This method converts the model instance to a dictionary
    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
    


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


class Card(db.Model):
    __tablename__ = 'cards'  # Name of the table
    __table_args__ = {'schema': 'assets'}  # Specify the schema

    id = db.Column(db.Integer, primary_key=True) 
    c_created_by = db.Column(db.String, db.ForeignKey('users.users.id'), nullable=False)
    c_created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    c_organization_id = db.Column(db.String,  db.ForeignKey('users.organization.id'), nullable=False)
    c_assigned_at = db.Column(db.DateTime, nullable=True)
    c_number = db.Column(db.String, nullable=False)
    c_expiry_date = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<cards {self.id}>' 

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
    

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
