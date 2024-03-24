"""
Main entry point for the FlaskChain server.
"""

from dotenv import load_dotenv

from server import app
from server.db.db import init_db
from server.utils.logger import logger
from server.langchain.response_stream import init_queues
from server.cli.cli import parse_arguments, cli_callbacks
from server.conversation.conversation_loader import start_conversation, set_app

def main():
    load_dotenv()

    init_queues()

    args = parse_arguments()

    cli_callbacks(args)

    flask = app.create_app()

    init_db(flask)

    set_app(flask)

    start_conversation(args)

    # init flask app
    flask.run(
        debug=True,
        port=5000,
        host='localhost',
        use_reloader=False,
        threaded=True,
    )

    logger.info("Local server running on http://localhost:5000")

if __name__ == "__main__":
    main()