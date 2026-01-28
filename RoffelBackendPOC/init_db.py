# init_db.py

from app.database import engine, Base
import app.models  # triggert alle model-registraties

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized (roffel_tool.db).")

if __name__ == "__main__":
    init_db()

