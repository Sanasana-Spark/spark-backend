from sanasana import db
from sqlalchemy import func


class Card(db.Model):
    __tablename__ = 'cards'  # Name of the table
    __table_args__ = {'schema': 'assets'}  # Specify the schema

    id = db.Column(db.Integer, primary_key=True) 
    c_created_by = db.Column(db.String, db.ForeignKey('users.users.id'), nullable=False)
    c_created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    c_organization_id = db.Column(db.String,  db.ForeignKey('users.organization.id'), nullable=False)
    c_assign_by = db.Column(db.String, db.ForeignKey('users.users.id'), nullable=True)
    c_assigned_at = db.Column(db.DateTime, nullable=True)
    c_assigned_to = db.Column(db.Integer, db.ForeignKey('assets.operators.id'), nullable=True)
    c_attached_asset = db.Column(db.Integer, db.ForeignKey('assets.assets.id'), nullable=True)
    c_number = db.Column(db.String, nullable=False)
    c_expiry_date = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<cards {self.id}>' 

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}