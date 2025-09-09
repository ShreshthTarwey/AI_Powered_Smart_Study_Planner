from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
# Creates instances of the extensions above but does not yet attach them to any app.

# This allows attaching these extensions to the Flask app dynamically later, which is essential for the factory pattern.


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# Defines the application factory function named create_app().
# This function creates and configures a new Flask app instance.

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from .auth import auth_bp
    from .main import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app
