import os
from werkzeug.utils import secure_filename
from flask import current_app
from sanasana import db
import base64
from sanasana.models import Maintenance
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
            current_app.root_path, 'static', 'uploads', 'maintenance'
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


