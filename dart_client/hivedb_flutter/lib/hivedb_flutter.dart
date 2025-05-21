library hivedb_flutter;

// تصدير الفئات الرئيسية
export 'src/config.dart';
export 'src/exceptions.dart';

// تصدير نماذج المصادقة
export 'src/auth/models.dart';

// تصدير نماذج الخلايا
export 'src/cell/models.dart';

// تصدير منشئ الاستعلامات
export 'src/data/query_builder.dart';

// استيراد الخدمات الداخلية
import 'src/config.dart';
import 'src/http_client.dart';
import 'src/cache/cache_manager.dart';
import 'src/auth/token_manager.dart';
import 'src/auth/auth_service.dart';
import 'src/cell/cell_service.dart';
import 'src/data/data_service.dart';
import 'src/sgx/secure_operations.dart';

/// الفئة الرئيسية لمكتبة HiveDB Flutter
class HiveDB {
  /// تكوين HiveDB
  late final HiveDBConfig _config;
  
  /// مدير الرموز المميزة
  late final TokenManager _tokenManager;
  
  /// مدير ذاكرة التخزين المؤقت
  late final CacheManager _cacheManager;
  
  /// عميل HTTP
  late final HiveDBHttpClient _httpClient;
  
  /// خدمة المصادقة
  late final AuthService auth;
  
  /// خدمة الخلايا
  late final CellService cells;
  
  /// خدمة البيانات
  late final DataService data;
  
  /// خدمة العمليات الآمنة
  late final SecureOperations secure;
  
  /// ما إذا كانت المكتبة مهيأة
  bool _initialized = false;

  /// إنشاء مثيل جديد من HiveDB
  HiveDB({
    required String baseUrl,
    bool enableSGX = true,
    Duration timeout = const Duration(seconds: 30),
    bool enableLogging = false,
    String? cacheDirectory,
    int cacheSize = 1000,
    Duration cacheTTL = const Duration(hours: 1),
    bool offlineMode = false,
    bool autoSync = true,
  }) {
    _config = HiveDBConfig(
      baseUrl: baseUrl,
      enableSGX: enableSGX,
      timeout: timeout,
      enableLogging: enableLogging,
      cacheDirectory: cacheDirectory,
      cacheSize: cacheSize,
      cacheTTL: cacheTTL,
      offlineMode: offlineMode,
      autoSync: autoSync,
    );
  }
  
  /// تهيئة المكتبة
  Future<void> initialize() async {
    if (_initialized) return;
    
    _tokenManager = TokenManager();
    _cacheManager = CacheManager(_config);
    await _cacheManager.initialize();
    
    _httpClient = HiveDBHttpClient(_config, _tokenManager, _cacheManager);
    
    auth = AuthService(_httpClient, _tokenManager);
    cells = CellService(_httpClient);
    data = DataService(_httpClient);
    secure = SecureOperations(_httpClient);
    
    _initialized = true;
  }
  
  /// التحقق مما إذا كان المستخدم مسجل الدخول
  Future<bool> isLoggedIn() async {
    _checkInitialized();
    return await _tokenManager.isTokenValid();
  }
  
  /// مزامنة العمليات غير المتصلة
  Future<List<Map<String, dynamic>>> syncOfflineOperations() async {
    _checkInitialized();
    return await _httpClient.syncOfflineOperations();
  }
  
  /// الحصول على حجم ذاكرة التخزين المؤقت
  Future<int> getCacheSize() async {
    _checkInitialized();
    return await _cacheManager.getSize();
  }
  
  /// مسح ذاكرة التخزين المؤقت
  Future<void> clearCache() async {
    _checkInitialized();
    await _cacheManager.clear();
  }
  
  /// التحقق مما إذا كان SGX متاحًا
  Future<bool> isSGXAvailable() async {
    _checkInitialized();
    return await secure.isSGXAvailable();
  }
  
  /// التحقق من حالة الاتصال
  Future<bool> isOnline() async {
    return await _httpClient.checkConnectivity();
  }
  
  /// تغيير وضع عدم الاتصال
  void setOfflineMode(bool enabled) {
    _config = _config.copyWith(offlineMode: enabled);
  }
  
  /// إغلاق المكتبة وتنظيف الموارد
  Future<void> close() async {
    if (!_initialized) return;
    
    _httpClient.close();
    await _cacheManager.close();
    
    _initialized = false;
  }
  
  /// التحقق مما إذا كانت المكتبة مهيأة
  void _checkInitialized() {
    if (!_initialized) {
      throw Exception('يجب تهيئة HiveDB قبل استخدامها. استدعِ initialize() أولاً.');
    }
  }
}

/// إنشاء مثيل HiveDB وتهيئته
Future<HiveDB> createHiveDB({
  required String baseUrl,
  bool enableSGX = true,
  Duration timeout = const Duration(seconds: 30),
  bool enableLogging = false,
  String? cacheDirectory,
  int cacheSize = 1000,
  Duration cacheTTL = const Duration(hours: 1),
  bool offlineMode = false,
  bool autoSync = true,
}) async {
  final hivedb = HiveDB(
    baseUrl: baseUrl,
    enableSGX: enableSGX,
    timeout: timeout,
    enableLogging: enableLogging,
    cacheDirectory: cacheDirectory,
    cacheSize: cacheSize,
    cacheTTL: cacheTTL,
    offlineMode: offlineMode,
    autoSync: autoSync,
  );
  
  await hivedb.initialize();
  return hivedb;
}
