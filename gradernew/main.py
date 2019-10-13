# Start the app
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, escape, request
from os import environ

# Start the database
app = Flask(__name__)


def get_db_configured_url():
    url = environ.get('POSTGRES_URL', default=None)
    database_name = environ.get('POSTGRES_DATABASE_NAME', default=None)
    username = environ.get('POSTGRES_USERNAME', default=None)
    password = environ.get('POSTGRES_PASSWORD', default="")

    # "postgresql://postgres:@localhost:32768/postgres" sebagai contoh
    return f"postgresql://{username}:{password}@{url}/{database_name}"


app.config['SQLALCHEMY_DATABASE_URI'] = get_db_configured_url()
db = SQLAlchemy(app)
from gradernew.models import *

"""
Use this by using `flask initdb`. Will initialize the database.

TODO: This is a very early version of it, make sure you could do
migrations here. Right now, it will only create tables and column
on models.py or anything that's extending `db.models`.
"""
@app.cli.command('initdb')
def resetdb_command():
    db.create_all()

# TODO move to a new file that handles controller. We're going Controller - Model here. With service and stuff.
@app.route('/')
def all_test_here():
    result_declarative = File.query.all()
    
    result_translated = []
    for j in result_declarative:
        i: File = j
        result_translated.append({
            'id':i.id,
            'name':i.name
        })
    
    return {'yuh': result_translated}
