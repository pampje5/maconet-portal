from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    return {"ok": True}

@router.get("/health-test")
def test():
    return {"source": "router"}
