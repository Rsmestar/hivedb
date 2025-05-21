import 'package:logging/logging.dart';

/// تكوين مكتبة HiveDB
class HiveDBConfig {
  /// عنوان URL الأساسي لخادم HiveDB
  final String baseUrl;
  
  /// تمكين دعم Intel SGX للعمليات الآمنة
  final bool enableSGX;
  
  /// مهلة الاتصال بالخادم
  final Duration timeout;
  
  /// تمكين تسجيل الأحداث للتصحيح
  final bool enableLogging;
  
  /// مستوى تسجيل الأحداث
  final Level logLevel;
  
  /// دليل التخزين المؤقت المحلي
  final String? cacheDirectory;
  
  /// حجم ذاكرة التخزين المؤقت (عدد العناصر)
  final int cacheSize;
  
  /// مدة صلاحية عناصر التخزين المؤقت
  final Duration cacheTTL;
  
  /// تمكين وضع عدم الاتصال
  final bool offlineMode;
  
  /// تمكين المزامنة التلقائية عند استعادة الاتصال
  final bool autoSync;

  /// إنشاء تكوين جديد لـ HiveDB
  HiveDBConfig({
    required this.baseUrl,
    this.enableSGX = true,
    this.timeout = const Duration(seconds: 30),
    this.enableLogging = false,
    this.logLevel = Level.INFO,
    this.cacheDirectory,
    this.cacheSize = 1000,
    this.cacheTTL = const Duration(hours: 1),
    this.offlineMode = false,
    this.autoSync = true,
  });
  
  /// إنشاء نسخة جديدة من التكوين مع تحديث بعض القيم
  HiveDBConfig copyWith({
    String? baseUrl,
    bool? enableSGX,
    Duration? timeout,
    bool? enableLogging,
    Level? logLevel,
    String? cacheDirectory,
    int? cacheSize,
    Duration? cacheTTL,
    bool? offlineMode,
    bool? autoSync,
  }) {
    return HiveDBConfig(
      baseUrl: baseUrl ?? this.baseUrl,
      enableSGX: enableSGX ?? this.enableSGX,
      timeout: timeout ?? this.timeout,
      enableLogging: enableLogging ?? this.enableLogging,
      logLevel: logLevel ?? this.logLevel,
      cacheDirectory: cacheDirectory ?? this.cacheDirectory,
      cacheSize: cacheSize ?? this.cacheSize,
      cacheTTL: cacheTTL ?? this.cacheTTL,
      offlineMode: offlineMode ?? this.offlineMode,
      autoSync: autoSync ?? this.autoSync,
    );
  }
}
