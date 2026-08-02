from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.services.model_performance import evaluate_model_performance

router = APIRouter(
    prefix="/model-performance",
    tags=["Model Performance"]
)


@router.get("/summary")
def model_performance_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return evaluate_model_performance(db, current_user.account_id)
