from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from core.security import limiter, LIMITS
from core.auth_utils import hash_password, verify_password, create_access_token, get_current_user
from db.database import get_db
from db.models import User
from schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
@limiter.limit(LIMITS["sensitive"])
def register(request: Request, payload: RegisterRequest, db: Session = Depends(get_db)):
    """Create a new account. Returns a token immediately so the user is logged in."""
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        display_name=payload.display_name or payload.email.split("@")[0],
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.email)
    return TokenResponse(access_token=token, display_name=user.display_name or "")


@router.post("/login", response_model=TokenResponse)
@limiter.limit(LIMITS["sensitive"])
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate and receive a JWT token."""
    user = db.query(User).filter(User.email == payload.email).first()

    # Always run verify to prevent timing-based enumeration
    valid = user and verify_password(payload.password, user.hashed_password)
    if not valid or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = create_access_token(user.email)
    return TokenResponse(access_token=token, display_name=user.display_name or "")


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "display_name": current_user.display_name,
        "created_at": current_user.created_at.isoformat(),
    }
