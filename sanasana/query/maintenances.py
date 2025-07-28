import os
from werkzeug.utils import secure_filename
from flask import current_app
from sanasana import db
import base64
from sanasana.models import Maintenance, User, Asset
from sanasana import models
from sqlalchemy import desc
from datetime import datetime


def save_attachment_file(attachment):
    if attachment:
        original_filename = attachment.get("name")
        base64_data = attachment.get("data")

        if not original_filename or not base64_data:
            return None

        # Sanitize filename
        original_filename = secure_filename(original_filename)
        name, ext = os.path.splitext(original_filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"{name}---{timestamp}{ext}"

        # Ensure directory exists
        folder_path = os.path.join(
            current_app.root_path, 'uploads', 'maintenance'
        )
        os.makedirs(folder_path, exist_ok=True)

        # Decode base64 string to binary
        file_bytes = base64.b64decode(base64_data)

        # Write to disk
        file_path = os.path.join(folder_path, new_filename)
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        return f'static/uploads/maintenance/{new_filename}'
    
    return None


def add_maintenance(maintenance, file=None):
    attachment_path = save_attachment_file(file) if file else None
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
    query = models.Maintenance.query.filter(
        models.Maintenance.m_organisation_id == org_id,
        models.Maintenance.m_date >= datetime.now().date()
    ).order_by(models.Maintenance.m_date.desc())
    return query.all()


def get_maintenance_history_by_organization(org_id):
    query = models.Maintenance.query.filter(
        models.Maintenance.m_organisation_id == org_id,
        models.Maintenance.m_date < datetime.now().date()
    ).order_by(models.Maintenance.m_date.desc())
    return query.all()


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



def get_report(org_id, start_date, end_date):

    # Validate date inputs
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
    except Exception:
        return jsonify(error="Invalid date format. Use YYYY-MM-DD."), 400

    # Query with joins and filtering
    results = (
        db.session.query(Maintenance, User.name, Asset.a_license_plate)
        .join(User, User.id == Maintenance.m_created_by)
        .join(Asset, Asset.id == Maintenance.m_asset_id)
        .filter(
            Maintenance.m_organisation_id == org_id,
            Maintenance.m_date.between(start, end)
        )
        .order_by(Maintenance.m_date.desc())
        .all()
    )

    # Format results
    maintenance_list = []
    for maintenance, created_by_name, license_plate in results:
        maintenance_list.append({
            "created_by": created_by_name,
            "asset_License": license_plate,
            "type": maintenance.m_type,
            "description": maintenance.m_description,
            "date": maintenance.m_date.strftime('%d/%m/%Y') if maintenance.m_date else None,
            "total_cost": maintenance.m_total_cost,
            "insurance_coverage": maintenance.m_insurance_coverage,
            "status": maintenance.m_status,
        })

    return maintenance_list


