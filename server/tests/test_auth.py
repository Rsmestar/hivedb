"""
اختبارات وحدة لوظائف المصادقة
"""

import pytest
from fastapi import status

def test_register_user(client):
    """اختبار تسجيل مستخدم جديد"""
    user_data = {
        "email": "newuser@example.com",
        "password": "securepassword123",
        "full_name": "New User"
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "id" in data
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "password" not in data  # التأكد من عدم إرجاع كلمة المرور

def test_register_duplicate_email(client, test_user):
    """اختبار تسجيل مستخدم بالبريد الإلكتروني نفسه"""
    user_data = {
        "email": "test@example.com",  # بريد إلكتروني موجود بالفعل
        "password": "anotherpassword123",
        "full_name": "Duplicate User"
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "البريد الإلكتروني مسجل بالفعل" in response.json()["detail"]

def test_login_success(client, test_user):
    """اختبار تسجيل الدخول الناجح"""
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    response = client.post("/token", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    """اختبار تسجيل الدخول بيانات اعتماد غير صالحة"""
    login_data = {
        "username": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/token", data=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "بيانات الاعتماد غير صحيحة" in response.json()["detail"]

def test_get_current_user(client, auth_headers):
    """اختبار الحصول على المستخدم الحالي"""
    response = client.get("/users/me", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password" not in data
