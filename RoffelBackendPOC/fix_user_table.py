from sqlalchemy import create_engine, text

# zelfde connection string als in app.py
engine = create_engine("sqlite:///roffel_tool.db", connect_args={"check_same_thread": False})

with engine.connect() as conn:
    # controleer of kolom al bestaat (veilig bij nogmaals draaien)
    res = conn.execute(text("PRAGMA table_info(users);"))
    cols = [row[1] for row in res.fetchall()]

    if "is_admin" not in cols:
        print("Kolom 'is_admin' toevoegen...")
        conn.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0;"))
        conn.commit()
        print("Gereed.")
    else:
        print("Kolom 'is_admin' bestaat al, niets te doen.")
