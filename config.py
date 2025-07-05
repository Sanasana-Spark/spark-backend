import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    CLERK_SECRET_KEY = os.environ.get('CLERK_SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    include_schemas = True
    INCLUDE_SCHEMAS = True

    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
    AUTHORIZATION_URL = os.environ.get("auth_uri", None)
    GOOGLE_DISCOVERY_URL = (
        "https://accounts.google.com/.well-known/openid-configuration"
    )
    SECRET_KEY = os.environ.get("secret_key", None)
    UPLOAD_FOLDER = 'resiix/images/'

    # mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'False') == 'True'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'True') == 'True'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = os.environ.get('ADMINS')

