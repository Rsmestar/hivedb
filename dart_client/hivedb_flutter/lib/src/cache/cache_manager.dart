import 'dart:convert';
import 'package:path_provider/path_provider.dart';
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart' as path;
import 'package:uuid/uuid.dart';
import '../config.dart';

/// مدير ذاكرة التخزين المؤقت لتخزين البيانات محليًا
class CacheManager {
  /// تكوين HiveDB
  final HiveDBConfig config;
  
  /// قاعدة البيانات المحلية
  late Database _database;
  
  /// معرف UUID
  final _uuid = const Uuid();
  
  /// إنشاء مدير ذاكرة تخزين مؤقت جديد
  CacheManager(this.config);
  
  /// تهيئة مدير ذاكرة التخزين المؤقت
  Future<void> initialize() async {
    final databasePath = await _getDatabasePath();
    _database = await openDatabase(
      databasePath,
      version: 1,
      onCreate: (db, version) async {
        // إنشاء جدول التخزين المؤقت
        await db.execute('''
          CREATE TABLE cache (
            key TEXT PRIMARY KEY,
            value TEXT,
            expires_at INTEGER
          )
        ''');
        
        // إنشاء جدول العمليات غير المتصلة
        await db.execute('''
          CREATE TABLE offline_operations (
            id TEXT PRIMARY KEY,
            method TEXT,
            path TEXT,
            body TEXT,
            created_at INTEGER
          )
        ''');
      },
    );
    
    // تنظيف العناصر منتهية الصلاحية
    await _cleanExpiredItems();
  }
  
  /// الحصول على مسار قاعدة البيانات
  Future<String> _getDatabasePath() async {
    if (config.cacheDirectory != null) {
      return path.join(config.cacheDirectory!, 'hivedb_cache.db');
    }
    
    final directory = await getApplicationDocumentsDirectory();
    return path.join(directory.path, 'hivedb_cache.db');
  }
  
  /// تنظيف العناصر منتهية الصلاحية
  Future<void> _cleanExpiredItems() async {
    final now = DateTime.now().millisecondsSinceEpoch;
    await _database.delete(
      'cache',
      where: 'expires_at < ?',
      whereArgs: [now],
    );
  }
  
  /// تخزين بيانات في ذاكرة التخزين المؤقت
  Future<void> set(
    String key,
    Map<String, dynamic> value, {
    Duration? duration,
  }) async {
    final expiresAt = DateTime.now().add(
      duration ?? config.cacheTTL,
    ).millisecondsSinceEpoch;
    
    await _database.insert(
      'cache',
      {
        'key': key,
        'value': jsonEncode(value),
        'expires_at': expiresAt,
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }
  
  /// الحصول على بيانات من ذاكرة التخزين المؤقت
  Future<Map<String, dynamic>?> get(String key) async {
    // تنظيف العناصر منتهية الصلاحية
    await _cleanExpiredItems();
    
    final result = await _database.query(
      'cache',
      where: 'key = ?',
      whereArgs: [key],
    );
    
    if (result.isEmpty) {
      return null;
    }
    
    final value = result.first['value'] as String;
    return jsonDecode(value) as Map<String, dynamic>;
  }
  
  /// إبطال عنصر في ذاكرة التخزين المؤقت
  Future<void> invalidate(String key) async {
    await _database.delete(
      'cache',
      where: 'key = ?',
      whereArgs: [key],
    );
  }
  
  /// إبطال عناصر ذاكرة التخزين المؤقت التي تطابق نمطًا
  Future<int> invalidatePattern(String pattern) async {
    final result = await _database.delete(
      'cache',
      where: 'key LIKE ?',
      whereArgs: ['%$pattern%'],
    );
    
    return result;
  }
  
  /// مسح جميع ذاكرة التخزين المؤقت
  Future<void> clear() async {
    await _database.delete('cache');
  }
  
  /// إضافة عملية إلى قائمة انتظار وضع عدم الاتصال
  Future<String> queueOfflineOperation(
    String method,
    String path,
    Map<String, dynamic>? body,
  ) async {
    final id = _uuid.v4();
    final createdAt = DateTime.now().millisecondsSinceEpoch;
    
    await _database.insert(
      'offline_operations',
      {
        'id': id,
        'method': method,
        'path': path,
        'body': body != null ? jsonEncode(body) : null,
        'created_at': createdAt,
      },
    );
    
    return id;
  }
  
  /// الحصول على العمليات غير المتصلة
  Future<List<Map<String, dynamic>>> getOfflineOperations() async {
    final result = await _database.query(
      'offline_operations',
      orderBy: 'created_at ASC',
    );
    
    return result.map((row) {
      final bodyString = row['body'] as String?;
      final body = bodyString != null
          ? jsonDecode(bodyString) as Map<String, dynamic>
          : null;
      
      return {
        'id': row['id'],
        'method': row['method'],
        'path': row['path'],
        'body': body,
        'created_at': row['created_at'],
      };
    }).toList();
  }
  
  /// إزالة عملية من قائمة انتظار وضع عدم الاتصال
  Future<void> removeOfflineOperation(String id) async {
    await _database.delete(
      'offline_operations',
      where: 'id = ?',
      whereArgs: [id],
    );
  }
  
  /// الحصول على حجم ذاكرة التخزين المؤقت
  Future<int> getSize() async {
    final result = await _database.rawQuery('SELECT COUNT(*) FROM cache');
    return Sqflite.firstIntValue(result) ?? 0;
  }
  
  /// الحصول على حجم قائمة انتظار وضع عدم الاتصال
  Future<int> getOfflineQueueSize() async {
    final result = await _database.rawQuery(
      'SELECT COUNT(*) FROM offline_operations',
    );
    return Sqflite.firstIntValue(result) ?? 0;
  }
  
  /// إغلاق مدير ذاكرة التخزين المؤقت
  Future<void> close() async {
    await _database.close();
  }
}
