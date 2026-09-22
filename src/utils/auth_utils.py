import random
import os
from datetime import datetime, timedelta, timezone
from diskcache import Cache
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

cache = Cache("./app_cache")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

mail_config = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def generate_otp(email: str) -> str:
    otp = f"{random.randint(100000, 999999)}"
    cache.set(f"otp:{email}", otp, expire=600)
    return otp


def verify_otp(email: str, otp: str) -> bool:
    stored_otp = cache.get(f"otp:{email}")
    if stored_otp and stored_otp == otp:
        cache.delete(f"otp:{email}")
        return True
    return False


def revoke_token(token: str, expire_seconds: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60):
    cache.set(f"bl:{token}", True, expire=expire_seconds)


def is_token_revoked(token: str) -> bool:
    return cache.get(f"bl:{token}") is True


async def send_otp_email(email: str, otp: str, subject: str = "Your Verification OTP"):
    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=f"Your OTP code is: {otp}. It will expire in 10 minutes.",
        subtype=MessageType.plain,
    )
    fm = FastMail(mail_config)
    await fm.send_message(message)

async def send_exam_link_email(
    email: str, course_title: str, exam_link: str
):
    body = (
        f"Hello,\n\n"
        f"You requested the exam link for '{course_title}'.\n\n"
        f"Access your exam here: {exam_link}\n\n"
        f"Passing score: 80% or higher. Good luck!"
    )
    message = MessageSchema(
        subject=f"Exam Link: {course_title}",
        recipients=[email],
        body=body,
        subtype=MessageType.plain,
    )
    fm = FastMail(mail_config)
    await fm.send_message(message)