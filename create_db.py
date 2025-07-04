from app import app, db

with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully!")
# This script initializes the database and creates the necessary tables.
# Run this script once to set up the database before starting the Flask app.