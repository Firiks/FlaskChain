"""
Routes for the Flask app.
"""

# flask
from flask import Blueprint, render_template, jsonify, request, Response

# local
from server.backend import get_index_data, chat_response, sse_response, shutdown_server

bp = Blueprint("routes", __name__, template_folder="templates", static_folder="static")

@bp.route("/", methods=["GET"])
def index_route():
    data = get_index_data()

    return render_template("index.html", data=data)

@bp.route("/chat", methods=["POST"])
def chat_route():
    response = chat_response()

    return jsonify(response)

@bp.route("/shutdown", methods=["GET"])
def shutdown_route():
    shutdown_server()

    return "Shutting down server..."
    
@bp.route("/sse", methods=["GET"])
def sse_route():
    return Response(sse_response(), content_type='text/event-stream')

@bp.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

@bp.errorhandler(500)
def server_error(e):
    return "<h1>500</h1><p>An internal error occurred. <code>{}</code></p>".format(e), 500