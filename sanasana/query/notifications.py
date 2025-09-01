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