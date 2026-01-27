from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.serviceorder_log import ServiceOrderLogOut
from app.services.serviceorder_logs import get_serviceorder_logs
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/serviceorders",
    tags=["serviceorders"],
)


@router.get(
    "/{so}/log",
    response_model=list[ServiceOrderLogOut],
)
def get_serviceorder_log(
    so: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve the event log (history) for a service order.
    """
    logs = get_serviceorder_logs(db, so)

    if logs is None:
        raise HTTPException(status_code=404, detail="Serviceorder not found")

    return logs
