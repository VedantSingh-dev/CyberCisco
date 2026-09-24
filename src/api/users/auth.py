from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from jose import jwt, JWTError
import re

from src.database.dbConfig import get_db
from src.modals.user_models import User
from src.schemas.auth_schemas import (
    UserRegisterRequest,
    VerifyOTPRequest,
    LoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from src.utils.auth_utils import (
    hash_password,
    verify_password,
    create_access_token,
    generate_otp,
    verify_otp,
    send_otp_email,
    revoke_token,
    is_token_revoked,
    SECRET_KEY,
    ALGORITHM,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    # Extract raw string if using Pydantic's SecretStr
    password = (
        payload.password.get_secret_value()
        if hasattr(payload.password, "get_secret_value")
        else payload.password
    )

    # Check 1: Length check (8 to 12 characters)
    is_valid_len = 8 <= len(password) <= 12
from fastapi import APIRouter, Depends, Header, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import re

from src.database.dbConfig import get_db
from src.modals.user_models import User
from src.schemas.auth_schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserRegisterRequest,
    VerifyOTPRequest,
)
from src.utils.auth_utils import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    generate_otp,
    hash_password,
    is_token_revoked,
    revoke_token,
    send_otp_email,
    verify_otp,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    # 1. Safely extract raw string from Pydantic SecretStr or str
    if hasattr(payload.password, "get_secret_value"):
        raw_password = payload.password.get_secret_value()
    else:
        raw_password = str(payload.password)

    # 2. Validate Password with a single Regex:
    # - 8 to 12 characters long
    # - Contains ONLY letters and numbers (alphanumeric)
    # - Contains AT LEAST one letter AND AT LEAST one digit
    pattern = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z0-9]{8,12}$"

    if not re.match(pattern, raw_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be 8-12 characters long and contain both letters and numbers (no special characters or spaces).",
        )

    db_user = db.query(User).filter(User.email == payload.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    otp = generate_otp(payload.email)
    cache_data = {
        "full_name": payload.full_name,
        "password": hash_password(raw_password),
    }

    from src.utils.auth_utils import cache

    cache.set(f"reg:{payload.email}", cache_data, expire=600)

    await send_otp_email(payload.email, otp)
    return {"message": "OTP sent to email. Please verify to complete registration."}


@router.post("/verify-registration")
def verify_registration(payload: VerifyOTPRequest, db: Session = Depends(get_db)):
    from src.utils.auth_utils import cache

    user_data = cache.get(f"reg:{payload.email}")
    if not user_data:
        raise HTTPException(
            status_code=400, detail="Registration session expired or invalid email"
        )

    if not verify_otp(payload.email, payload.otp):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    new_user = User(
        full_name=user_data["full_name"],
        email=payload.email,
        hashed_password=user_data["password"],
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    cache.delete(f"reg:{payload.email}")

    return {"message": "Account verified and created successfully."}


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}


@router.post("/forgot-password")
async def forgot_password(
    payload: ForgotPasswordRequest, db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = generate_otp(payload.email)
    await send_otp_email(
        payload.email, otp, subject="Password Reset Verification OTP"
    )
    return {"message": "Password reset OTP sent to email"}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    if not verify_otp(payload.email, payload.otp):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hash_password(payload.new_password)
    db.commit()
    return {"message": "Password updated successfully."}


@router.post("/logout")
def logout(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Invalid authorization header")

    token = authorization.split(" ")[1]
    if is_token_revoked(token):
        raise HTTPException(status_code=400, detail="Token already logged out")

    revoke_token(token)
    return {"message": "Logged out successfully."}
    # Check 2: Contains at least one letter and at least one digit
    has_letter = bool(re.search(r"[A-Za-z]", password))
    has_digit = bool(re.search(r"\d", password))

    # Check 3: Strictly alphanumeric (no special characters/spaces)
    # Note: Remove `and is_alphanumeric` below if you WANT special characters to be allowed.
    is_alphanumeric = bool(re.match(r"^[A-Za-z0-9]+$", password))

    if not (is_valid_len and has_letter and has_digit and is_alphanumeric):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be 8-12 characters long and contain both letters and numbers.",
        )

    db_user = db.query(User).filter(User.email == payload.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    otp = generate_otp(payload.email)
    cache_data = {
        "full_name": payload.full_name,
        "password": hash_password(password),
    }

    from src.utils.auth_utils import cache

    cache.set(f"reg:{payload.email}", cache_data, expire=600)

    await send_otp_email(payload.email, otp)
    return {"message": "OTP sent to email. Please verify to complete registration."}

@router.post("/verify-registration")
def verify_registration(payload: VerifyOTPRequest, db: Session = Depends(get_db)):
    from src.utils.auth_utils import cache

    user_data = cache.get(f"reg:{payload.email}")
    if not user_data:
        raise HTTPException(
            status_code=400, detail="Registration session expired or invalid email"
        )

    if not verify_otp(payload.email, payload.otp):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    new_user = User(
        full_name=user_data["full_name"],
        email=payload.email,
        hashed_password=user_data["password"],
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    cache.delete(f"reg:{payload.email}")

    return {"message": "Account verified and created successfully."}


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}


@router.post("/forgot-password")
async def forgot_password(
    payload: ForgotPasswordRequest, db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = generate_otp(payload.email)
    await send_otp_email(
        payload.email, otp, subject="Password Reset Verification OTP"
    )
    return {"message": "Password reset OTP sent to email"}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    if not verify_otp(payload.email, payload.otp):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hash_password(payload.new_password)
    db.commit()
    return {"message": "Password updated successfully."}


@router.post("/logout")
def logout(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Invalid authorization header")

    token = authorization.split(" ")[1]
    if is_token_revoked(token):
        raise HTTPException(status_code=400, detail="Token already logged out")

    revoke_token(token)
    return {"message": "Logged out successfully."}