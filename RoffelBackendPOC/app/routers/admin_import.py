from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import tempfile
import os

from app.database import get_db
from app.services.duallist_importer import import_duallist_from_excel
from app.core.security import require_min_role
from app.models.user import UserRole

router = APIRouter(
    prefix="/admin/import",
    tags=["Admin Imports"],
 )

@router.post("/duallist")
def upload_duallist(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(require_min_role(UserRole.admin)),
):
    if not file.filename.endswith((".xlsx", ".xlsm", ".xls")):
        raise HTTPException(
            status_code=400,
            detail="Alleen Excel bestanden toegestaan",
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name

    try:
        result = import_duallist_from_excel(tmp_path, db)
        return {
            "status": "ok",
            **result,
        }
    finally:
        os.unlink(tmp_path)
