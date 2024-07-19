from sanasana import db
# from ..views import db


class User(db.Model):
    __tablename__ = 'users'  # Name of the table
    __table_args__ = {'schema': 'users'}  # Specify the schema

    id = db.Column(db.String, unique=True)
    default_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    organization_id = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
    
    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
    

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
        return f'<organization {self.f_name}>'
    
    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}