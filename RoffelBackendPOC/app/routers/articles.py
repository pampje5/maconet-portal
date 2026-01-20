from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.article import Article
from app.schemas.article import ArticleOut
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter(
    prefix="/articles",
    tags=["Articles"],
)

@router.get("/{part_no}", response_model=ArticleOut)
def get_article(
    part_no: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rec = db.query(Article).filter(Article.part_no == part_no).first()
    if not rec:
        raise HTTPException(404, "Article not found")
    return rec
