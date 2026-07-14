from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel, Field
from typing import List
import uvicorn
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer

# Creating the SQLite database
DATABASE_URL = "sqlite:///./users.db"

# Database engine and session setup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}) # Engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Database Session
Base = declarative_base() # parent class of SQLAlchemy models

# Defining the User model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

# Create the table in database
Base.metadata.create_all(bind=engine)

class UserCreate(BaseModel):
    username: str = Field(min_length=4, max_length=20)
    password: str = Field(min_length=8)

class UserRead(BaseModel):
    id: int
    username: str
    is_active: bool

    class Config:
        from_attributes = True

# This function creates a new database session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

# Home route
@app.get("/")
def home():
    return {"message": "Welcome to the FastAPI application! - Week3 - FlyRank AI Internship"}

# Get all users
@app.get("/users", response_model=List[UserRead])
def read_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

# Create a user
@app.post("/users", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(username=user.username, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Get a user by ID
@app.get("/users/{user_id}", response_model=UserRead)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Update a user by ID
@app.put("/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.username = user.username
    db_user.password = user.password
    db.commit()
    db.refresh(db_user)
    return db_user

# Delete a user by ID
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}

# Login
@app.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username, User.password == user.password).first()
    if db_user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return RedirectResponse(url=f"/profile?user_id={db_user.id}")

# Logout
@app.post("/logout")
def logout():
    return RedirectResponse(url="/")

# Profile Route
@app.get("/profile")
def profile(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": db_user.username, "is_active": db_user.is_active}

# Register
@app.post("/register", response_model=UserRead)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    new_user = User(username=user.username, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Run the application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)