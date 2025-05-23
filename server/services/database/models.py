"""
نماذج قاعدة البيانات الأساسية لـ HiveDB
يحتوي على تعريفات جداول قاعدة البيانات والعلاقات بينها
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    """نموذج المستخدم"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(200))
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    hives = relationship("HiveOwnership", back_populates="user")
    cells = relationship("CellOwnership", back_populates="user")

class Hive(Base):
    """نموذج خلية النحل (قاعدة البيانات)"""
    __tablename__ = "hives"
    
    id = Column(Integer, primary_key=True, index=True)
    hive_id = Column(String(50), unique=True, index=True)
    name = Column(String(100), index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    owners = relationship("HiveOwnership", back_populates="hive")
    cells = relationship("Cell", back_populates="hive")

class HiveOwnership(Base):
    """نموذج ملكية خلية النحل"""
    __tablename__ = "hive_ownerships"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    hive_id = Column(Integer, ForeignKey("hives.id"))
    permission_level = Column(String(20), default="owner")  # owner, editor, viewer
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # العلاقات
    user = relationship("User", back_populates="hives")
    hive = relationship("Hive", back_populates="owners")

class Cell(Base):
    """نموذج الخلية (وحدة تخزين البيانات)"""
    __tablename__ = "cells"
    
    id = Column(Integer, primary_key=True, index=True)
    cell_id = Column(String(50), unique=True, index=True)
    hive_id = Column(Integer, ForeignKey("hives.id"))
    coordinates = Column(String(20), index=True)  # تنسيق: "x,y"
    data_type = Column(String(20))  # json, binary, key_value, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    hive = relationship("Hive", back_populates="cells")
    owners = relationship("CellOwnership", back_populates="cell")
    data_items = relationship("CellData", back_populates="cell")

class CellOwnership(Base):
    """نموذج ملكية الخلية"""
    __tablename__ = "cell_ownerships"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    cell_id = Column(Integer, ForeignKey("cells.id"))
    permission_level = Column(String(20), default="owner")  # owner, editor, viewer
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # العلاقات
    user = relationship("User", back_populates="cells")
    cell = relationship("Cell", back_populates="owners")

class CellData(Base):
    """نموذج بيانات الخلية"""
    __tablename__ = "cell_data"
    
    id = Column(Integer, primary_key=True, index=True)
    cell_id = Column(Integer, ForeignKey("cells.id"))
    key = Column(String(100), index=True)
    value_text = Column(Text, nullable=True)
    value_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    cell = relationship("Cell", back_populates="data_items")

class ApiKey(Base):
    """نموذج مفتاح API"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    key = Column(String(100), unique=True, index=True)
    name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # العلاقات
    user = relationship("User")

class AuditLog(Base):
    """نموذج سجل المراجعة"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(50))
    resource_type = Column(String(50))
    resource_id = Column(String(50))
    details = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # العلاقات
    user = relationship("User")
