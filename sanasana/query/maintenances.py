import os
from werkzeug.utils import secure_filename
from flask import current_app
from sanasana import db
from sanasana.models import Maintenance
from sqlalchemy import desc
from datetime import datetime


def save_attachment_file(file_storage):
    if file_storage:
        original_filename = secure_filename(file_storage.filename)
        name, ext = os.path.splitext(original_filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"{name}---{timestamp}{ext}"

        folder_path = os.path.join(current_app.root_path, 'static', 'uploads', 'maintenance')
        os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path, new_filename)
        file_storage.save(file_path)

        return f'static/uploads/maintenance/{new_filename}'
    return None


def add_maintenance(data, file=None):
    attachment_path = save_attachment_file(file) if file else None

    maintenance = Maintenance(
        m_created_by=data['m_created_by'],
        m_asset_id=data['m_asset_id'],
        m_type=data['m_type'],
        m_description=data.get('m_description'),
        m_date=data.get('m_date'),
        m_total_cost=data.get('m_total_cost'),
        m_estimated_cost=data.get('m_estimated_cost'),
        m_insurance_coverage=data.get('m_insurance_coverage'),
        m_status=data.get('m_status'),
        m_attachment=attachment_path,
        m_organisation_id=data.get("m_organisation_id")
    )
    db.session.add(maintenance)
    db.session.commit()
    return maintenance


def edit_maintenance(maintenance_id, data, file=None):
    maintenance = Maintenance.query.get(maintenance_id)
    if not maintenance:
        return None

    for key, value in data.items():
        if hasattr(maintenance, key):
            setattr(maintenance, key, value)

    if file:
        maintenance.m_attachment = save_attachment_file(file)
    db.session.commit()
    return maintenance


def get_maintenance_by_organization(org_id):
    return db.session.query(Maintenance).join(Maintenance.asset)\
        .filter(Maintenance.asset.has(a_organisation_id=org_id))\
        .order_by(desc(Maintenance.id)).all()


def get_maintenance_by_asset(org_id, asset_id):
    return Maintenance.query.filter_by(m_asset_id=asset_id)\
        .order_by(desc(Maintenance.id)).all()
        
        
def delete_maintenance(maintenance_id):
    maintenance = Maintenance.query.get(maintenance_id)
    if not maintenance:
        return None
    db.session.delete(maintenance)
    db.session.commit()
    return maintenance


