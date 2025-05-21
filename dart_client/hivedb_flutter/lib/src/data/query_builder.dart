/// منشئ استعلامات لبناء استعلامات مرنة للبيانات
class QueryBuilder {
  /// مرشح الاستعلام
  final Map<String, dynamic> _filter = {};
  
  /// حقول الترتيب
  List<String>? _sort;
  
  /// حد النتائج
  int? _limit;
  
  /// إزاحة النتائج
  int? _offset;
  
  /// مصطلح البحث
  String? _search;
  
  /// حقول البحث
  List<String>? _searchFields;

  /// إضافة شرط مرشح
  QueryBuilder filter(String field, dynamic value) {
    _filter[field] = value;
    return this;
  }

  /// إضافة شرط مرشح للمساواة
  QueryBuilder equals(String field, dynamic value) {
    _filter[field] = value;
    return this;
  }

  /// إضافة شرط مرشح لعدم المساواة
  QueryBuilder notEquals(String field, dynamic value) {
    _filter[field] = {'\$ne': value};
    return this;
  }

  /// إضافة شرط مرشح للقيم الأكبر من
  QueryBuilder greaterThan(String field, dynamic value) {
    _filter[field] = {'\$gt': value};
    return this;
  }

  /// إضافة شرط مرشح للقيم الأكبر من أو تساوي
  QueryBuilder greaterThanOrEquals(String field, dynamic value) {
    _filter[field] = {'\$gte': value};
    return this;
  }

  /// إضافة شرط مرشح للقيم الأصغر من
  QueryBuilder lessThan(String field, dynamic value) {
    _filter[field] = {'\$lt': value};
    return this;
  }

  /// إضافة شرط مرشح للقيم الأصغر من أو تساوي
  QueryBuilder lessThanOrEquals(String field, dynamic value) {
    _filter[field] = {'\$lte': value};
    return this;
  }

  /// إضافة شرط مرشح للقيم في المصفوفة
  QueryBuilder inArray(String field, List<dynamic> values) {
    _filter[field] = {'\$in': values};
    return this;
  }

  /// إضافة شرط مرشح للقيم ليست في المصفوفة
  QueryBuilder notInArray(String field, List<dynamic> values) {
    _filter[field] = {'\$nin': values};
    return this;
  }

  /// إضافة شرط مرشح للقيم التي تحتوي على النص
  QueryBuilder contains(String field, String value) {
    _filter[field] = {'\$contains': value};
    return this;
  }

  /// إضافة شرط مرشح للقيم التي تبدأ بالنص
  QueryBuilder startsWith(String field, String value) {
    _filter[field] = {'\$startsWith': value};
    return this;
  }

  /// إضافة شرط مرشح للقيم التي تنتهي بالنص
  QueryBuilder endsWith(String field, String value) {
    _filter[field] = {'\$endsWith': value};
    return this;
  }

  /// إضافة شرط مرشح للقيم التي تطابق التعبير النمطي
  QueryBuilder matches(String field, String regex) {
    _filter[field] = {'\$regex': regex};
    return this;
  }

  /// إضافة شرط مرشح للقيم التي تقع بين قيمتين
  QueryBuilder between(String field, dynamic lower, dynamic upper) {
    _filter[field] = {'\$gte': lower, '\$lte': upper};
    return this;
  }

  /// إضافة شرط مرشح للقيم التي ليست فارغة
  QueryBuilder exists(String field) {
    _filter[field] = {'\$exists': true};
    return this;
  }

  /// إضافة شرط مرشح للقيم الفارغة
  QueryBuilder notExists(String field) {
    _filter[field] = {'\$exists': false};
    return this;
  }

  /// ترتيب النتائج حسب الحقول
  QueryBuilder sortBy(List<String> fields) {
    _sort = fields;
    return this;
  }

  /// ترتيب النتائج تصاعديًا حسب الحقل
  QueryBuilder sortAscending(String field) {
    _sort = [field];
    return this;
  }

  /// ترتيب النتائج تنازليًا حسب الحقل
  QueryBuilder sortDescending(String field) {
    _sort = ['-$field'];
    return this;
  }

  /// تحديد حد أقصى لعدد النتائج
  QueryBuilder limit(int count) {
    _limit = count;
    return this;
  }

  /// تحديد إزاحة للنتائج (للصفحات)
  QueryBuilder offset(int count) {
    _offset = count;
    return this;
  }

  /// إضافة مصطلح بحث
  QueryBuilder search(String term, {List<String>? fields}) {
    _search = term;
    _searchFields = fields;
    return this;
  }

  /// بناء استعلام JSON
  Map<String, dynamic> build() {
    final query = <String, dynamic>{};
    
    if (_filter.isNotEmpty) {
      query['filter'] = _filter;
    }
    
    if (_sort != null && _sort!.isNotEmpty) {
      query['sort'] = _sort;
    }
    
    if (_limit != null) {
      query['limit'] = _limit;
    }
    
    if (_offset != null) {
      query['offset'] = _offset;
    }
    
    if (_search != null && _search!.isNotEmpty) {
      query['search'] = _search;
      
      if (_searchFields != null && _searchFields!.isNotEmpty) {
        query['search_fields'] = _searchFields;
      }
    }
    
    return query;
  }
  
  /// إعادة تعيين الاستعلام
  void reset() {
    _filter.clear();
    _sort = null;
    _limit = null;
    _offset = null;
    _search = null;
    _searchFields = null;
  }
  
  @override
  String toString() {
    return build().toString();
  }
}
