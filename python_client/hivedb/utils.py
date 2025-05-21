"""
وحدة المساعدة لـ HiveDB
توفر وظائف التشفير وإدارة المفاتيح
"""

import base64
import hashlib
import os
import secrets
import uuid
from typing import Tuple
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def generate_cell_key() -> str:
    """
    إنشاء مفتاح خلية جديد وفريد
    
    العائد:
        str: مفتاح الخلية الجديد
    """
    # إنشاء معرف فريد باستخدام UUID وتحويله إلى سلسلة نصية
    unique_id = str(uuid.uuid4().int)[:10]
    return f"cell{unique_id}"

def hash_password(password: str, salt: bytes = None) -> str:
    """
    تجزئة كلمة المرور باستخدام SHA-256 مع ملح
    
    المعلمات:
        password: كلمة المرور للتجزئة
        salt: الملح (اختياري)
        
    العائد:
        str: كلمة المرور المجزأة بتنسيق Base64
    """
    if salt is None:
        salt = os.urandom(16)
    
    # تجزئة كلمة المرور مع الملح
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000  # عدد التكرارات
    )
    
    # دمج الملح مع التجزئة وتحويلها إلى Base64
    combined = salt + password_hash
    return base64.b64encode(combined).decode('utf-8')

def verify_password(password: str, stored_hash: str) -> bool:
    """
    التحقق من كلمة المرور مقابل التجزئة المخزنة
    
    المعلمات:
        password: كلمة المرور للتحقق منها
        stored_hash: التجزئة المخزنة بتنسيق Base64
        
    العائد:
        bool: صحة كلمة المرور
    """
    # فك ترميز التجزئة المخزنة
    combined = base64.b64decode(stored_hash.encode('utf-8'))
    
    # استخراج الملح (أول 16 بايت)
    salt = combined[:16]
    
    # التحقق من كلمة المرور
    return hash_password(password, salt) == stored_hash

def derive_key(password: str) -> bytes:
    """
    اشتقاق مفتاح تشفير من كلمة المرور
    
    المعلمات:
        password: كلمة المرور
        
    العائد:
        bytes: مفتاح التشفير (32 بايت)
    """
    return hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        b'hivedb-salt',  # ملح ثابت للاشتقاق
        50000  # عدد التكرارات
    )

def encrypt(data: str, password: str) -> str:
    """
    تشفير البيانات باستخدام AES-256-GCM
    
    المعلمات:
        data: البيانات للتشفير
        password: كلمة المرور أو مفتاح التشفير
        
    العائد:
        str: البيانات المشفرة بتنسيق Base64
    """
    # اشتقاق مفتاح التشفير
    key = derive_key(password)
    
    # إنشاء متجه التهيئة (IV)
    iv = os.urandom(16)
    
    # إنشاء شفرة AES
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # تشفير البيانات
    padded_data = pad(data.encode('utf-8'), AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    
    # دمج IV مع البيانات المشفرة
    combined = iv + encrypted_data
    
    # تحويل إلى Base64
    return base64.b64encode(combined).decode('utf-8')

def decrypt(encrypted_data: str, password: str) -> str:
    """
    فك تشفير البيانات المشفرة بـ AES-256-GCM
    
    المعلمات:
        encrypted_data: البيانات المشفرة بتنسيق Base64
        password: كلمة المرور أو مفتاح التشفير
        
    العائد:
        str: البيانات الأصلية
    """
    # اشتقاق مفتاح التشفير
    key = derive_key(password)
    
    # فك ترميز البيانات المشفرة
    combined = base64.b64decode(encrypted_data.encode('utf-8'))
    
    # استخراج IV (أول 16 بايت)
    iv = combined[:16]
    encrypted_data = combined[16:]
    
    # إنشاء شفرة AES
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # فك تشفير البيانات
    decrypted_padded = cipher.decrypt(encrypted_data)
    
    # إزالة التبطين
    decrypted_data = unpad(decrypted_padded, AES.block_size)
    
    # تحويل إلى سلسلة نصية
    return decrypted_data.decode('utf-8')

def generate_token() -> str:
    """
    إنشاء رمز جلسة آمن
    
    العائد:
        str: رمز الجلسة
    """
    return secrets.token_urlsafe(32)
