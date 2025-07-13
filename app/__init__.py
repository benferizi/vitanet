from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_babel import Babel

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vitanet.db'
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'

    # Initialize extensions
    db.init_app(app)
    CORS(app)
    Babel(app)

    # Register main route
    @app.route("/")
    def index():
        return render_template("index.html")

    # Register Blueprints
    from vitalsync import vitalsync_bp
    app.register_blueprint(vitalsync_bp)

    from app.routes import bp as api_bp
    app.register_blueprint(api_bp)

    return app
