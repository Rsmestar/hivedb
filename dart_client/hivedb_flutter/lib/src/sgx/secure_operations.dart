import '../http_client.dart';
import '../exceptions.dart';

/// خدمة العمليات الآمنة باستخدام Intel SGX
class SecureOperations {
  /// عميل HTTP
  final HiveDBHttpClient _client;

  /// إنشاء خدمة عمليات آمنة جديدة
  SecureOperations(this._client);

  /// تشفير البيانات باستخدام SGX
  Future<Map<String, dynamic>> encryptData(
    Map<String, dynamic> data, {
    String? dataId,
  }) async {
    try {
      final response = await _client.post('/api/secure/encrypt', body: {
        'data': data,
        if (dataId != null) 'data_id': dataId,
      });
      
      return response;
    } catch (e) {
      if (e is ApiException && e.statusCode == 503) {
        throw SGXNotAvailableException('خدمة التشفير الآمن غير متاحة حاليًا');
      }
      throw SGXException('فشل تشفير البيانات: $e');
    }
  }

  /// فك تشفير البيانات باستخدام SGX
  Future<Map<String, dynamic>> decryptData(String encryptedData) async {
    try {
      final response = await _client.post('/api/secure/decrypt', body: {
        'encrypted_data': encryptedData,
      });
      
      return response;
    } catch (e) {
      if (e is ApiException && e.statusCode == 503) {
        throw SGXNotAvailableException('خدمة التشفير الآمن غير متاحة حاليًا');
      }
      throw SGXException('فشل فك تشفير البيانات: $e');
    }
  }

  /// إجراء عملية آمنة على البيانات المشفرة
  Future<Map<String, dynamic>> secureCompute(
    String operation,
    Map<String, String> encryptedData,
    Map<String, dynamic> params,
  ) async {
    try {
      final response = await _client.post('/api/secure/compute', body: {
        'operation': operation,
        'encrypted_data': encryptedData,
        'params': params,
      });
      
      return response;
    } catch (e) {
      if (e is ApiException) {
        if (e.statusCode == 503) {
          throw SGXNotAvailableException('خدمة التشفير الآمن غير متاحة حاليًا');
        } else if (e.statusCode == 400) {
          throw SGXException('عملية غير مدعومة: $operation');
        }
      }
      throw SGXException('فشل إجراء العملية الآمنة: $e');
    }
  }

  /// التحقق من سلامة البيانات باستخدام SGX
  Future<Map<String, dynamic>> verifyData(
    Map<String, dynamic> data,
    String hashValue,
  ) async {
    try {
      final response = await _client.post('/api/secure/verify', body: {
        'data': data,
        'hash_value': hashValue,
      });
      
      return response;
    } catch (e) {
      if (e is ApiException && e.statusCode == 503) {
        throw SGXNotAvailableException('خدمة التشفير الآمن غير متاحة حاليًا');
      }
      throw SGXException('فشل التحقق من البيانات: $e');
    }
  }

  /// إنشاء تجزئة آمنة للبيانات
  Future<String> secureHash(Map<String, dynamic> data) async {
    try {
      final response = await _client.post('/api/secure/hash', body: {
        'data': data,
      });
      
      return response['hash'];
    } catch (e) {
      if (e is ApiException && e.statusCode == 503) {
        throw SGXNotAvailableException('خدمة التشفير الآمن غير متاحة حاليًا');
      }
      throw SGXException('فشل إنشاء تجزئة آمنة: $e');
    }
  }

  /// إجراء التحقق عن بعد من بيئة SGX
  Future<Map<String, dynamic>> remoteAttestation() async {
    try {
      final response = await _client.get('/api/secure/attestation');
      
      return response;
    } catch (e) {
      if (e is ApiException && e.statusCode == 503) {
        throw SGXNotAvailableException('خدمة التشفير الآمن غير متاحة حاليًا');
      }
      throw SGXException('فشل إجراء التحقق عن بعد: $e');
    }
  }
  
  /// البحث في البيانات المشفرة
  Future<Map<String, dynamic>> searchEncrypted(
    String encryptedData,
    String query,
  ) async {
    try {
      final response = await _client.post('/api/secure/compute', body: {
        'operation': 'search',
        'encrypted_data': {'value': encryptedData},
        'params': {'query': query},
      });
      
      return response;
    } catch (e) {
      if (e is ApiException && e.statusCode == 503) {
        throw SGXNotAvailableException('خدمة التشفير الآمن غير متاحة حاليًا');
      }
      throw SGXException('فشل البحث في البيانات المشفرة: $e');
    }
  }
  
  /// تجميع البيانات المشفرة
  Future<Map<String, dynamic>> aggregateEncrypted(
    List<String> encryptedData,
    String operation,
  ) async {
    try {
      final response = await _client.post('/api/secure/compute', body: {
        'operation': 'aggregate',
        'encrypted_data': {'values': encryptedData},
        'params': {'aggregation': operation},
      });
      
      return response;
    } catch (e) {
      if (e is ApiException && e.statusCode == 503) {
        throw SGXNotAvailableException('خدمة التشفير الآمن غير متاحة حاليًا');
      }
      throw SGXException('فشل تجميع البيانات المشفرة: $e');
    }
  }
  
  /// تصفية البيانات المشفرة
  Future<Map<String, dynamic>> filterEncrypted(
    List<String> encryptedData,
    Map<String, dynamic> criteria,
  ) async {
    try {
      final response = await _client.post('/api/secure/compute', body: {
        'operation': 'filter',
        'encrypted_data': {'values': encryptedData},
        'params': {'criteria': criteria},
      });
      
      return response;
    } catch (e) {
      if (e is ApiException && e.statusCode == 503) {
        throw SGXNotAvailableException('خدمة التشفير الآمن غير متاحة حاليًا');
      }
      throw SGXException('فشل تصفية البيانات المشفرة: $e');
    }
  }
  
  /// التحقق من حالة SGX
  Future<bool> isSGXAvailable() async {
    try {
      final response = await _client.get('/api/secure/status');
      
      return response['sgx_enabled'] == true;
    } catch (e) {
      return false;
    }
  }
}
