from sanasana import db
from sanasana import models


def add_client(data):
    """
    Add a new client to the database.
    """
    client = models.Client()
    for key, value in data.items():
        if hasattr(client, key):
            setattr(client, key, value)
        else:
            raise ValueError(f"Invalid attribute '{key}' for Client model")
    # Set default values for optional fields if not provided
    db.session.add(client)
    db.session.commit()
    return client


def update_client(client_id, data):
    """
    Update an existing client in the database.
    """
    client = models.Client.query.get(client_id)
    if not client:
        raise ValueError(f"Client with ID {client_id} not found")
    for key, value in data.items():
        if hasattr(client, key):
            setattr(client, key, value)
        else:
            raise ValueError(f"Invalid attribute '{key}' for Client model")
    db.session.commit()
    return client


def delete_client(client_id):
    """
    Delete a client from the database.
    Scenario 1: If client has no invoices, delete completely.
    Scenario 2: If client has invoices, perform a soft delete.
    """
    client = models.Client.query.get(client_id)
    if not client:
        raise ValueError(f"Client with ID {client_id} not found")

    # Check if the client has any invoices
    has_invoices = models.TripIncome.query.filter_by(ti_client_id=client_id).first()

    if has_invoices:
        # Scenario 2: Soft delete
        client.c_is_deleted = True  # or client.deleted = True if renamed
        db.session.commit()
        return f"Client ID {client_id} soft deleted (invoices exist)"
    else:
        # Scenario 1: Hard delete
        db.session.delete(client)
        db.session.commit()
        return f"Client ID {client_id} permanently deleted"


def add_invoice(client_id, data):
    """
    Add a new invoice for a client.
    """
    invoice = models.TripIncome(ti_client_id=client_id)
    for key, value in data.items():
        if hasattr(invoice, key):
            setattr(invoice, key, value)
        else:
            raise ValueError(f"Invalid attribute '{key}' for Invoice model")
    db.session.add(invoice)
    db.session.commit()
    return invoice