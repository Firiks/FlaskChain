"""
Get Flask app instance
"""

# flask
from flask import Flask

# import routes blueprint
from server.routes import bp as routes_bp

def create_app():
    app = Flask(__name__)

    # Register Blueprints
    app.register_blueprint(routes_bp)

    return app