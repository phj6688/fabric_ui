from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
import bcrypt
import datetime

# Database Setup
DATABASE_URL = "sqlite:///fabric-ui.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# User Model
class User(Base):
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
class Action(Base):
    __tablename__ = "actions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User", back_populates="actions")


Base.metadata.create_all(bind=engine)


# Database Helper Functions
def get_user(username: str):
    session = SessionLocal()
    user = session.query(User).filter(User.username == username).first()
    session.close()
    return user

def create_user(username: str, password: str):
    session = SessionLocal()
    if get_user(username):
        return "User already exists"
    new_user = User(username=username, password_hash=User.hash_password(password))
    session.add(new_user)
    session.commit()
    session.close()
    return "User created successfully"


def update_password(username: str, new_password: str):
    session = SessionLocal()
    user = session.query(User).filter(User.username == username).first()
    if not user:
        return "User not found"
    user.password_hash = User.hash_password(new_password)
    session.commit()
    session.close()
    return "Password updated successfully"


def log_action(username: str, action: str):
    session = SessionLocal()
    user = get_user(username)
    if not user:
        return "User not found"
    new_action = Action(user_id=user.id, action=action)
    session.add(new_action)
    session.commit()
    session.close()
    return "Action logged"

def list_user_actions(username: str):
    session = SessionLocal()
    user = get_user(username)
    if not user:
        return "User not found"
    actions = session.query(Action).filter(Action.user_id == user.id).all()
    session.close()
    return [{"action": a.action, "timestamp": a.timestamp} for a in actions]

