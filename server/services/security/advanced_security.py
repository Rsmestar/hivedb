"""
نظام أمان متقدم لـ HiveDB
يوفر طبقات حماية إضافية تتفوق على إمكانيات Directus
"""

import logging
import secrets
import hashlib
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.orm import Session
from ..database.models import User, AuditLog, SecuritySettings
from ..database import get_db

logger = logging.getLogger(__name__)

# إعدادات الأمان
SECRET_KEY = "YOUR_SECRET_KEY_HERE"  # يجب تغييره واستخدام متغير بيئي
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# إنشاء كائن تشفير كلمات المرور
password_hasher = PasswordHasher(
    time_cost=2,      # عدد التكرارات
    memory_cost=65536,  # استخدام الذاكرة بالكيلوبايت
    parallelism=4,    # عدد المعالجات المتوازية
    hash_len=32,      # طول التجزئة
    salt_len=16       # طول الملح
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

class AdvancedSecurity:
    """نظام أمان متقدم لـ HiveDB"""
    
    def __init__(self):
        self.rate_limit_cache = {}
        self.blocked_ips = set()
        self.suspicious_activities = []
        self.security_settings = {}
        self.load_security_settings()
    
    def load_security_settings(self, db: Optional[Session] = None):
        """تحميل إعدادات الأمان من قاعدة البيانات"""
        try:
            if db:
                settings = db.query(SecuritySettings).first()
                if settings:
                    self.security_settings = json.loads(settings.settings_json)
                else:
                    # إعدادات افتراضية
                    self.security_settings = {
                        "max_login_attempts": 5,
                        "lockout_duration_minutes": 30,
                        "password_min_length": 8,
                        "password_require_uppercase": True,
                        "password_require_lowercase": True,
                        "password_require_numbers": True,
                        "password_require_special": True,
                        "session_timeout_minutes": 30,
                        "enable_2fa": True,
                        "ip_rate_limit": 100,  # عدد الطلبات في الدقيقة
                        "enable_audit_logging": True,
                        "sensitive_data_encryption": True
                    }
            else:
                # إعدادات افتراضية
                self.security_settings = {
                    "max_login_attempts": 5,
                    "lockout_duration_minutes": 30,
                    "password_min_length": 8,
                    "password_require_uppercase": True,
                    "password_require_lowercase": True,
                    "password_require_numbers": True,
                    "password_require_special": True,
                    "session_timeout_minutes": 30,
                    "enable_2fa": True,
                    "ip_rate_limit": 100,  # عدد الطلبات في الدقيقة
                    "enable_audit_logging": True,
                    "sensitive_data_encryption": True
                }
        except Exception as e:
            logger.error(f"Error loading security settings: {e}")
            # إعدادات افتراضية في حالة الخطأ
            self.security_settings = {
                "max_login_attempts": 5,
                "lockout_duration_minutes": 30,
                "password_min_length": 8,
                "password_require_uppercase": True,
                "password_require_lowercase": True,
                "password_require_numbers": True,
                "password_require_special": True,
                "session_timeout_minutes": 30,
                "enable_2fa": True,
                "ip_rate_limit": 100,
                "enable_audit_logging": True,
                "sensitive_data_encryption": True
            }
    
    def hash_password(self, password: str) -> str:
        """تشفير كلمة المرور باستخدام Argon2"""
        return password_hasher.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """التحقق من كلمة المرور"""
        try:
            return password_hasher.verify(hashed_password, plain_password)
        except VerifyMismatchError:
            return False
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """التحقق من قوة كلمة المرور"""
        min_length = self.security_settings.get("password_min_length", 8)
        require_uppercase = self.security_settings.get("password_require_uppercase", True)
        require_lowercase = self.security_settings.get("password_require_lowercase", True)
        require_numbers = self.security_settings.get("password_require_numbers", True)
        require_special = self.security_settings.get("password_require_special", True)
        
        errors = []
        
        if len(password) < min_length:
            errors.append(f"يجب أن تكون كلمة المرور {min_length} أحرف على الأقل")
        
        if require_uppercase and not any(c.isupper() for c in password):
            errors.append("يجب أن تحتوي كلمة المرور على حرف كبير واحد على الأقل")
        
        if require_lowercase and not any(c.islower() for c in password):
            errors.append("يجب أن تحتوي كلمة المرور على حرف صغير واحد على الأقل")
        
        if require_numbers and not any(c.isdigit() for c in password):
            errors.append("يجب أن تحتوي كلمة المرور على رقم واحد على الأقل")
        
        if require_special and not any(not c.isalnum() for c in password):
            errors.append("يجب أن تحتوي كلمة المرور على حرف خاص واحد على الأقل")
        
        # حساب قوة كلمة المرور
        strength = 0
        if len(password) >= min_length:
            strength += 1
        if any(c.isupper() for c in password):
            strength += 1
        if any(c.islower() for c in password):
            strength += 1
        if any(c.isdigit() for c in password):
            strength += 1
        if any(not c.isalnum() for c in password):
            strength += 1
        
        strength_percentage = (strength / 5) * 100
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "strength_percentage": strength_percentage,
            "strength_text": self._get_strength_text(strength_percentage)
        }
    
    def _get_strength_text(self, percentage: float) -> str:
        """الحصول على وصف لقوة كلمة المرور"""
        if percentage < 20:
            return "ضعيفة جدًا"
        elif percentage < 40:
            return "ضعيفة"
        elif percentage < 60:
            return "متوسطة"
        elif percentage < 80:
            return "قوية"
        else:
            return "قوية جدًا"
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """إنشاء رمز وصول JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """إنشاء رمز تحديث JWT"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "refresh": True})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """التحقق من صحة الرمز وفك تشفيره"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="رمز غير صالح",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
        """الحصول على المستخدم الحالي من الرمز"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="لا يمكن التحقق من بيانات الاعتماد",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = self.verify_token(token)
            user_id: int = payload.get("sub")
            if user_id is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise credentials_exception
        
        return user
    
    async def rate_limit_middleware(self, request: Request, db: Session = Depends(get_db)):
        """وسيط للحد من معدل الطلبات"""
        if not self.security_settings.get("ip_rate_limit", 0):
            return
        
        client_ip = request.client.host
        
        # التحقق من الحظر
        if client_ip in self.blocked_ips:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="تم حظر عنوان IP الخاص بك بسبب نشاط مشبوه"
            )
        
        # التحقق من معدل الطلبات
        current_time = datetime.now()
        if client_ip in self.rate_limit_cache:
            requests = self.rate_limit_cache[client_ip]["requests"]
            last_request_time = self.rate_limit_cache[client_ip]["last_request"]
            
            # إعادة تعيين العداد بعد دقيقة
            if (current_time - last_request_time).total_seconds() > 60:
                self.rate_limit_cache[client_ip] = {
                    "requests": 1,
                    "last_request": current_time
                }
            else:
                # زيادة العداد
                self.rate_limit_cache[client_ip]["requests"] += 1
                self.rate_limit_cache[client_ip]["last_request"] = current_time
                
                # التحقق من تجاوز الحد
                if requests > self.security_settings.get("ip_rate_limit", 100):
                    # تسجيل النشاط المشبوه
                    self._log_suspicious_activity(db, client_ip, "rate_limit_exceeded")
                    
                    # حظر مؤقت
                    self.blocked_ips.add(client_ip)
                    
                    # إزالة الحظر بعد فترة
                    async def remove_block():
                        import asyncio
                        await asyncio.sleep(self.security_settings.get("lockout_duration_minutes", 30) * 60)
                        if client_ip in self.blocked_ips:
                            self.blocked_ips.remove(client_ip)
                    
                    # تشغيل مهمة إزالة الحظر
                    import asyncio
                    asyncio.create_task(remove_block())
                    
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="تم تجاوز الحد المسموح به من الطلبات"
                    )
        else:
            # أول طلب من هذا العنوان
            self.rate_limit_cache[client_ip] = {
                "requests": 1,
                "last_request": current_time
            }
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """تشفير البيانات الحساسة"""
        if not self.security_settings.get("sensitive_data_encryption", True):
            return data
        
        # إنشاء مفتاح تشفير فريد
        key = hashlib.sha256(SECRET_KEY.encode()).digest()
        
        # استخدام التشفير المتماثل AES
        from cryptography.fernet import Fernet
        f = Fernet(base64.b64encode(key))
        encrypted_data = f.encrypt(data.encode())
        
        return encrypted_data.decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """فك تشفير البيانات الحساسة"""
        if not self.security_settings.get("sensitive_data_encryption", True):
            return encrypted_data
        
        # إنشاء مفتاح التشفير
        key = hashlib.sha256(SECRET_KEY.encode()).digest()
        
        # فك التشفير
        from cryptography.fernet import Fernet
        f = Fernet(base64.b64encode(key))
        decrypted_data = f.decrypt(encrypted_data.encode())
        
        return decrypted_data.decode()
    
    def generate_csrf_token(self) -> str:
        """إنشاء رمز CSRF"""
        return secrets.token_hex(32)
    
    def verify_csrf_token(self, request_token: str, session_token: str) -> bool:
        """التحقق من رمز CSRF"""
        return request_token == session_token
    
    def _log_suspicious_activity(self, db: Session, ip: str, activity_type: str):
        """تسجيل النشاط المشبوه"""
        if not self.security_settings.get("enable_audit_logging", True):
            return
        
        log = AuditLog(
            user_id=None,
            action_type="security_alert",
            action=f"Suspicious activity: {activity_type}",
            resource_type="security",
            resource_id=None,
            ip_address=ip,
            timestamp=datetime.utcnow()
        )
        
        db.add(log)
        db.commit()
        
        # إضافة إلى قائمة الأنشطة المشبوهة
        self.suspicious_activities.append({
            "ip": ip,
            "activity_type": activity_type,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def log_auth_failure(self, db: Session, email: str, ip: str):
        """تسجيل فشل المصادقة وتطبيق سياسة الإغلاق"""
        # تسجيل الفشل
        log = AuditLog(
            user_id=None,
            action_type="auth_failure",
            action=f"Failed login attempt for email: {email}",
            resource_type="auth",
            resource_id=None,
            ip_address=ip,
            timestamp=datetime.utcnow()
        )
        
        db.add(log)
        db.commit()
        
        # التحقق من عدد محاولات الفشل
        max_attempts = self.security_settings.get("max_login_attempts", 5)
        lockout_duration = self.security_settings.get("lockout_duration_minutes", 30)
        
        # الحصول على محاولات الفشل الأخيرة
        recent_time = datetime.utcnow() - timedelta(minutes=lockout_duration)
        failed_attempts = db.query(AuditLog).filter(
            AuditLog.action_type == "auth_failure",
            AuditLog.action.like(f"%{email}%"),
            AuditLog.timestamp >= recent_time
        ).count()
        
        if failed_attempts >= max_attempts:
            # تسجيل محاولة اختراق محتملة
            self._log_suspicious_activity(db, ip, "multiple_auth_failures")
            
            # إغلاق الحساب مؤقتًا
            user = db.query(User).filter(User.email == email).first()
            if user:
                user.is_locked = True
                user.locked_until = datetime.utcnow() + timedelta(minutes=lockout_duration)
                db.commit()
    
    def check_account_lockout(self, db: Session, email: str) -> bool:
        """التحقق من إغلاق الحساب"""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False
        
        if user.is_locked and user.locked_until:
            if user.locked_until > datetime.utcnow():
                return True
            else:
                # إلغاء الإغلاق بعد انتهاء المدة
                user.is_locked = False
                user.locked_until = None
                db.commit()
        
        return False
    
    def log_security_event(self, db: Session, user_id: Optional[int], event_type: str, details: str, ip: str):
        """تسجيل حدث أمني"""
        if not self.security_settings.get("enable_audit_logging", True):
            return
        
        log = AuditLog(
            user_id=user_id,
            action_type="security_event",
            action=f"{event_type}: {details}",
            resource_type="security",
            resource_id=None,
            ip_address=ip,
            timestamp=datetime.utcnow()
        )
        
        db.add(log)
        db.commit()
    
    def generate_2fa_secret(self) -> str:
        """إنشاء سر للمصادقة الثنائية"""
        import pyotp
        return pyotp.random_base32()
    
    def get_2fa_qr_code_url(self, email: str, secret: str) -> str:
        """الحصول على رابط رمز QR للمصادقة الثنائية"""
        import pyotp
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=email, issuer_name="HiveDB")
    
    def verify_2fa_code(self, secret: str, code: str) -> bool:
        """التحقق من رمز المصادقة الثنائية"""
        import pyotp
        totp = pyotp.TOTP(secret)
        return totp.verify(code)

# إنشاء نسخة واحدة من نظام الأمان
advanced_security = AdvancedSecurity()
