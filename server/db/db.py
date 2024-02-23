"""
DB module
"""

from flask_sqlalchemy import SQLAlchemy

from server.utils.helpers import get_location

db_path = get_location('../db/flaskchain.db')

db = SQLAlchemy()

def init_db(app):
    global db

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()