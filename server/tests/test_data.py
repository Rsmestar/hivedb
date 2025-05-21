"""
اختبارات وحدة لوظائف إدارة البيانات داخل الخلايا
"""

import pytest
from fastapi import status

@pytest.fixture
def test_cell(client, auth_headers):
    """إنشاء خلية اختبار"""
    cell_data = {
        "key": "data_test_cell",
        "password": "cell_password123"
    }
    response = client.post("/cells", json=cell_data, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()

def test_store_cell_data(client, auth_headers, test_cell):
    """اختبار تخزين البيانات في خلية"""
    data_item = {
        "key": "test_key",
        "value": "test_value"
    }
    response = client.post(f"/cells/{test_cell['key']}/data", json=data_item, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["status"] == "success"
    assert "key" in data
    assert data["key"] == data_item["key"]

def test_get_cell_data(client, auth_headers, test_cell):
    """اختبار الحصول على البيانات من خلية"""
    # تخزين البيانات أولاً
    data_item = {
        "key": "get_test_key",
        "value": "get_test_value"
    }
    client.post(f"/cells/{test_cell['key']}/data", json=data_item, headers=auth_headers)
    
    # الحصول على البيانات
    response = client.get(f"/cells/{test_cell['key']}/data/{data_item['key']}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["key"] == data_item["key"]
    assert data["value"] == data_item["value"]

def test_get_nonexistent_data(client, auth_headers, test_cell):
    """اختبار الحصول على بيانات غير موجودة"""
    response = client.get(f"/cells/{test_cell['key']}/data/nonexistent_key", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "البيانات غير موجودة" in response.json()["detail"]

def test_delete_cell_data(client, auth_headers, test_cell):
    """اختبار حذف البيانات من خلية"""
    # تخزين البيانات أولاً
    data_item = {
        "key": "delete_test_key",
        "value": "delete_test_value"
    }
    client.post(f"/cells/{test_cell['key']}/data", json=data_item, headers=auth_headers)
    
    # حذف البيانات
    response = client.delete(f"/cells/{test_cell['key']}/data/{data_item['key']}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    
    # التأكد من حذف البيانات
    response = client.get(f"/cells/{test_cell['key']}/data/{data_item['key']}", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_cell_keys(client, auth_headers, test_cell):
    """اختبار الحصول على مفاتيح البيانات في خلية"""
    # تخزين بعض البيانات
    for i in range(3):
        data_item = {
            "key": f"key_{i}",
            "value": f"value_{i}"
        }
        client.post(f"/cells/{test_cell['key']}/data", json=data_item, headers=auth_headers)
    
    # الحصول على المفاتيح
    response = client.get(f"/cells/{test_cell['key']}/keys", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "keys" in data
    assert len(data["keys"]) >= 3
    assert "key_0" in data["keys"]
    assert "key_1" in data["keys"]
    assert "key_2" in data["keys"]

def test_query_cell_data(client, auth_headers, test_cell):
    """اختبار استعلام البيانات في خلية"""
    # تخزين بعض البيانات
    for i in range(5):
        data_item = {
            "key": f"query_key_{i}",
            "value": {
                "name": f"item_{i}",
                "count": i * 10,
                "active": i % 2 == 0
            }
        }
        client.post(f"/cells/{test_cell['key']}/data", json=data_item, headers=auth_headers)
    
    # استعلام البيانات
    query = {
        "filter": {
            "active": True
        },
        "sort": ["count"],
        "limit": 2
    }
    response = client.post(f"/cells/{test_cell['key']}/query", json=query, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "results" in data
    assert "count" in data
    assert len(data["results"]) <= 2  # يجب ألا يتجاوز الحد
    
    # التحقق من أن النتائج تطابق المرشح
    for item in data["results"]:
        assert item["active"] is True
