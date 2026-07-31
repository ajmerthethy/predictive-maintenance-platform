from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserLogin
from app.core.security import verify_password, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.get("/test")
def test_auth():
    return {
        "message": "Authentication router is working!"
    }


@router.post("/login")
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):

    user = (
        db.query(User)
        .filter(User.username == credentials.username)
        .first()
    )

    if not user or not verify_password(
        credentials.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = create_access_token(user.username)

    return {
        "access_token": token,
        "token_type": "bearer",
    }
