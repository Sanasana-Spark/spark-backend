from sanasana import db
from sqlalchemy import func

class Trip(db.Model):
    __tablename__ = 'trips'  # Name of the table
    __table_args__ = {'schema': 'assets'}  # Specify the schema

    id = db.Column(db.Integer, primary_key=True) 
    t_created_by = db.Column(db.String, db.ForeignKey('users.users.id'), nullable=False)
    t_created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    t_organization_id = db.Column(db.String,  db.ForeignKey('users.organization.id'), nullable=False) 
    t_type = db.Column(db.String(100), nullable=True)
    t_start_lat = db.Column(db.Numeric, nullable=False)
    t_start_long = db.Column(db.Numeric, nullable=False)
    t_start_elavation = db.Column(db.Numeric, nullable=True)
    t_end_lat = db.Column(db.Numeric, nullable=False)
    t_end_long = db.Column(db.Numeric, nullable=False)
    t_end_elavation = db.Column(db.Numeric, nullable=True)
    t_distance = db.Column(db.Float, nullable=True)
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

    def __repr__(self):
        return f'<Trips {self.id}>' 

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
    
