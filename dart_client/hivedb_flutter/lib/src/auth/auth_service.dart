import '../http_client.dart';
import '../exceptions.dart';
import 'models.dart';
import 'token_manager.dart';

/// خدمة المصادقة للتعامل مع تسجيل الدخول والتسجيل وإدارة المستخدمين
class AuthService {
  /// عميل HTTP
  final HiveDBHttpClient _client;
  
  /// مدير الرموز المميزة
  final TokenManager _tokenManager;

  /// إنشاء خدمة مصادقة جديدة
  AuthService(this._client, this._tokenManager);

  /// تسجيل مستخدم جديد
  Future<User> register(String email, String username, String password) async {
    try {
      final response = await _client.post('/register', body: {
        'email': email,
        'username': username,
        'password': password,
      });
      
      return User.fromJson(response);
    } catch (e) {
      if (e is ApiException && e.statusCode == 400) {
        throw AuthException('فشل التسجيل: قد يكون البريد الإلكتروني أو اسم المستخدم مستخدمًا بالفعل');
      }
      rethrow;
    }
  }

  /// تسجيل الدخول باستخدام البريد الإلكتروني وكلمة المرور
  Future<LoginResult> login(String email, String password) async {
    try {
      final response = await _client.post('/token', body: {
        'email': email,
        'password': password,
      });
      
      final result = LoginResult.fromJson(response);
      
      // حفظ الرمز المميز
      await _tokenManager.saveToken(
        result.accessToken,
        refreshToken: result.refreshToken,
      );
      
      return result;
    } catch (e) {
      if (e is ApiException && e.statusCode == 401) {
        throw AuthException('فشل تسجيل الدخول: البريد الإلكتروني أو كلمة المرور غير صحيحة');
      }
      rethrow;
    }
  }

  /// تسجيل الخروج
  Future<void> logout() async {
    try {
      // محاولة تسجيل الخروج من الخادم إذا كان متصلاً
      try {
        await _client.post('/logout');
      } catch (_) {
        // تجاهل الأخطاء عند تسجيل الخروج من الخادم
      }
      
      // مسح الرموز المميزة المحلية
      await _tokenManager.clearToken();
    } catch (e) {
      throw AuthException('فشل تسجيل الخروج: $e');
    }
  }

  /// الحصول على المستخدم الحالي
  Future<User> getCurrentUser() async {
    try {
      final response = await _client.get('/users/me');
      return User.fromJson(response);
    } catch (e) {
      if (e is UnauthorizedException) {
        throw AuthException('غير مصرح به: يرجى تسجيل الدخول مرة أخرى');
      }
      rethrow;
    }
  }

  /// التحقق مما إذا كان المستخدم مسجل الدخول
  Future<bool> isLoggedIn() async {
    return await _tokenManager.isTokenValid();
  }
  
  /// تغيير كلمة المرور
  Future<bool> changePassword(String currentPassword, String newPassword) async {
    try {
      final response = await _client.post('/users/change-password', body: {
        'current_password': currentPassword,
        'new_password': newPassword,
      });
      
      return response['status'] == 'success';
    } catch (e) {
      if (e is ApiException && e.statusCode == 400) {
        throw AuthException('فشل تغيير كلمة المرور: كلمة المرور الحالية غير صحيحة');
      }
      rethrow;
    }
  }
  
  /// تحديث معلومات المستخدم
  Future<User> updateProfile({
    String? username,
    String? email,
  }) async {
    final updates = <String, dynamic>{};
    if (username != null) updates['username'] = username;
    if (email != null) updates['email'] = email;
    
    if (updates.isEmpty) {
      throw AuthException('لم يتم تحديد أي تحديثات للملف الشخصي');
    }
    
    try {
      final response = await _client.put('/users/me', body: updates);
      return User.fromJson(response);
    } catch (e) {
      if (e is ApiException && e.statusCode == 400) {
        throw AuthException('فشل تحديث الملف الشخصي: قد يكون البريد الإلكتروني أو اسم المستخدم مستخدمًا بالفعل');
      }
      rethrow;
    }
  }
  
  /// طلب إعادة تعيين كلمة المرور
  Future<bool> requestPasswordReset(String email) async {
    try {
      final response = await _client.post('/reset-password/request', body: {
        'email': email,
      });
      
      return response['status'] == 'success';
    } catch (e) {
      // لا نريد الكشف عما إذا كان البريد الإلكتروني موجودًا أم لا
      return true;
    }
  }
  
  /// إعادة تعيين كلمة المرور باستخدام الرمز
  Future<bool> resetPassword(String token, String newPassword) async {
    try {
      final response = await _client.post('/reset-password/confirm', body: {
        'token': token,
        'new_password': newPassword,
      });
      
      return response['status'] == 'success';
    } catch (e) {
      if (e is ApiException && e.statusCode == 400) {
        throw AuthException('فشل إعادة تعيين كلمة المرور: الرمز غير صالح أو منتهي الصلاحية');
      }
      rethrow;
    }
  }
  
  /// تنشيط الحساب
  Future<bool> activateAccount(String token) async {
    try {
      final response = await _client.post('/activate-account', body: {
        'token': token,
      });
      
      return response['status'] == 'success';
    } catch (e) {
      if (e is ApiException && e.statusCode == 400) {
        throw AuthException('فشل تنشيط الحساب: الرمز غير صالح أو منتهي الصلاحية');
      }
      rethrow;
    }
  }
}
