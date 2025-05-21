import '../http_client.dart';
import '../exceptions.dart';
import 'models.dart';

/// خدمة الخلايا للتعامل مع إدارة الخلايا
class CellService {
  /// عميل HTTP
  final HiveDBHttpClient _client;

  /// إنشاء خدمة خلايا جديدة
  CellService(this._client);

  /// إنشاء خلية جديدة
  Future<Cell> createCell(String key, String password) async {
    try {
      final response = await _client.post('/cells', body: {
        'key': key,
        'password': password,
      });
      
      return Cell.fromJson(response);
    } catch (e) {
      if (e is ApiException && e.statusCode == 400) {
        throw HiveDBException('فشل إنشاء الخلية: قد يكون المفتاح مستخدمًا بالفعل');
      }
      rethrow;
    }
  }

  /// الحصول على جميع خلايا المستخدم
  Future<List<Cell>> getUserCells({bool useCache = true}) async {
    try {
      final response = await _client.get('/cells', useCache: useCache);
      
      final cells = response['cells'] as List<dynamic>;
      return cells.map((cell) => Cell.fromJson(cell as Map<String, dynamic>)).toList();
    } catch (e) {
      if (e is UnauthorizedException) {
        throw HiveDBException('غير مصرح به: يرجى تسجيل الدخول مرة أخرى');
      }
      rethrow;
    }
  }

  /// الحصول على خلية بواسطة المفتاح
  Future<Cell> getCell(String cellKey, {bool useCache = true}) async {
    try {
      final response = await _client.get('/cells/$cellKey', useCache: useCache);
      
      return Cell.fromJson(response);
    } catch (e) {
      if (e is ApiException && e.statusCode == 404) {
        throw HiveDBException('الخلية غير موجودة: $cellKey');
      }
      rethrow;
    }
  }
  
  /// حذف خلية
  Future<bool> deleteCell(String cellKey) async {
    try {
      final response = await _client.delete('/cells/$cellKey');
      
      return response['status'] == 'success';
    } catch (e) {
      if (e is ApiException && e.statusCode == 404) {
        throw HiveDBException('الخلية غير موجودة: $cellKey');
      }
      rethrow;
    }
  }
  
  /// مشاركة خلية مع مستخدم آخر
  Future<CellOwnership> shareCell(
    String cellKey,
    String userEmail, {
    String permissionLevel = 'editor',
  }) async {
    try {
      final response = await _client.post('/cells/$cellKey/share', body: {
        'user_email': userEmail,
        'permission_level': permissionLevel,
      });
      
      return CellOwnership.fromJson(response);
    } catch (e) {
      if (e is ApiException) {
        if (e.statusCode == 404) {
          throw HiveDBException('الخلية أو المستخدم غير موجود');
        } else if (e.statusCode == 400) {
          throw HiveDBException('فشل مشاركة الخلية: قد يكون المستخدم لديه بالفعل وصول إلى هذه الخلية');
        }
      }
      rethrow;
    }
  }
  
  /// إلغاء مشاركة خلية مع مستخدم
  Future<bool> unshareCell(String cellKey, String userEmail) async {
    try {
      final response = await _client.delete('/cells/$cellKey/share/$userEmail');
      
      return response['status'] == 'success';
    } catch (e) {
      if (e is ApiException && e.statusCode == 404) {
        throw HiveDBException('الخلية أو المستخدم غير موجود');
      }
      rethrow;
    }
  }
  
  /// الحصول على قائمة المستخدمين الذين لديهم وصول إلى خلية
  Future<List<CellOwnership>> getCellUsers(String cellKey, {bool useCache = true}) async {
    try {
      final response = await _client.get('/cells/$cellKey/users', useCache: useCache);
      
      final ownerships = response['ownerships'] as List<dynamic>;
      return ownerships.map((ownership) => CellOwnership.fromJson(ownership as Map<String, dynamic>)).toList();
    } catch (e) {
      if (e is ApiException && e.statusCode == 404) {
        throw HiveDBException('الخلية غير موجودة: $cellKey');
      }
      rethrow;
    }
  }
  
  /// تغيير مستوى إذن مستخدم لخلية
  Future<CellOwnership> changePermission(
    String cellKey,
    String userEmail,
    String permissionLevel,
  ) async {
    try {
      final response = await _client.put('/cells/$cellKey/share', body: {
        'user_email': userEmail,
        'permission_level': permissionLevel,
      });
      
      return CellOwnership.fromJson(response);
    } catch (e) {
      if (e is ApiException) {
        if (e.statusCode == 404) {
          throw HiveDBException('الخلية أو المستخدم غير موجود');
        } else if (e.statusCode == 400) {
          throw HiveDBException('فشل تغيير الإذن: قد لا يكون المستخدم لديه وصول إلى هذه الخلية');
        }
      }
      rethrow;
    }
  }
  
  /// الحصول على إحصائيات الخلية
  Future<Map<String, dynamic>> getCellStats(String cellKey, {bool useCache = true}) async {
    try {
      final response = await _client.get('/cells/$cellKey/stats', useCache: useCache);
      
      return response;
    } catch (e) {
      if (e is ApiException && e.statusCode == 404) {
        throw HiveDBException('الخلية غير موجودة: $cellKey');
      }
      rethrow;
    }
  }
}
