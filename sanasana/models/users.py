from sanasana import db
# from ..views import db


class User(db.Model):
    __tablename__ = 'user'  # Name of the table
    __table_args__ = {'schema': 'users'}  # Specify the schema

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    firm_id = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
    

class Organization(db.Model):
    __tablename__ = 'firm'  # Name of the table
    __table_args__ = {'schema': 'users'}  # Specify the schema

    id = db.Column(db.Integer, primary_key=True)
    f_name = db.Column(db.String(80), unique=True, nullable=False)
    f_industry = db.Column(db.String(80), unique=True, nullable=False)
    f_country = db.Column(db.String(80), unique=True, nullable=False)
    f_email = db.Column(db.String(120), unique=True, nullable=False)
    f_size = db.Column(db.Integer, nullable=False)
    f_fiscal_start = db.Column(db.Date, nullable=True)
    f_fiscal_stop = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return f'<Firm {self.f_name}>'