import 'dart:convert';
import 'dart:io';
import 'dart:async';
import 'package:dio/dio.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:logging/logging.dart';
import 'package:retry/retry.dart';

import 'config.dart';
import 'exceptions.dart';
import 'auth/token_manager.dart';
import 'cache/cache_manager.dart';

/// عميل HTTP لإجراء طلبات إلى خادم HiveDB
class HiveDBHttpClient {
  /// تكوين HiveDB
  final HiveDBConfig config;
  
  /// مدير الرموز المميزة
  final TokenManager tokenManager;
  
  /// مدير ذاكرة التخزين المؤقت
  final CacheManager cacheManager;
  
  /// عميل Dio للطلبات HTTP
  late final Dio _dio;
  
  /// مسجل الأحداث
  late final Logger _logger;
  
  /// إنشاء عميل HTTP جديد
  HiveDBHttpClient(this.config, this.tokenManager, this.cacheManager) {
    _initDio();
    _initLogger();
  }
  
  /// تهيئة عميل Dio
  void _initDio() {
    _dio = Dio(BaseOptions(
      baseUrl: config.baseUrl,
      connectTimeout: config.timeout,
      receiveTimeout: config.timeout,
      contentType: 'application/json',
      responseType: ResponseType.json,
    ));
    
    // إضافة معترض لإضافة رأس التفويض
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await tokenManager.getToken();
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        
        // إضافة رأس SGX إذا كان ممكنًا
        if (config.enableSGX) {
          options.headers['X-SGX-Enabled'] = 'true';
        }
        
        return handler.next(options);
      },
      onError: (DioException error, handler) async {
        if (error.response?.statusCode == 401) {
          // محاولة تحديث الرمز المميز
          try {
            final refreshToken = await tokenManager.getRefreshToken();
            if (refreshToken != null) {
              final response = await _dio.post('/token/refresh', data: {
                'refresh_token': refreshToken,
              });
              
              if (response.statusCode == 200 && response.data != null) {
                final newToken = response.data['access_token'];
                await tokenManager.saveToken(
                  newToken, 
                  refreshToken: response.data['refresh_token'],
                );
                
                // إعادة المحاولة مع الرمز المميز الجديد
                final options = error.requestOptions;
                options.headers['Authorization'] = 'Bearer $newToken';
                
                final retryResponse = await _dio.fetch(options);
                return handler.resolve(retryResponse);
              }
            }
          } catch (e) {
            // فشل تحديث الرمز المميز، مسح الرموز المميزة
            await tokenManager.clearToken();
          }
        }
        
        return handler.next(error);
      },
    ));
    
    // إضافة معترض للتسجيل
    if (config.enableLogging) {
      _dio.interceptors.add(LogInterceptor(
        requestBody: true,
        responseBody: true,
      ));
    }
  }
  
  /// تهيئة مسجل الأحداث
  void _initLogger() {
    _logger = Logger('HiveDBHttpClient');
    if (config.enableLogging) {
      Logger.root.level = config.logLevel;
      Logger.root.onRecord.listen((record) {
        // ignore: avoid_print
        print('${record.level.name}: ${record.time}: ${record.message}');
      });
    }
  }
  
  /// التحقق من حالة الاتصال
  Future<bool> checkConnectivity() async {
    if (config.offlineMode) {
      return false;
    }
    
    final connectivityResult = await Connectivity().checkConnectivity();
    return connectivityResult != ConnectivityResult.none;
  }
  
  /// إجراء طلب GET
  Future<Map<String, dynamic>> get(
    String path, {
    Map<String, dynamic>? queryParams,
    bool useCache = true,
    Duration? cacheDuration,
  }) async {
    final cacheKey = '${path}?${queryParams?.toString() ?? ''}';
    
    // التحقق من ذاكرة التخزين المؤقت أولاً إذا كان مسموحًا
    if (useCache) {
      final cachedData = await cacheManager.get(cacheKey);
      if (cachedData != null) {
        _logger.fine('Cache hit for $path');
        return cachedData;
      }
    }
    
    // التحقق من الاتصال
    final isConnected = await checkConnectivity();
    if (!isConnected) {
      if (config.offlineMode) {
        _logger.warning('Working in offline mode for $path');
        // محاولة الحصول على البيانات من ذاكرة التخزين المؤقت حتى لو كان useCache = false
        final cachedData = await cacheManager.get(cacheKey);
        if (cachedData != null) {
          return cachedData;
        }
        throw OfflineModeException('لا يمكن الوصول إلى الخادم في وضع عدم الاتصال ولا توجد بيانات مخزنة مؤقتًا');
      } else {
        throw ConnectionException('لا يوجد اتصال بالإنترنت');
      }
    }
    
    try {
      // استخدام إعادة المحاولة للتعامل مع فشل الشبكة المؤقت
      final response = await retry(
        () => _dio.get(path, queryParameters: queryParams),
        retryIf: (e) => e is SocketException || e is TimeoutException,
        maxAttempts: 3,
      );
      
      final data = response.data as Map<String, dynamic>;
      
      // تخزين البيانات في ذاكرة التخزين المؤقت إذا كان مسموحًا
      if (useCache) {
        await cacheManager.set(cacheKey, data, duration: cacheDuration);
      }
      
      return data;
    } on DioException catch (e) {
      throw _handleDioException(e, path);
    } catch (e) {
      throw ConnectionException('خطأ في الاتصال: $e');
    }
  }
  
  /// إجراء طلب POST
  Future<Map<String, dynamic>> post(
    String path, {
    Map<String, dynamic>? body,
    bool invalidateCache = true,
    List<String>? invalidateCachePatterns,
  }) async {
    // التحقق من الاتصال
    final isConnected = await checkConnectivity();
    if (!isConnected) {
      if (config.offlineMode) {
        _logger.warning('Queuing offline operation: POST $path');
        // تخزين العملية للتنفيذ لاحقًا عند استعادة الاتصال
        await cacheManager.queueOfflineOperation('POST', path, body);
        return {'status': 'queued', 'message': 'العملية في قائمة الانتظار لوضع عدم الاتصال'};
      } else {
        throw ConnectionException('لا يوجد اتصال بالإنترنت');
      }
    }
    
    try {
      final response = await retry(
        () => _dio.post(path, data: body),
        retryIf: (e) => e is SocketException || e is TimeoutException,
        maxAttempts: 3,
      );
      
      final data = response.data as Map<String, dynamic>;
      
      // إبطال ذاكرة التخزين المؤقت إذا كان مطلوبًا
      if (invalidateCache) {
        if (invalidateCachePatterns != null && invalidateCachePatterns.isNotEmpty) {
          for (final pattern in invalidateCachePatterns) {
            await cacheManager.invalidatePattern(pattern);
          }
        } else {
          // إبطال أي ذاكرة تخزين مؤقت تبدأ بنفس المسار
          await cacheManager.invalidatePattern(path);
        }
      }
      
      return data;
    } on DioException catch (e) {
      throw _handleDioException(e, path);
    } catch (e) {
      throw ConnectionException('خطأ في الاتصال: $e');
    }
  }
  
  /// إجراء طلب PUT
  Future<Map<String, dynamic>> put(
    String path, {
    Map<String, dynamic>? body,
    bool invalidateCache = true,
    List<String>? invalidateCachePatterns,
  }) async {
    // التحقق من الاتصال
    final isConnected = await checkConnectivity();
    if (!isConnected) {
      if (config.offlineMode) {
        _logger.warning('Queuing offline operation: PUT $path');
        // تخزين العملية للتنفيذ لاحقًا عند استعادة الاتصال
        await cacheManager.queueOfflineOperation('PUT', path, body);
        return {'status': 'queued', 'message': 'العملية في قائمة الانتظار لوضع عدم الاتصال'};
      } else {
        throw ConnectionException('لا يوجد اتصال بالإنترنت');
      }
    }
    
    try {
      final response = await retry(
        () => _dio.put(path, data: body),
        retryIf: (e) => e is SocketException || e is TimeoutException,
        maxAttempts: 3,
      );
      
      final data = response.data as Map<String, dynamic>;
      
      // إبطال ذاكرة التخزين المؤقت إذا كان مطلوبًا
      if (invalidateCache) {
        if (invalidateCachePatterns != null && invalidateCachePatterns.isNotEmpty) {
          for (final pattern in invalidateCachePatterns) {
            await cacheManager.invalidatePattern(pattern);
          }
        } else {
          // إبطال أي ذاكرة تخزين مؤقت تبدأ بنفس المسار
          await cacheManager.invalidatePattern(path);
        }
      }
      
      return data;
    } on DioException catch (e) {
      throw _handleDioException(e, path);
    } catch (e) {
      throw ConnectionException('خطأ في الاتصال: $e');
    }
  }
  
  /// إجراء طلب DELETE
  Future<Map<String, dynamic>> delete(
    String path, {
    bool invalidateCache = true,
    List<String>? invalidateCachePatterns,
  }) async {
    // التحقق من الاتصال
    final isConnected = await checkConnectivity();
    if (!isConnected) {
      if (config.offlineMode) {
        _logger.warning('Queuing offline operation: DELETE $path');
        // تخزين العملية للتنفيذ لاحقًا عند استعادة الاتصال
        await cacheManager.queueOfflineOperation('DELETE', path, null);
        return {'status': 'queued', 'message': 'العملية في قائمة الانتظار لوضع عدم الاتصال'};
      } else {
        throw ConnectionException('لا يوجد اتصال بالإنترنت');
      }
    }
    
    try {
      final response = await retry(
        () => _dio.delete(path),
        retryIf: (e) => e is SocketException || e is TimeoutException,
        maxAttempts: 3,
      );
      
      final data = response.data as Map<String, dynamic>;
      
      // إبطال ذاكرة التخزين المؤقت إذا كان مطلوبًا
      if (invalidateCache) {
        if (invalidateCachePatterns != null && invalidateCachePatterns.isNotEmpty) {
          for (final pattern in invalidateCachePatterns) {
            await cacheManager.invalidatePattern(pattern);
          }
        } else {
          // إبطال أي ذاكرة تخزين مؤقت تبدأ بنفس المسار
          await cacheManager.invalidatePattern(path);
        }
      }
      
      return data;
    } on DioException catch (e) {
      throw _handleDioException(e, path);
    } catch (e) {
      throw ConnectionException('خطأ في الاتصال: $e');
    }
  }
  
  /// التعامل مع استثناءات Dio
  Exception _handleDioException(DioException e, String path) {
    _logger.warning('DioException for $path: ${e.message}');
    
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return ConnectionException('انتهت مهلة الاتصال: ${e.message}');
      
      case DioExceptionType.badResponse:
        final statusCode = e.response?.statusCode ?? 0;
        final responseData = e.response?.data;
        String message = 'خطأ في الاستجابة';
        
        if (responseData is Map<String, dynamic> && responseData.containsKey('detail')) {
          message = responseData['detail'].toString();
        } else if (responseData is String) {
          message = responseData;
        }
        
        switch (statusCode) {
          case 401:
            return UnauthorizedException(message);
          case 403:
            return ForbiddenException(message);
          case 404:
            return ApiException(statusCode: statusCode, message: 'غير موجود: $message');
          default:
            return ApiException(statusCode: statusCode, message: message);
        }
      
      case DioExceptionType.cancel:
        return ConnectionException('تم إلغاء الطلب');
      
      default:
        return ConnectionException('خطأ في الاتصال: ${e.message}');
    }
  }
  
  /// مزامنة العمليات غير المتصلة
  Future<List<Map<String, dynamic>>> syncOfflineOperations() async {
    final isConnected = await checkConnectivity();
    if (!isConnected) {
      throw ConnectionException('لا يمكن المزامنة بدون اتصال بالإنترنت');
    }
    
    final operations = await cacheManager.getOfflineOperations();
    final results = <Map<String, dynamic>>[];
    
    for (final operation in operations) {
      try {
        final method = operation['method'] as String;
        final path = operation['path'] as String;
        final body = operation['body'] as Map<String, dynamic>?;
        
        Map<String, dynamic> result;
        
        switch (method) {
          case 'POST':
            result = await post(path, body: body, invalidateCache: false);
            break;
          case 'PUT':
            result = await put(path, body: body, invalidateCache: false);
            break;
          case 'DELETE':
            result = await delete(path, invalidateCache: false);
            break;
          default:
            throw HiveDBException('طريقة غير مدعومة: $method');
        }
        
        results.add({
          'operation': operation,
          'result': result,
          'success': true,
        });
        
        // إزالة العملية من قائمة الانتظار
        await cacheManager.removeOfflineOperation(operation['id'] as String);
      } catch (e) {
        results.add({
          'operation': operation,
          'error': e.toString(),
          'success': false,
        });
      }
    }
    
    return results;
  }
  
  /// إجراء طلب PATCH
  Future<Map<String, dynamic>> patch(
    String path, {
    Map<String, dynamic>? body,
    bool invalidateCache = true,
    List<String>? invalidateCachePatterns,
  }) async {
    try {
      final isConnected = await checkConnectivity();
      
      if (!isConnected && config.offlineMode) {
        // تخزين العملية للتنفيذ لاحقًا
        final operationId = await cacheManager.queueOfflineOperation('PATCH', path, body);
        
        return {
          'status': 'queued',
          'operation_id': operationId,
          'message': 'تم حفظ العملية للتنفيذ عند استعادة الاتصال',
        };
      } else if (!isConnected) {
        throw ConnectionException('لا يوجد اتصال بالإنترنت');
      }
      
      final response = await retry(
        () => _dio.patch(
          path,
          data: body != null ? jsonEncode(body) : null,
        ),
        retryIf: (e) => e is DioException && e.type != DioExceptionType.cancel,
        maxAttempts: 3,
      );
      
      final data = response.data as Map<String, dynamic>;
      
      // إبطال ذاكرة التخزين المؤقت إذا كان مطلوبًا
      if (invalidateCache) {
        if (invalidateCachePatterns != null && invalidateCachePatterns.isNotEmpty) {
          for (final pattern in invalidateCachePatterns) {
            await cacheManager.invalidatePattern(pattern);
          }
        } else {
          // إبطال أي ذاكرة تخزين مؤقت تبدأ بنفس المسار
          await cacheManager.invalidatePattern(path);
        }
      }
      
      return data;
    } on DioException catch (e) {
      throw _handleDioException(e, path);
    } on TimeoutException catch (e) {
      throw ConnectionException('انتهت مهلة الاتصال: $e');
    } catch (e) {
      throw ConnectionException('خطأ في الاتصال: $e');
    }
  }

  /// إغلاق العميل
  void close() {
    _dio.close();
  }
}
