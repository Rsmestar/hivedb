import 'package:equatable/equatable.dart';
import '../auth/models.dart';

/// نموذج الخلية
class Cell extends Equatable {
  /// معرف الخلية
  final int id;
  
  /// مفتاح الخلية
  final String key;
  
  /// تاريخ إنشاء الخلية
  final DateTime createdAt;
  
  /// تاريخ تحديث الخلية
  final DateTime updatedAt;

  /// إنشاء خلية جديدة
  const Cell({
    required this.id,
    required this.key,
    required this.createdAt,
    required this.updatedAt,
  });

  /// إنشاء خلية من JSON
  factory Cell.fromJson(Map<String, dynamic> json) {
    return Cell(
      id: json['id'],
      key: json['key'],
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : DateTime.now(),
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'])
          : DateTime.now(),
    );
  }

  /// تحويل الخلية إلى JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'key': key,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  @override
  List<Object?> get props => [id, key, createdAt, updatedAt];
}

/// نموذج إنشاء خلية جديدة
class CellCreate {
  /// مفتاح الخلية
  final String key;
  
  /// كلمة مرور الخلية
  final String password;

  /// إنشاء نموذج إنشاء خلية جديدة
  const CellCreate({
    required this.key,
    required this.password,
  });

  /// تحويل النموذج إلى JSON
  Map<String, dynamic> toJson() {
    return {
      'key': key,
      'password': password,
    };
  }
}

/// نموذج ملكية الخلية
class CellOwnership extends Equatable {
  /// معرف الملكية
  final int id;
  
  /// المستخدم المالك
  final User user;
  
  /// الخلية المملوكة
  final Cell cell;
  
  /// مستوى الإذن (مالك، محرر، مشاهد)
  final String permissionLevel;
  
  /// تاريخ إنشاء الملكية
  final DateTime createdAt;

  /// إنشاء ملكية خلية جديدة
  const CellOwnership({
    required this.id,
    required this.user,
    required this.cell,
    required this.permissionLevel,
    required this.createdAt,
  });

  /// إنشاء ملكية خلية من JSON
  factory CellOwnership.fromJson(Map<String, dynamic> json) {
    return CellOwnership(
      id: json['id'],
      user: User.fromJson(json['user']),
      cell: Cell.fromJson(json['cell']),
      permissionLevel: json['permission_level'],
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : DateTime.now(),
    );
  }

  /// تحويل ملكية الخلية إلى JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user': user.toJson(),
      'cell': cell.toJson(),
      'permission_level': permissionLevel,
      'created_at': createdAt.toIso8601String(),
    };
  }

  @override
  List<Object?> get props => [id, user, cell, permissionLevel, createdAt];
}

/// نموذج إنشاء ملكية خلية جديدة
class CellOwnershipCreate {
  /// مفتاح الخلية
  final String cellKey;
  
  /// البريد الإلكتروني للمستخدم
  final String userEmail;
  
  /// مستوى الإذن (مالك، محرر، مشاهد)
  final String permissionLevel;

  /// إنشاء نموذج إنشاء ملكية خلية جديدة
  const CellOwnershipCreate({
    required this.cellKey,
    required this.userEmail,
    this.permissionLevel = 'editor',
  });

  /// تحويل النموذج إلى JSON
  Map<String, dynamic> toJson() {
    return {
      'cell_key': cellKey,
      'user_email': userEmail,
      'permission_level': permissionLevel,
    };
  }
}

/// نموذج عنصر بيانات الخلية
class CellDataItem extends Equatable {
  /// مفتاح البيانات
  final String key;
  
  /// قيمة البيانات
  final dynamic value;
  
  /// تاريخ الإنشاء (اختياري)
  final DateTime? createdAt;
  
  /// تاريخ التحديث (اختياري)
  final DateTime? updatedAt;

  /// إنشاء عنصر بيانات خلية جديد
  const CellDataItem({
    required this.key,
    required this.value,
    this.createdAt,
    this.updatedAt,
  });

  /// إنشاء عنصر بيانات خلية من JSON
  factory CellDataItem.fromJson(Map<String, dynamic> json) {
    return CellDataItem(
      key: json['key'],
      value: json['value'],
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : null,
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'])
          : null,
    );
  }

  /// تحويل عنصر بيانات الخلية إلى JSON
  Map<String, dynamic> toJson() {
    return {
      'key': key,
      'value': value,
      if (createdAt != null) 'created_at': createdAt!.toIso8601String(),
      if (updatedAt != null) 'updated_at': updatedAt!.toIso8601String(),
    };
  }

  @override
  List<Object?> get props => [key, value, createdAt, updatedAt];
}

/// نموذج استجابة استعلام الخلية
class CellQueryResponse extends Equatable {
  /// نتائج الاستعلام
  final List<dynamic> results;
  
  /// عدد النتائج
  final int count;

  /// إنشاء استجابة استعلام خلية جديدة
  const CellQueryResponse({
    required this.results,
    required this.count,
  });

  /// إنشاء استجابة استعلام خلية من JSON
  factory CellQueryResponse.fromJson(Map<String, dynamic> json) {
    return CellQueryResponse(
      results: json['results'] ?? [],
      count: json['count'] ?? 0,
    );
  }

  /// تحويل استجابة استعلام الخلية إلى JSON
  Map<String, dynamic> toJson() {
    return {
      'results': results,
      'count': count,
    };
  }

  @override
  List<Object?> get props => [results, count];
}
