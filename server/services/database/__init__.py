"""
وحدة قاعدة البيانات الأساسية لـ HiveDB
توفر اتصالًا بقاعدة البيانات وتعريفات النماذج الأساسية
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# استخدام قاعدة بيانات SQLite للتطوير المحلي وقاعدة بيانات PostgreSQL في الإنتاج
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hivedb.db")

# تعديل سلسلة الاتصال لـ PostgreSQL على Render
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# إنشاء محرك قاعدة البيانات
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# إنشاء جلسة قاعدة البيانات
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# قاعدة النموذج التي سترث منها جميع النماذج
Base = declarative_base()

# دالة للحصول على جلسة قاعدة البيانات
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
