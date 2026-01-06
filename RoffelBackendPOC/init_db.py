import sqlite3

DB_PATH = "app.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Tabel voor serviceorders
cur.execute("""
CREATE TABLE IF NOT EXISTS service_orders (
    so TEXT PRIMARY KEY,
    supplier TEXT,
    customer_ref TEXT,
    po TEXT,
    status TEXT,
    employee TEXT
)
""")

# Testdata invoegen
cur.execute("""
INSERT OR IGNORE INTO service_orders
(so, supplier, customer_ref, po, status, employee)
VALUES
('SO-1001', 'Sullair', 'REF-A', 'PO-001', 'OPEN', 'Ron'),
('SO-1002', 'Sullair', 'REF-B', 'PO-002', 'OFFERTE', 'Ron'),
('SO-1003', 'Sullair', 'REF-C', 'PO-003', 'BESTELD', 'Ron')
""")

conn.commit()
conn.close()

print("Database aangemaakt en gevuld.")
