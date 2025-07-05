from flask import current_app
from flask_mail import Message

from sanasana import mail


def send_email(message_recipient, message_subject, message_body):
    # with current_app.app_context():
    msg = Message(
        subject=message_subject,
        sender="info@sanasanasustainability.com",
        recipients=[message_recipient],
        body=message_body
    )
    mail.send(msg)


def send_trip_assigned_email(message_recipient, user_name):
    msg = Message("New Trip Alert !!", sender="info@sanasanasustainability.com", recipients=[message_recipient])
    msg.body = f"Hi {user_name},\n\n" \
               "You have been assigned a new trip.\n\n" \
               "Click the link below to view the details:\n" \
               "https://sanasanapwa.netlify.app/"
               
    msg.html = f"<p>Hi {user_name},</p>" \
               "<p>You have been assigned a new trip.</p>" \
               '<p>Click <a href="https://sanasanapwa.netlify.app/">here</a> to view the details.</p>'

    mail.send(msg)


