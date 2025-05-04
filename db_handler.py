from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime
import bcrypt
import os

# Initialize SQLAlchemy
db = SQLAlchemy()

# User Model
class User(db.Model):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    actions = relationship("Action", back_populates="user")

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())


# Action Model
class Action(db.Model):
    __tablename__ = "actions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User", back_populates="actions")


# Database Helper Functions
def get_user(username: str):
    """Get a user by username"""
    return User.query.filter_by(username=username).first()


def create_user(username: str, password: str):
    """Create a new user"""
    if get_user(username):
        return "User already exists"
    
    new_user = User(username=username, password_hash=User.hash_password(password))
    db.session.add(new_user)
    db.session.commit()
    return "User created successfully"


def update_password(username: str, new_password: str):
    """Update a user's password"""
    user = User.query.filter_by(username=username).first()
    if not user:
        return "User not found"
    
    user.password_hash = User.hash_password(new_password)
    db.session.commit()
    return "Password updated successfully"


def log_action(username: str, action: str):
    """Log a user action"""
    user = get_user(username)
    if not user:
        return "User not found"
    
    new_action = Action(user_id=user.id, action=action)
    db.session.add(new_action)
    db.session.commit()
    return "Action logged"


def list_user_actions(username: str):
    """List all actions for a user"""
    user = get_user(username)
    if not user:
        return "User not found"
    
    actions = Action.query.filter_by(user_id=user.id).all()
    return [{"action": a.action, "timestamp": a.timestamp} for a in actions]

