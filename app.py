import mimetypes
import sys
import os

# Windows registry maps .js to text/plain, which Chrome rejects for ES6 modules.
# Calling init() first loads the registry, then add_type() overrides it.
mimetypes.init()
mimetypes.add_type("application/javascript", ".js")

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template
from config import Config
from routes.api import api
from routes.agent_api import agent_api


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(api)
    app.register_blueprint(agent_api)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/chat")
    def chat():
        return render_template("chat.html")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
