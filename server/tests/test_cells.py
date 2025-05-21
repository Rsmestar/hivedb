"""
اختبارات وحدة لوظائف إدارة الخلايا
"""

import pytest
from fastapi import status

def test_create_cell(client, auth_headers):
    """اختبار إنشاء خلية جديدة"""
    cell_data = {
        "key": "test_cell",
        "password": "cell_password123"
    }
    response = client.post("/cells", json=cell_data, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "id" in data
    assert data["key"] == cell_data["key"]
    assert "password" not in data  # التأكد من عدم إرجاع كلمة المرور

def test_create_duplicate_cell(client, auth_headers):
    """اختبار إنشاء خلية بمفتاح موجود بالفعل"""
    # إنشاء الخلية الأولى
    cell_data = {
        "key": "duplicate_cell",
        "password": "cell_password123"
    }
    response = client.post("/cells", json=cell_data, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    
    # محاولة إنشاء خلية بنفس المفتاح
    response = client.post("/cells", json=cell_data, headers=auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "مفتاح الخلية مستخدم بالفعل" in response.json()["detail"]

def test_get_user_cells(client, auth_headers):
    """اختبار الحصول على خلايا المستخدم"""
    # إنشاء خلية للمستخدم
    cell_data = {
        "key": "user_cell",
        "password": "cell_password123"
    }
    client.post("/cells", json=cell_data, headers=auth_headers)
    
    # الحصول على خلايا المستخدم
    response = client.get("/cells", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "cells" in data
    assert len(data["cells"]) > 0
    assert any(cell["key"] == "user_cell" for cell in data["cells"])

def test_get_cell_by_key(client, auth_headers):
    """اختبار الحصول على خلية بواسطة المفتاح"""
    # إنشاء خلية
    cell_data = {
        "key": "specific_cell",
        "password": "cell_password123"
    }
    client.post("/cells", json=cell_data, headers=auth_headers)
    
    # الحصول على الخلية بواسطة المفتاح
    response = client.get("/cells/specific_cell", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["key"] == "specific_cell"

def test_get_nonexistent_cell(client, auth_headers):
    """اختبار الحصول على خلية غير موجودة"""
    response = client.get("/cells/nonexistent_cell", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "الخلية غير موجودة" in response.json()["detail"]
