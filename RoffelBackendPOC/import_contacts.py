import openpyxl
from app import SessionLocal, Customer

FILE = r"C:\Users\rroff\project_maconet\RoffelBackendPOC\Aanvraag en bestellen sullair def.xlsm"  # pad aanpassen indien nodig
SHEET = "Contactgegevens"

def run():
    wb = openpyxl.load_workbook(FILE, data_only=True)
    ws = wb[SHEET]

    db = SessionLocal()

    added = 0

    for row in ws.iter_rows(min_row=2):  # skip header
        name = row[0].value
        contact = row[1].value
        email = row[2].value

        if not name:
            continue

        cust = Customer(
            name=name,
            contact=contact,
            email=email
        )

        db.add(cust)
        added += 1

    db.commit()
    db.close()

    print(f"Imported {added} customers")

if __name__ == "__main__":
    run()
