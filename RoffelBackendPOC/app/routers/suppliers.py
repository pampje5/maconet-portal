from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.supplier import Supplier
from app.schemas.supplier import (
    SupplierIn,
    SupplierOut,
    SupplierUpdate,
)
from app.core.security import require_min_role
from app.models.user import User, UserRole

router = APIRouter(
    prefix="/suppliers",
    tags=["suppliers"],
)

# =========================
# GET – lijst leveranciers
# =========================
@router.get(
    "",
    response_model=List[SupplierOut],
)
def list_suppliers(
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.user)),
):
    return (
        db.query(Supplier)
        .order_by(Supplier.name.asc())
        .all()
    )


# =========================
# GET – één leverancier
# =========================
@router.get(
    "/{supplier_id}",
    response_model=SupplierOut,
)
def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.user)),
):
    supplier = (
        db.query(Supplier)
        .filter(Supplier.id == supplier_id)
        .first()
    )

    if not supplier:
        raise HTTPException(404, "Supplier not found")

    return supplier


# =========================
# POST – nieuwe leverancier
# =========================
@router.post(
    "",
    response_model=SupplierOut,
    status_code=201,
)
def create_supplier(
    payload: SupplierIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.admin)),
):
    existing = (
        db.query(Supplier)
        .filter(Supplier.name == payload.name)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Supplier with this name already exists",
        )

    supplier = Supplier(**payload.model_dump())

    db.add(supplier)
    db.commit()
    db.refresh(supplier)

    return supplier


# =========================
# PUT – update leverancier
# =========================
@router.put(
    "/{supplier_id}",
    response_model=SupplierOut,
)
def update_supplier(
    supplier_id: int,
    payload: SupplierUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.admin)),
):
    supplier = (
        db.query(Supplier)
        .filter(Supplier.id == supplier_id)
        .first()
    )

    if not supplier:
        raise HTTPException(404, "Supplier not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(supplier, field, value)

    db.commit()
    db.refresh(supplier)

    return supplier


# =========================
# DELETE – soft delete
# =========================
@router.delete(
    "/{supplier_id}",
)
def deactivate_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.admin)),
):
    supplier = (
        db.query(Supplier)
        .filter(Supplier.id == supplier_id)
        .first()
    )

    if not supplier:
        raise HTTPException(404, "Supplier not found")

    supplier.is_active = False
    db.commit()

    return {"status": "deactivated"}
