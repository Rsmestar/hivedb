"""
وحدة العميل الرئيسية لـ HiveDB
توفر واجهة برمجية بسيطة للتفاعل مع خلايا HiveDB
"""

import json
import os
import requests
import time
from typing import Any, Dict, List, Optional, Union
from .utils import encrypt, decrypt, hash_password

# عنوان الخادم الافتراضي
DEFAULT_SERVER = "https://api.hivedb.io"

class Cell:
    """
    فئة تمثل خلية بيانات في نظام HiveDB
    """
    
    def __init__(self, cell_key: str, password: str, server_url: str = DEFAULT_SERVER):
        """
        تهيئة اتصال بخلية HiveDB
        
        المعلمات:
            cell_key: مفتاح الخلية الفريد
            password: كلمة المرور للوصول إلى الخلية
            server_url: عنوان خادم HiveDB (اختياري)
        """
        self.cell_key = cell_key
        self.password_hash = hash_password(password)
        self.server_url = server_url
        self.session_token = None
        self.cache = {}
        
        # التحقق من الاتصال والمصادقة
        self._authenticate()
    
    def _authenticate(self) -> None:
        """
        مصادقة الاتصال بالخلية
        يرفع استثناء في حالة فشل المصادقة
        """
        try:
            response = requests.post(
                f"{self.server_url}/auth",
                json={
                    "cell_key": self.cell_key,
                    "password_hash": self.password_hash
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.session_token = data.get("session_token")
            else:
                raise ConnectionError(f"فشل المصادقة: {response.status_code} - {response.text}")
        except requests.RequestException as e:
            # في حالة عدم توفر الاتصال، نعمل في وضع غير متصل
            print(f"تحذير: العمل في وضع غير متصل - {str(e)}")
    
    def store(self, key: str, value: str) -> bool:
        """
        تخزين قيمة نصية في الخلية
        
        المعلمات:
            key: المفتاح
            value: القيمة النصية للتخزين
            
        العائد:
            bool: نجاح العملية
        """
        # تخزين في الذاكرة المؤقتة المحلية
        self.cache[key] = value
        
        # تشفير البيانات
        encrypted_value = encrypt(value, self.password_hash)
        
        # محاولة التخزين على الخادم إذا كان متصلاً
        try:
            if self.session_token:
                response = requests.post(
                    f"{self.server_url}/cells/{self.cell_key}/data",
                    headers={"Authorization": f"Bearer {self.session_token}"},
                    json={
                        "key": key,
                        "value": encrypted_value
                    }
                )
                return response.status_code == 200
            return True  # نجاح محلي فقط
        except requests.RequestException:
            return True  # نجاح محلي فقط
    
    def get(self, key: str) -> Optional[str]:
        """
        استرجاع قيمة من الخلية
        
        المعلمات:
            key: المفتاح للبحث عنه
            
        العائد:
            القيمة المخزنة أو None إذا لم يتم العثور عليها
        """
        # التحقق أولاً من الذاكرة المؤقتة المحلية
        if key in self.cache:
            return self.cache[key]
        
        # محاولة الحصول على البيانات من الخادم
        try:
            if self.session_token:
                response = requests.get(
                    f"{self.server_url}/cells/{self.cell_key}/data/{key}",
                    headers={"Authorization": f"Bearer {self.session_token}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    encrypted_value = data.get("value")
                    if encrypted_value:
                        value = decrypt(encrypted_value, self.password_hash)
                        self.cache[key] = value
                        return value
            return None
        except requests.RequestException:
            return None
    
    def delete(self, key: str) -> bool:
        """
        حذف قيمة من الخلية
        
        المعلمات:
            key: المفتاح للحذف
            
        العائد:
            bool: نجاح العملية
        """
        # حذف من الذاكرة المؤقتة المحلية
        if key in self.cache:
            del self.cache[key]
        
        # محاولة الحذف من الخادم
        try:
            if self.session_token:
                response = requests.delete(
                    f"{self.server_url}/cells/{self.cell_key}/data/{key}",
                    headers={"Authorization": f"Bearer {self.session_token}"}
                )
                return response.status_code == 200
            return True  # نجاح محلي فقط
        except requests.RequestException:
            return True  # نجاح محلي فقط
    
    def store_json(self, key: str, data: Dict[str, Any]) -> bool:
        """
        تخزين بيانات JSON في الخلية
        
        المعلمات:
            key: المفتاح
            data: بيانات Python (قاموس، قائمة، إلخ)
            
        العائد:
            bool: نجاح العملية
        """
        json_str = json.dumps(data, ensure_ascii=False)
        return self.store(key, json_str)
    
    def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """
        استرجاع بيانات JSON من الخلية
        
        المعلمات:
            key: المفتاح للبحث عنه
            
        العائد:
            البيانات المخزنة كقاموس Python أو None إذا لم يتم العثور عليها
        """
        json_str = self.get(key)
        if json_str:
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                return None
        return None
    
    def list_keys(self) -> List[str]:
        """
        الحصول على قائمة بجميع المفاتيح في الخلية
        
        العائد:
            List[str]: قائمة بالمفاتيح
        """
        try:
            if self.session_token:
                response = requests.get(
                    f"{self.server_url}/cells/{self.cell_key}/keys",
                    headers={"Authorization": f"Bearer {self.session_token}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("keys", [])
            return list(self.cache.keys())
        except requests.RequestException:
            return list(self.cache.keys())
    
    def export_data(self) -> Dict[str, str]:
        """
        تصدير جميع بيانات الخلية
        
        العائد:
            Dict[str, str]: قاموس بجميع البيانات
        """
        data = {}
        keys = self.list_keys()
        
        for key in keys:
            value = self.get(key)
            if value is not None:
                data[key] = value
        
        return data
    
    def import_data(self, data: Dict[str, str]) -> bool:
        """
        استيراد بيانات إلى الخلية
        
        المعلمات:
            data: قاموس بالبيانات للاستيراد
            
        العائد:
            bool: نجاح العملية
        """
        success = True
        for key, value in data.items():
            if not self.store(key, value):
                success = False
        
        return success


def connect(cell_key: str, password: str, server_url: str = DEFAULT_SERVER) -> Cell:
    """
    الاتصال بخلية HiveDB
    
    المعلمات:
        cell_key: مفتاح الخلية الفريد
        password: كلمة المرور للوصول إلى الخلية
        server_url: عنوان خادم HiveDB (اختياري)
        
    العائد:
        Cell: كائن خلية HiveDB
    """
    return Cell(cell_key, password, server_url)
