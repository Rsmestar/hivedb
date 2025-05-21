import '../http_client.dart';
import '../exceptions.dart';
import '../cell/models.dart';
import 'query_builder.dart';

/// خدمة البيانات للتعامل مع عمليات البيانات في الخلايا
class DataService {
  /// عميل HTTP
  final HiveDBHttpClient _client;

  /// إنشاء خدمة بيانات جديدة
  DataService(this._client);

  /// الحصول على بيانات من خلية
  Future<CellDataItem> getData(String cellKey, String dataKey, {bool useCache = true}) async {
    try {
      final response = await _client.get(
        '/cells/$cellKey/data/$dataKey',
        useCache: useCache,
      );
      
      return CellDataItem(
        key: response['key'],
        value: response['value'],
      );
    } catch (e) {
      if (e is ApiException) {
        if (e.statusCode == 404) {
          throw HiveDBException('البيانات غير موجودة: $dataKey');
        } else if (e.statusCode == 403) {
          throw HiveDBException('ليس لديك إذن للوصول إلى هذه البيانات');
        }
      }
      rethrow;
    }
  }

  /// تخزين بيانات في خلية
  Future<Map<String, dynamic>> storeData(
    String cellKey,
    String dataKey,
    dynamic value, {
    bool encrypt = false,
  }) async {
    try {
      final response = await _client.post(
        '/cells/$cellKey/data',
        body: {
          'key': dataKey,
          'value': value is String ? value : value.toString(),
          'encrypt': encrypt,
        },
        invalidateCachePatterns: ['/cells/$cellKey/data', '/cells/$cellKey/keys'],
      );
      
      return response;
    } catch (e) {
      if (e is ApiException) {
        if (e.statusCode == 404) {
          throw HiveDBException('الخلية غير موجودة: $cellKey');
        } else if (e.statusCode == 403) {
          throw HiveDBException('ليس لديك إذن للكتابة في هذه الخلية');
        }
      }
      rethrow;
    }
  }

  /// حذف بيانات من خلية
  Future<Map<String, dynamic>> deleteData(String cellKey, String dataKey) async {
    try {
      final response = await _client.delete(
        '/cells/$cellKey/data/$dataKey',
        invalidateCachePatterns: ['/cells/$cellKey/data', '/cells/$cellKey/keys'],
      );
      
      return response;
    } catch (e) {
      if (e is ApiException) {
        if (e.statusCode == 404) {
          throw HiveDBException('البيانات أو الخلية غير موجودة');
        } else if (e.statusCode == 403) {
          throw HiveDBException('ليس لديك إذن للحذف من هذه الخلية');
        }
      }
      rethrow;
    }
  }

  /// الحصول على مفاتيح البيانات في خلية
  Future<List<String>> getKeys(String cellKey, {bool useCache = true}) async {
    try {
      final response = await _client.get(
        '/cells/$cellKey/keys',
        useCache: useCache,
      );
      
      return List<String>.from(response['keys']);
    } catch (e) {
      if (e is ApiException) {
        if (e.statusCode == 404) {
          throw HiveDBException('الخلية غير موجودة: $cellKey');
        } else if (e.statusCode == 403) {
          throw HiveDBException('ليس لديك إذن للوصول إلى هذه الخلية');
        }
      }
      rethrow;
    }
  }

  /// استعلام البيانات في خلية
  Future<CellQueryResponse> query(
    String cellKey,
    QueryBuilder query, {
    bool useCache = true,
  }) async {
    try {
      final response = await _client.post(
        '/cells/$cellKey/query',
        body: query.build(),
      );
      
      return CellQueryResponse.fromJson(response);
    } catch (e) {
      if (e is ApiException) {
        if (e.statusCode == 404) {
          throw HiveDBException('الخلية غير موجودة: $cellKey');
        } else if (e.statusCode == 403) {
          throw HiveDBException('ليس لديك إذن للوصول إلى هذه الخلية');
        } else if (e.statusCode == 400) {
          throw HiveDBException('استعلام غير صالح: ${e.message}');
        }
      }
      rethrow;
    }
  }
  
  /// تخزين مجموعة من البيانات في خلية (عملية جماعية)
  Future<Map<String, dynamic>> storeBatch(
    String cellKey,
    Map<String, dynamic> data, {
    bool encrypt = false,
  }) async {
    try {
      final response = await _client.post(
        '/cells/$cellKey/data/batch',
        body: {
          'data': data,
          'encrypt': encrypt,
        },
        invalidateCachePatterns: ['/cells/$cellKey/data', '/cells/$cellKey/keys'],
      );
      
      return response;
    } catch (e) {
      if (e is ApiException) {
        if (e.statusCode == 404) {
          throw HiveDBException('الخلية غير موجودة: $cellKey');
        } else if (e.statusCode == 403) {
          throw HiveDBException('ليس لديك إذن للكتابة في هذه الخلية');
        }
      }
      rethrow;
    }
  }
  
  /// حذف مجموعة من البيانات من خلية (عملية جماعية)
  Future<Map<String, dynamic>> deleteBatch(
    String cellKey,
    List<String> keys,
  ) async {
    try {
      final response = await _client.post(
        '/cells/$cellKey/data/batch/delete',
        body: {
          'keys': keys,
        },
        invalidateCachePatterns: ['/cells/$cellKey/data', '/cells/$cellKey/keys'],
      );
      
      return response;
    } catch (e) {
      if (e is ApiException) {
        if (e.statusCode == 404) {
          throw HiveDBException('الخلية غير موجودة: $cellKey');
        } else if (e.statusCode == 403) {
          throw HiveDBException('ليس لديك إذن للحذف من هذه الخلية');
        }
      }
      rethrow;
    }
  }
  
  /// الحصول على مجموعة من البيانات من خلية (عملية جماعية)
  Future<Map<String, dynamic>> getBatch(
    String cellKey,
    List<String> keys, {
    bool useCache = true,
  }) async {
    try {
      final response = await _client.post(
        '/cells/$cellKey/data/batch/get',
        body: {
          'keys': keys,
        },
      );
      
      return response;
    } catch (e) {
      if (e is ApiException) {
        if (e.statusCode == 404) {
          throw HiveDBException('الخلية غير موجودة: $cellKey');
        } else if (e.statusCode == 403) {
          throw HiveDBException('ليس لديك إذن للوصول إلى هذه الخلية');
        }
      }
      rethrow;
    }
  }
  
  /// تحديث جزئي للبيانات في خلية
  Future<Map<String, dynamic>> updatePartial(
    String cellKey,
    String dataKey,
    Map<String, dynamic> updates,
  ) async {
    try {
      final response = await _client.patch(
        '/cells/$cellKey/data/$dataKey',
        body: updates,
        invalidateCachePatterns: ['/cells/$cellKey/data/$dataKey'],
      );
      
      return response;
    } catch (e) {
      if (e is ApiException) {
        if (e.statusCode == 404) {
          throw HiveDBException('البيانات أو الخلية غير موجودة');
        } else if (e.statusCode == 403) {
          throw HiveDBException('ليس لديك إذن للتحديث في هذه الخلية');
        }
      }
      rethrow;
    }
  }
}
