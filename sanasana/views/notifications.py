import datetime
from flask import (
    Blueprint,  jsonify, request, abort
)
from werkzeug.utils import secure_filename
import os
from flask_restful import Api, Resource
from .. import  db
from sanasana.query import notifications as qnotifications

# import pandas as pd


bp = Blueprint('notifications', __name__, url_prefix='/notifications')

api_notifications = Api(bp)


class AutoReminderNotifications(Resource):
    def get(self, user_id):
        """ Get all auto reminder notifications """
        # use user_id to check permission once implemented properly
        #temporary
        # qnotifications.delete_all_notifications()
        notifications = qnotifications.get_all_auto_reminder_notifications()
        notifications = [notification.as_dict() for notification in notifications]
        return jsonify(notifications=notifications)

    def post(self, user_id):
        """ Create an auto reminder notification """
        # use user_id to check permission once implemented properly
        notifications = qnotifications.check_inactive_fleets()
        notifications = [notification.as_dict() for notification in notifications]
        return jsonify(notifications=notifications)


class NotificationsByUser(Resource):
    def get(self, user_id):
        """ Get all notifications for a specific user """
        status = request.args.get('status', 'all')
        notifications = qnotifications.get_notifications_by_user(user_id, status)
        notifications = [notification.as_dict() for notification in notifications]
        return jsonify(notifications=notifications)


class UpdateNotificationStatus(Resource):
    def post(self, user_id):
        """ Update the status of a notification """
        notification_id = request.json.get('notification_id')
        status = request.json.get('status')
        if not notification_id or not status:
            abort(400, 'Missing notification_id or status')

        if status not in ['read', 'unread']:
            abort(400, 'Invalid status')

        if status == 'read':
            qnotifications.mark_notification_as_read(notification_id)
        else:
            qnotifications.mark_notification_as_unread(notification_id)

        return jsonify(success=True)


api_notifications.add_resource(AutoReminderNotifications, '/<user_id>/auto-reminder/')
api_notifications.add_resource(NotificationsByUser, '/<user_id>/')
api_notifications.add_resource(UpdateNotificationStatus, '/<user_id>/update-status/')
