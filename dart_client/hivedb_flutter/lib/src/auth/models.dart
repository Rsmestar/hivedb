import 'package:equatable/equatable.dart';

/// نموذج المستخدم
class User extends Equatable {
  /// معرف المستخدم
  final int id;
  
  /// اسم المستخدم
  final String username;
  
  /// البريد الإلكتروني
  final String email;
  
  /// ما إذا كان المستخدم نشطًا
  final bool isActive;
  
  /// ما إذا كان المستخدم مسؤولًا
  final bool isAdmin;
  
  /// تاريخ إنشاء المستخدم
  final DateTime createdAt;

  /// إنشاء مستخدم جديد
  const User({
    required this.id,
    required this.username,
    required this.email,
    required this.isActive,
    required this.isAdmin,
    required this.createdAt,
  });

  /// إنشاء مستخدم من JSON
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      username: json['username'],
      email: json['email'],
      isActive: json['is_active'] ?? true,
      isAdmin: json['is_admin'] ?? false,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : DateTime.now(),
    );
  }

  /// تحويل المستخدم إلى JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'email': email,
      'is_active': isActive,
      'is_admin': isAdmin,
      'created_at': createdAt.toIso8601String(),
    };
  }

  @override
  List<Object?> get props => [id, username, email, isActive, isAdmin, createdAt];
}

/// نموذج إنشاء مستخدم جديد
class UserCreate {
  /// اسم المستخدم
  final String username;
  
  /// البريد الإلكتروني
  final String email;
  
  /// كلمة المرور
  final String password;

  /// إنشاء نموذج إنشاء مستخدم جديد
  const UserCreate({
    required this.username,
    required this.email,
    required this.password,
  });

  /// تحويل النموذج إلى JSON
  Map<String, dynamic> toJson() {
    return {
      'username': username,
      'email': email,
      'password': password,
    };
  }
}

/// نموذج تسجيل الدخول
class UserLogin {
  /// البريد الإلكتروني
  final String email;
  
  /// كلمة المرور
  final String password;

  /// إنشاء نموذج تسجيل الدخول
  const UserLogin({
    required this.email,
    required this.password,
  });

  /// تحويل النموذج إلى JSON
  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'password': password,
    };
  }
}

/// نتيجة تسجيل الدخول
class LoginResult extends Equatable {
  /// رمز الوصول
  final String accessToken;
  
  /// نوع الرمز المميز
  final String tokenType;
  
  /// معرف المستخدم
  final int userId;
  
  /// اسم المستخدم
  final String username;
  
  /// البريد الإلكتروني
  final String email;
  
  /// ما إذا كان المستخدم مسؤولًا
  final bool isAdmin;
  
  /// رمز التحديث (اختياري)
  final String? refreshToken;

  /// إنشاء نتيجة تسجيل دخول جديدة
  const LoginResult({
    required this.accessToken,
    required this.tokenType,
    required this.userId,
    required this.username,
    required this.email,
    required this.isAdmin,
    this.refreshToken,
  });

  /// إنشاء نتيجة تسجيل دخول من JSON
  factory LoginResult.fromJson(Map<String, dynamic> json) {
    return LoginResult(
      accessToken: json['access_token'],
      tokenType: json['token_type'] ?? 'bearer',
      userId: json['user_id'],
      username: json['username'],
      email: json['email'],
      isAdmin: json['is_admin'] ?? false,
      refreshToken: json['refresh_token'],
    );
  }

  /// تحويل نتيجة تسجيل الدخول إلى JSON
  Map<String, dynamic> toJson() {
    return {
      'access_token': accessToken,
      'token_type': tokenType,
      'user_id': userId,
      'username': username,
      'email': email,
      'is_admin': isAdmin,
      if (refreshToken != null) 'refresh_token': refreshToken,
    };
  }

  @override
  List<Object?> get props => [
    accessToken,
    tokenType,
    userId,
    username,
    email,
    isAdmin,
    refreshToken,
  ];
}
