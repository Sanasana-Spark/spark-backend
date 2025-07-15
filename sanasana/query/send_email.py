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


def send_organization_creation_success_email(message_recipient, org_name):
    msg = Message(
        "Organization Created Successfully",
        sender="info@sanasanasustainability.com",
        recipients=[message_recipient]
    )
    msg.body = (
        f"Hi,\n\n"
        f"Your organization '{org_name}' has been created successfully.\n\n"
        "You can view your organization details using the following links:\n"
        "Drivers App: https://sanasanapwa.netlify.app/\n"
        "Managers Side: https://sanasana.netlify.app/"
    )
    msg.html = (
        "<p>Hi,</p>"
        f"<p>Your organization '<strong>{org_name}</strong>' has been created successfully.</p>"
        '<p>You can view your organization details using the following links:</p>'
        '<ul>'
        '<li>Drivers App: <a href="https://sanasanapwa.netlify.app/">https://sanasanapwa.netlify.app/</a></li>'
        '<li>Managers Side: <a href="https://sanasana.netlify.app/">https://sanasana.netlify.app/</a></li>'
        '</ul>'
    )
    mail.send(msg)