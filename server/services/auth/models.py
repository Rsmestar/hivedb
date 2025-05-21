from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cells = relationship("CellOwnership", back_populates="user")
    
class Cell(Base):
    __tablename__ = "cells"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owners = relationship("CellOwnership", back_populates="cell")

class CellOwnership(Base):
    __tablename__ = "cell_ownerships"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    cell_id = Column(Integer, ForeignKey("cells.id"))
    permission_level = Column(String, default="owner")  # owner, editor, viewer
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="cells")
    cell = relationship("Cell", back_populates="owners")

# Pydantic Models for API
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        orm_mode = True

class CellBase(BaseModel):
    key: str

class CellCreate(CellBase):
    password: str

class CellResponse(CellBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class CellOwnershipCreate(BaseModel):
    cell_key: str
    user_email: EmailStr
    permission_level: str = "editor"

class CellOwnershipResponse(BaseModel):
    id: int
    user: UserResponse
    cell: CellResponse
    permission_level: str
    created_at: datetime
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str
    email: str
    is_admin: bool

class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None
    is_admin: Optional[bool] = False
