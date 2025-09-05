from sanasana import db, models
from sqlalchemy import func
from datetime import datetime, timedelta


def check_inactive_fleets():
    five_days_ago = datetime.utcnow() - timedelta(days=5)

    # Step 1: Get all fleet managers (created_by in Trips)
    fleet_managers = (
        db.session.query(models.Trip.t_created_by, models.Trip.t_organization_id)
        .distinct()
        .all()
    )
    # Get all managers details by ID
    managers = (
        db.session.query(models.User)
        .filter(models.User.id.in_([m[0] for m in fleet_managers]))
        .all()
    )

    reminders = []

    for manager_id, org_id in fleet_managers:
        # Step 2: Find last trip date for this organization
        last_trip = (
            db.session.query(func.max(models.Trip.t_created_at))
            .filter(models.Trip.t_organization_id == org_id)
            .scalar()
        )

        # If org has no trips or last trip older than 5 days
        if not last_trip or last_trip < five_days_ago:
            # Step 3: Check if a reminder notification already exists in last 5 days
            recent_notification = (
                db.session.query(models.Notification)
                .filter(
                    models.Notification.recipient_user_id == manager_id,
                    models.Notification.type == "reminder",
                    models.Notification.category == "trip-engagement",
                    models.Notification.created_date < five_days_ago,
                )
                .first()
            )

            if not recent_notification:
                # Step 4: Insert a new reminder notification
                manager_name = next((manager.username for manager in managers if manager.id == manager_id and manager.username is not None), "Fleet Manager")
                manager_email = next((manager.email for manager in managers if manager.id == manager_id), None)
                message = (
                    f"Hello {manager_name},\n\n"
                    "We noticed that it’s been a while since your last trip — over 5 days ago. "
                    "Keeping your trips active helps you manage your fleet more efficiently and ensures your drivers and customers stay connected.\n\n"
                    "Why not create your next trip today and see how Sanasana continues to simplify fleet management for you?\n\n"
                    "https://sanasana.netlify.app/trips\n\n"
                    "Thank you for being part of the Sanasana community!\n"
                    "– The Sanasana Team"
                )
                new_notif = models.Notification(
                    recipient_user_id=manager_id,
                    recipient_email=manager_email,
                    message=message,
                    type="reminder",
                    category="trip-engagement",
                )
                db.session.add(new_notif)
                reminders.append(new_notif)

    if reminders:
        db.session.commit()

    return reminders

def get_all_auto_reminder_notifications():
    return db.session.query(models.Notification).filter(
        models.Notification.type == "reminder",
        models.Notification.category == "trip-engagement"
    ).all()


def get_notifications_by_user(user_id, status):
    query = db.session.query(models.Notification).filter(
        models.Notification.recipient_user_id == user_id
    )
    if status == 'all':
        query = query
    if status == 'read':
        query = query.filter(models.Notification.read == True)
    elif status == 'unread':
        query = query.filter(models.Notification.read == False)
    return query.all()


def delete_notification(notification_id):
    notif = db.session.query(models.Notification).get(notification_id)
    if notif:
        db.session.delete(notif)
        db.session.commit()
        return True
    return False


def mark_notification_as_read(notification_id):
    notif = db.session.query(models.Notification).get(notification_id)
    if notif:
        notif.read = True
        db.session.commit()
        return True
    return False


def mark_notification_as_unread(notification_id):
    notif = db.session.query(models.Notification).get(notification_id)
    if notif:
        notif.read = False
        db.session.commit()
        return True
    return False


def create_notification(user_id, **kwargs):
    notification = models.Notification(created_by=user_id, **kwargs)
    db.session.add(notification)
    db.session.commit()
    return notification


def create_maintenance_notifications():
    today = datetime.utcnow().date()
    reminders = []
    # Days before scheduled maintenance
    offsets = {5: "in 5 days", 1: "tomorrow", 0: "today"}

    maintenances = db.session.query(models.Maintenance).filter(
        models.Maintenance.m_date.isnot(None)
    ).all()

    for m in maintenances:
        if not m.asset:
            continue

        driver = db.session.query(models.Operator).filter(
            models.Operator.o_assigned_asset == m.m_asset_id
        ).first()

        for offset, label in offsets.items():
            notify_date = m.m_date - timedelta(days=offset)
            if notify_date == today:
                # Fleet manager message
                fm_message = (
                    f"Scheduled maintenance for {m.asset.a_make} {m.asset.a_model} "
                    f"({m.asset.a_license_plate}) is due {label} ({m.m_date})."
                )
                notif_manager = models.Notification(
                    created_by=m.m_created_by,
                    recipient_user_id=m.m_created_by,
                    message=fm_message,
                    type="reminder",
                    category="maintenance",
                )
                db.session.add(notif_manager)
                reminders.append(notif_manager)

                # Driver message if assigned
                if driver:
                    driver_message = (
                        f"Dear {driver.o_name}, maintenance for your assigned vehicle "
                        f"{m.asset.a_make} {m.asset.a_model} ({m.asset.a_license_plate}) "
                        f"is scheduled {label} ({m.m_date}). Please plan accordingly."
                    )
                    notif_driver = models.Notification(
                        created_by=m.m_created_by,
                        recipient_user_id=driver.user_id,
                        recipient_email=driver.o_email,
                        message=driver_message,
                        type="reminder",
                        category="maintenance",
                    )
                    db.session.add(notif_driver)
                    reminders.append(notif_driver)

    if reminders:
        db.session.commit()
    return reminders


def create_insurance_notifications():
    today = datetime.utcnow().date()
    reminders = []
    # Before expiry
    before_offsets = {7: "in 7 days", 2: "in 2 days", 0: "today"}
    # After expiry
    after_offsets = {3: "3 days ago", 7: "a week ago", 14: "2 weeks ago"}

    assets = db.session.query(models.Asset).filter(
        models.Asset.a_insurance_expiry.isnot(None)
    ).all()

    for asset in assets:
        expiry = asset.a_insurance_expiry
        if not expiry:
            continue

        # Fleet manager only
        for offset, label in before_offsets.items():
            notify_date = expiry - timedelta(days=offset)
            if notify_date == today:
                message = (
                    f"Insurance for {asset.a_make} {asset.a_model} "
                    f"({asset.a_license_plate}) will expire {label} ({expiry})."
                )
                notif = models.Notification(
                    created_by=asset.a_created_by,
                    recipient_user_id=asset.a_created_by,
                    message=message,
                    type="reminder",
                    category="insurance",
                )
                db.session.add(notif)
                reminders.append(notif)

        # After expiry nudges
        for offset, label in after_offsets.items():
            notify_date = expiry + timedelta(days=offset)
            if notify_date == today:
                message = (
                    f"Insurance for {asset.a_make} {asset.a_model} "
                    f"({asset.a_license_plate}) expired {label} ({expiry}). "
                    "Please update records to stay compliant."
                )
                notif = models.Notification(
                    created_by=asset.a_created_by,
                    recipient_user_id=asset.a_created_by,
                    message=message,
                    type="warning",
                    category="insurance",
                )
                db.session.add(notif)
                reminders.append(notif)

    if reminders:
        db.session.commit()
    return reminders


def create_license_notifications():
    today = datetime.utcnow().date()
    reminders = []
    # Before expiry
    before_offsets = {14: "in 14 days", 5: "in 5 days", 0: "today"}
    # After expiry
    after_offsets = {3: "3 days ago", 7: "a week ago", 14: "2 weeks ago"}

    operators = db.session.query(models.Operator).filter(
        models.Operator.o_lincense_expiry.isnot(None)
    ).all()

    for driver in operators:
        expiry = driver.o_lincense_expiry.date() if driver.o_lincense_expiry else None
        if not expiry:
            continue

        # Before expiry
        for offset, label in before_offsets.items():
            notify_date = expiry - timedelta(days=offset)
            if notify_date == today:
                # Driver message
                driver_msg = (
                    f"Dear {driver.o_name}, your driving license will expire {label} ({expiry}). "
                    "Please ensure renewal and share updated details with fleet management."
                )
                notif_driver = models.Notification(
                    created_by=driver.o_created_by,
                    recipient_user_id=driver.user_id,
                    recipient_email=driver.o_email,
                    message=driver_msg,
                    type="reminder",
                    category="license",
                )
                db.session.add(notif_driver)
                reminders.append(notif_driver)

                # Fleet manager message
                fm_msg = (
                    f"Driver {driver.o_name}'s license will expire {label} ({expiry}). "
                    "Ensure records are updated to stay compliant."
                )
                notif_manager = models.Notification(
                    created_by=driver.o_created_by,
                    recipient_user_id=driver.o_created_by,
                    message=fm_msg,
                    type="reminder",
                    category="license",
                )
                db.session.add(notif_manager)
                reminders.append(notif_manager)

        # After expiry
        for offset, label in after_offsets.items():
            notify_date = expiry + timedelta(days=offset)
            if notify_date == today:
                # Driver message
                driver_msg = (
                    f"Dear {driver.o_name}, your driving license expired {label} ({expiry}). "
                    "Please renew immediately and provide updated details."
                )
                notif_driver = models.Notification(
                    created_by=driver.o_created_by,
                    recipient_user_id=driver.user_id,
                    recipient_email=driver.o_email,
                    message=driver_msg,
                    type="warning",
                    category="license",
                )
                db.session.add(notif_driver)
                reminders.append(notif_driver)

                # Fleet manager message
                fm_msg = (
                    f"Driver {driver.o_name}'s license expired {label} ({expiry}). "
                    "Please follow up to update records and ensure compliance."
                )
                notif_manager = models.Notification(
                    created_by=driver.o_created_by,
                    recipient_user_id=driver.o_created_by,
                    message=fm_msg,
                    type="warning",
                    category="license",
                )
                db.session.add(notif_manager)
                reminders.append(notif_manager)

    if reminders:
        db.session.commit()
    return reminders
