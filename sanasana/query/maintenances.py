from sanasana import db
from sanasana.models import Maintenance
from sqlalchemy import desc

def add_maintenance(data):
    maintenance = Maintenance(
        m_created_by=data['m_created_by'],
        m_asset_id=data['m_asset_id'],
        m_type=data['m_type'],
        m_description=data.get('m_description'),
        m_date=data.get('m_date'),
        m_total_cost=data.get('m_total_cost'),
        m_insurance_coverage=data.get('m_insurance_coverage'),
        m_status=data.get('m_status')
    )
    db.session.add(maintenance)
    db.session.commit()
    return maintenance

def edit_maintenance(maintenance_id, data):
    maintenance = Maintenance.query.get(maintenance_id)
    if not maintenance:
        return None
    for key, value in data.items():
        if hasattr(maintenance, key):
            setattr(maintenance, key, value)
    db.session.commit()
    return maintenance

def get_maintenance_by_organization(org_id):
    return db.session.query(Maintenance).join(Maintenance.asset)\
        .filter(Maintenance.asset.has(a_organisation_id=org_id))\
        .order_by(desc(Maintenance.id)).all()

def get_maintenance_by_asset(asset_id):
    return Maintenance.query.filter_by(m_asset_id=asset_id)\
        .order_by(desc(Maintenance.id)).all()

