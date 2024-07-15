from sanasana import db


class Asset(db.Model):
    __tablename__ = 'assets'  # Name of the table
    __table_args__ = {'schema': 'assets'}  # Specify the schema

    id = db.Column(db.Integer, primary_key=True)
    a_name = db.Column(db.String(100), nullable=False)
    a_make = db.Column(db.String(100), nullable=False)
    a_model = db.Column(db.String(100), nullable=False)
    a_year = db.Column(db.Integer, nullable=False)
    a_license_plate = db.Column(db.String(50), nullable=False)
    a_type = db.Column(db.String(50), nullable=False)
    a_msrp = db.Column(db.Float, nullable=False)
    a_chasis_no = db.Column(db.String(100), nullable=False)
    a_engine_size = db.Column(db.Float, nullable=False)
    a_tank_size = db.Column(db.Float, nullable=False)
    a_efficiency_rate = db.Column(db.Float, nullable=False)
    a_fuel_type = db.Column(db.String(50), nullable=False)
    a_cost = db.Column(db.Float, nullable=False)
    a_value = db.Column(db.Float, nullable=False)
    a_depreciation_rate = db.Column(db.Float, nullable=False)
    a_apreciation_rate = db.Column(db.Float, nullable=False)
    a_accumulated_dep = db.Column(db.Float, nullable=False)
    a_image = db.Column(db.String(200), nullable=True)
    a_attachment1 = db.Column(db.String(200), nullable=True)
    a_attachment2 = db.Column(db.String(200), nullable=True)
    a_attachment3 = db.Column(db.String(200), nullable=True)
    a_status = db.Column(db.String(50), nullable=False)
    a_owner_id = db.Column(db.Integer, db.ForeignKey('users.firm.id'), nullable=True)

    def __repr__(self):
        return f'<Asset {self.a_name}>' 

    # This method converts the model instance to a dictionary
    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}