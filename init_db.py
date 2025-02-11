from db_handler import create_user, engine, Base

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Create predefined users
    users = [
        {"username": "admin", "password": "IamAdmin2411"},
        {"username": "Arezou", "password": "123Arezou456"},
        {"username": "Jalal", "password": "147Jalal369"},        
    ]
    
    for user in users:
        response = create_user(user["username"], user["password"])
        print(f"Creating user {user['username']}: {response}")

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialization complete!")

    