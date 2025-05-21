"""
ملف تكوين pytest
يحتوي على التجهيزات (fixtures) المشتركة للاختبارات
"""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from services.database import Base, get_db
from main import app

# إنشاء قاعدة بيانات اختبار في الذاكرة
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def test_db_engine():
    """إنشاء محرك قاعدة بيانات للاختبار"""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test.db"):
        os.remove("./test.db")

@pytest.fixture(scope="function")
def db_session(test_db_engine):
    """إنشاء جلسة قاعدة بيانات للاختبار"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def client(db_session):
    """إنشاء عميل اختبار للتطبيق"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_user(client, db_session):
    """إنشاء مستخدم اختبار"""
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 201
    return response.json()

@pytest.fixture(scope="function")
def auth_headers(client, test_user):
    """الحصول على رؤوس المصادقة للمستخدم"""
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
