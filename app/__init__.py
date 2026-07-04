from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade, stamp
from dotenv import load_dotenv
import os
import logging
import subprocess
from sqlalchemy import inspect

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

logger = logging.getLogger(__name__)

def get_app_version():
    """Get the application version from the latest git tag"""
    try:
        return subprocess.check_output(
            ['git', 'describe', '--tags', '--abbrev=0'],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
    except Exception:
        return 'dev'

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///mempush.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['ONION_URL'] = os.getenv('ONION_URL', 'your-onion-url')
    app.config['VERSION'] = get_app_version()

    @app.context_processor
    def inject_globals():
        return {'app_version': app.config['VERSION']}

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.routes import bp
    app.register_blueprint(bp)
    
    return app 