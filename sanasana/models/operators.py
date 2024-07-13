from sanasana import db


class Operator(db.Model):
    __tablename__ = 'operators'  # Name of the table
    __table_args__ = {'schema': 'assets'}  # Specify the schema

    id = db.Column(db.Integer, primary_key=True)
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

    def __repr__(self):
        return f'<Operators {self.o_national_id}>' 

    # This method converts the model instance to a dictionary
    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}