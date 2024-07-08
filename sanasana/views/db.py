import sanasana  # Import the app instance
from flask import current_app
import psycopg2
import click


def get_db():
    db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
    dbname = db_uri.split('/')[-1]
    user = db_uri.split('://')[1].split(':')[0]
    password = db_uri.split(':')[2].split('@')[0]
    host = db_uri.split('@')[1].split(':')[0]
    port = db_uri.split(':')[3].split('/')[0]  
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    return conn


def init_db():
    None


def close_db(e=None):
    db = get_db()
    db.close()


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
