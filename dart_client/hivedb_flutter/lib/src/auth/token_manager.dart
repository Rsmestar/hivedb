import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:jwt_decoder/jwt_decoder.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../exceptions.dart';

/// مدير الرموز المميزة للمصادقة
class TokenManager {
  static const String _tokenKey = 'hivedb_auth_token';
  static const String _refreshTokenKey = 'hivedb_refresh_token';
  static const String _userDataKey = 'hivedb_user_data';
  
  final FlutterSecureStorage _secureStorage;
  
  /// إنشاء مدير رموز مميزة جديد
  TokenManager({FlutterSecureStorage? secureStorage}) 
      : _secureStorage = secureStorage ?? const FlutterSecureStorage();
  
  /// حفظ رمز الوصول
  Future<void> saveToken(String token, {String? refreshToken}) async {
    try {
      await _secureStorage.write(key: _tokenKey, value: token);
      
      if (refreshToken != null) {
        await _secureStorage.write(key: _refreshTokenKey, value: refreshToken);
      }
      
      // استخراج بيانات المستخدم من الرمز المميز وتخزينها
      final Map<String, dynamic> decodedToken = JwtDecoder.decode(token);
      
      if (decodedToken.containsKey('user_id') || 
          decodedToken.containsKey('sub')) {
        final userData = <String, dynamic>{
          'userId': decodedToken['user_id'] ?? decodedToken['sub'],
          'username': decodedToken['username'] ?? '',
          'email': decodedToken['email'] ?? '',
          'isAdmin': decodedToken['is_admin'] ?? false,
        };
        
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString(_userDataKey, jsonEncode(userData));
      }
    } catch (e) {
      throw AuthException('فشل في حفظ الرمز المميز: $e');
    }
  }
  
  /// الحصول على رمز الوصول
  Future<String?> getToken() async {
    try {
      return await _secureStorage.read(key: _tokenKey);
    } catch (e) {
      throw AuthException('فشل في قراءة الرمز المميز: $e');
    }
  }
  
  /// الحصول على رمز التحديث
  Future<String?> getRefreshToken() async {
    try {
      return await _secureStorage.read(key: _refreshTokenKey);
    } catch (e) {
      throw AuthException('فشل في قراءة رمز التحديث: $e');
    }
  }
  
  /// مسح الرموز المميزة
  Future<void> clearToken() async {
    try {
      await _secureStorage.delete(key: _tokenKey);
      await _secureStorage.delete(key: _refreshTokenKey);
      
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_userDataKey);
    } catch (e) {
      throw AuthException('فشل في مسح الرمز المميز: $e');
    }
  }
  
  /// التحقق مما إذا كان الرمز المميز صالحًا
  Future<bool> isTokenValid() async {
    try {
      final token = await getToken();
      if (token == null) return false;
      
      // التحقق من صلاحية الرمز المميز
      return !JwtDecoder.isExpired(token);
    } catch (e) {
      return false;
    }
  }
  
  /// الحصول على بيانات المستخدم المخزنة
  Future<Map<String, dynamic>?> getUserData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final userDataString = prefs.getString(_userDataKey);
      
      if (userDataString == null) return null;
      
      return jsonDecode(userDataString) as Map<String, dynamic>;
    } catch (e) {
      throw AuthException('فشل في قراءة بيانات المستخدم: $e');
    }
  }
  
  /// الحصول على معرف المستخدم
  Future<String?> getUserId() async {
    final userData = await getUserData();
    return userData?['userId']?.toString();
  }
  
  /// التحقق مما إذا كان المستخدم مسؤولًا
  Future<bool> isAdmin() async {
    final userData = await getUserData();
    return userData?['isAdmin'] == true;
  }
}
