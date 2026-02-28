from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from sqlalchemy.orm import Session

from . import models
from .database import get_db

SECRET_KEY = "jscorp-hr-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)


_BCRYPT_MAX_BYTES = 72


def _truncate_for_bcrypt(s: str) -> str:
    if not isinstance(s, str):
        s = str(s) if s is not None else ""
    b = s.encode("utf-8")
    if len(b) <= _BCRYPT_MAX_BYTES:
        return s
    out = b[:_BCRYPT_MAX_BYTES].decode("utf-8", errors="ignore")
    return out if out else "\x00"


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(_truncate_for_bcrypt(plain), hashed)
    except ValueError:
        return False


def get_password_hash(password: str) -> str:
    password = password if isinstance(password, str) else (str(password) if password is not None else "")
    pwd = _truncate_for_bcrypt(password)
    try:
        return pwd_context.hash(pwd)
    except ValueError as e:
        if "72 bytes" not in str(e):
            raise
        pwd = (password.encode("utf-8")[: _BCRYPT_MAX_BYTES]).decode("utf-8", errors="ignore") or "\x00"
        return pwd_context.hash(pwd)


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> models.User:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username = decode_token(credentials.credentials)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_admin(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if current_user.username != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin only",
        )
    return current_user
