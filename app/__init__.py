from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from datetime import timedelta

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()  # Initialize CSRFProtect outside the function

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    # Apply configuration settings from config.py
    app.config.from_object(config_class)

    # session lifetime 
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)

    
    # Initialize CSRF protection
    csrf.init_app(app)
    csrf._disable_on_debug = True  # Disable CSRF protection in debug mode, only for local testing

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Set up login settings
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # User loader function
    from app.models import User  # Import the User model

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))  # Load user by ID
    
    # Import and register blueprints
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    

    # Return the Flask app instance
    return app

app = create_app()
