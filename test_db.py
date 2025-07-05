from sqlalchemy import create_engine, text

db_url = "postgresql://stroke_predictor_db_user:45iK9KB4ZSd7oHM77hn8u6hkkMEUWOm0@dpg-d1khf06mcj7s73co4h00-a.oregon-postgres.render.com/stroke_predictor_db"

try:
    engine = create_engine(db_url)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT now();"))
        print("Connected! Time in DB server:", result.fetchone()[0])
except Exception as e:
    print("Connection failed:", e)
# This code tests the connection to the PostgreSQL database using SQLAlchemy.