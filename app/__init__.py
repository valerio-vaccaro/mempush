from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade, stamp
from dotenv import load_dotenv
import os
import logging
from sqlalchemy import inspect

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///mempush.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['ONION_URL'] = os.getenv('ONION_URL', 'your-onion-url')

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.routes import bp
    app.register_blueprint(bp)
    
    return app 