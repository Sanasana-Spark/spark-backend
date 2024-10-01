from sanasana import db
from sqlalchemy import func

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
    a_attached_card = db.Column(db.Integer, db.ForeignKey('assets.cards.id'), nullable=True)

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
    

def get_asset_by_id(trip_id):
    act = Asset.query.filter_by(
        id=trip_id
    ).first()
    return act


def get_asset_count_by_org(org_id):
    count_of_assets = db.session.query(
        func.count(Asset.id)  # Replace Asset.id with the appropriate column if needed
    ).filter(Asset.a_organisation_id == org_id).scalar()

    return count_of_assets

def get_asset_value_sum_by_org(org_id):
    sum_of_values = db.session.query(
        func.sum(Asset.a_value)
    ).filter(Asset.a_organisation_id == org_id).scalar()

    return sum_of_values
