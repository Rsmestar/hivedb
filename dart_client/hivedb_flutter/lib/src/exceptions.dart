/// استثناء أساسي لـ HiveDB
class HiveDBException implements Exception {
  /// رسالة الخطأ
  final String message;
  
  /// سبب الاستثناء
  final dynamic cause;

  /// إنشاء استثناء جديد
  HiveDBException(this.message, [this.cause]);

  @override
  String toString() {
    if (cause != null) {
      return 'HiveDBException: $message (Cause: $cause)';
    }
    return 'HiveDBException: $message';
  }
}

/// استثناء للخطأ في الاتصال بالخادم
class ConnectionException extends HiveDBException {
  ConnectionException(String message, [dynamic cause]) : super(message, cause);
}

/// استثناء للخطأ في المصادقة
class AuthException extends HiveDBException {
  AuthException(String message, [dynamic cause]) : super(message, cause);
}

/// استثناء للمستخدم غير المصرح له
class UnauthorizedException extends AuthException {
  UnauthorizedException(String message, [dynamic cause]) : super(message, cause);
}

/// استثناء للمستخدم غير المسموح له
class ForbiddenException extends AuthException {
  ForbiddenException(String message, [dynamic cause]) : super(message, cause);
}

/// استثناء لخطأ في واجهة برمجة التطبيقات
class ApiException extends HiveDBException {
  /// رمز حالة HTTP
  final int statusCode;

  ApiException({
    required this.statusCode,
    required String message,
    dynamic cause,
  }) : super(message, cause);

  @override
  String toString() {
    return 'ApiException: [$statusCode] $message';
  }
}

/// استثناء لخطأ في التخزين المؤقت
class CacheException extends HiveDBException {
  CacheException(String message, [dynamic cause]) : super(message, cause);
}

/// استثناء لخطأ في عمليات SGX
class SGXException extends HiveDBException {
  SGXException(String message, [dynamic cause]) : super(message, cause);
}

/// استثناء لعدم توفر SGX
class SGXNotAvailableException extends SGXException {
  SGXNotAvailableException(String message, [dynamic cause]) : super(message, cause);
}

/// استثناء لوضع عدم الاتصال
class OfflineModeException extends HiveDBException {
  OfflineModeException(String message, [dynamic cause]) : super(message, cause);
}
