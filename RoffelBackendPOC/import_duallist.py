import openpyxl
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import Article

FILE = "Aanvraag en bestellen sullair def.xlsm"
SHEET = "Duallist"

engine = create_engine("sqlite:///roffel_tool.db")
SessionLocal = sessionmaker(bind=engine)

def import_duallist():
    print("Opening Excel:", FILE)
    wb = openpyxl.load_workbook(FILE, data_only=True)
    ws = wb[SHEET]

    db = SessionLocal()

    created = 0
    updated = 0

    for row in ws.iter_rows(min_row=2):

        part_no = row[0].value
        description = row[1].value
        list_price = row[2].value
        price_bruto = row[4].value
        price_wvk = row[5].value
        price_edmac = row[6].value
        price_purchase = row[3].value

        if not part_no:
            continue

        part_no = str(part_no).strip()

        # ----------------------------------
        # check if article exists already
        # ----------------------------------
        existing = db.query(Article).filter(
            Article.part_no == part_no
        ).first()

        if existing:
            # UPDATE RECORD
            existing.description = description or ""
            existing.list_price = float(list_price or 0)
            existing.price_bruto = float(price_bruto or 0)
            existing.price_wvk = float(price_wvk or 0)
            existing.price_edmac = float(price_edmac or 0)
            existing.price_purchase = float(price_purchase or 0)

            updated += 1

        else:
            # CREATE NEW
            art = Article(
                part_no=part_no,
                description=description or "",
                list_price=float(list_price or 0),
                price_bruto=float(price_bruto or 0),
                price_wvk=float(price_wvk or 0),
                price_edmac=float(price_edmac or 0),
                price_purchase=float(price_purchase or 0),
                active=True
            )
            db.add(art)
            created += 1

    db.commit()
    db.close()

    print("Done.")
    print("Created:", created)
    print("Updated:", updated)

if __name__ == "__main__":
    import_duallist()
