from flask import Flask
from db_handler import db, create_user
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database with default users."""
    # Create a temporary Flask app for the database context
    app = Flask(__name__)
    
    # Configure the app for database initialization
    DATABASE_DIR = '/app/data'
    os.makedirs(DATABASE_DIR, exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(DATABASE_DIR, 'fabric-ui.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize the database
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create predefined users
        users = [
            {"username": "admin", "password": "IamAdmin2411"},
            {"username": "Arezou", "password": "123Arezou456"},
            {"username": "Jalal", "password": "147Jalal369"},        
        ]
        
        for user in users:
            response = create_user(user["username"], user["password"])
            logger.info(f"Creating user {user['username']}: {response}")

if __name__ == "__main__":
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialization complete!")

