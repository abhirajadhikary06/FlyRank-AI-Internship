import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, ExpiredSignatureError, jwt
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# ---------------------------
# Load environment variables
# ---------------------------
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing in .env")

# ---------------------------
# Database setup
# ---------------------------
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ---------------------------
# FastAPI app
# ---------------------------
app = FastAPI(
    title="Auth API with FastAPI + Neon",
    description="Secure authentication API with signup, login, logout, public and protected routes.",
    version="1.0.0"
)

# ---------------------------
# Security
# ---------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

token_blacklist = set()

# ---------------------------
# Database model
# ---------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

# Create tables
Base.metadata.create_all(bind=engine)

# ---------------------------
# Pydantic schemas
# ---------------------------
class AuthRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

# ---------------------------
# Dependencies
# ---------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------
# Helper functions
# ---------------------------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required"
        )

    if token in token_blacklist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        token_type = payload.get("type")

        if email is None or token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    return user, token

# ---------------------------
# Stage 1: Signup
# ---------------------------
@app.post("/auth/signup", status_code=201)
def signup(payload: AuthRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    password = payload.password.strip()

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )

    new_user = User(
        email=email,
        hashed_password=hash_password(password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "created_at": new_user.created_at
        }
    }

# ---------------------------
# Stage 1: Login
# ---------------------------
@app.post("/auth/login", status_code=200, response_model=LoginResponse)
def login(payload: AuthRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    password = payload.password.strip()

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )

    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login credentials"
        )

    access_token = create_access_token({"sub": user.email, "user_id": user.id})
    refresh_token = create_refresh_token({"sub": user.email, "user_id": user.id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# ---------------------------
# Stage 2: Public route
# ---------------------------
@app.get("/public/info", status_code=200)
def public_info():
    return {"message": "Welcome stranger! This info is public."}

# ---------------------------
# Stage 2/3/4: Protected profile
# ---------------------------
@app.get("/protected/profile", status_code=200)
def protected_profile(current=Depends(get_current_user)):
    user, _token = current
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at
    }

# ---------------------------
# Stage 4: Another protected route
# ---------------------------
@app.get("/protected/dashboard", status_code=200)
def protected_dashboard(current=Depends(get_current_user)):
    user, _token = current
    return {
        "message": f"Welcome to your dashboard, {user.email}",
        "user_id": user.id
    }

# ---------------------------
# Stage 4: Logout
# ---------------------------
@app.post("/auth/logout", status_code=204)
def logout(current=Depends(get_current_user)):
    _user, token = current
    token_blacklist.add(token)
    return

# ---------------------------
# Root route
# ---------------------------
@app.get("/")
def root():
    return {"message": "Server running and connected to Neon"}
