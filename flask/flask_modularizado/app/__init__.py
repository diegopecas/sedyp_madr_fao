from flask import Flask
from flask_cors import CORS
from .config import Config
from .auth import auth
from .user import user
from .eventos import event
from .audit import audit
from .permits import permits
from .visor import visor
from .reports import report


def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config.update(Config.EMAIL_CONFIG)
    app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
    app.config['UPLOAD_EVENTO'] = Config.UPLOAD_EVENTO
    app.config['UPLOAD_SEGUIMIENTO'] = Config.UPLOAD_SEGUIMIENTO   

    # Register the blueprints
    app.register_blueprint(auth)
    app.register_blueprint(user)
    app.register_blueprint(event)
    app.register_blueprint(audit)
    app.register_blueprint(permits)
    app.register_blueprint(visor)
    app.register_blueprint(report)

    return {'app': app}