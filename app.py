from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_babel import Babel

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vitanet.db'
app.config['BABEL_DEFAULT_LOCALE'] = 'en'

db = SQLAlchemy(app)
CORS(app)
Babel(app)

# Register Blueprints
from vitalsync import vitalsync_bp
app.register_blueprint(vitalsync_bp)

if __name__ == '__main__':
    app.run(debug=True)

