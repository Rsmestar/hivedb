# HiveDB Flutter SDK

مكتبة Flutter للتفاعل مع خادم HiveDB - قاعدة بيانات آمنة وعالية الأداء مستوحاة من خلايا النحل.

## المميزات

- ✅ **مصادقة المستخدمين**: تسجيل الدخول، التسجيل، تحديث الملف الشخصي، وإدارة الجلسات
- ✅ **إدارة الخلايا**: إنشاء، قراءة، تحديث، وحذف الخلايا
- ✅ **إدارة البيانات**: تخزين واسترجاع البيانات مع دعم للاستعلامات المتقدمة
- ✅ **التخزين المؤقت**: تخزين البيانات محليًا لتحسين الأداء وتقليل استهلاك الشبكة
- ✅ **وضع عدم الاتصال**: استمرار العمل حتى عند انقطاع الاتصال بالإنترنت
- ✅ **دعم SGX**: عمليات آمنة باستخدام Intel SGX للتشفير والمعالجة الآمنة

## التثبيت

أضف `hivedb_flutter` إلى ملف `pubspec.yaml` الخاص بك:

```yaml
dependencies:
  hivedb_flutter: ^0.1.0
```

ثم قم بتنفيذ:

```bash
flutter pub get
```

## الاستخدام السريع

### التهيئة

```dart
import 'package:hivedb_flutter/hivedb_flutter.dart';

void main() async {
  // إنشاء وتهيئة مثيل HiveDB
  final hivedb = await createHiveDB(
    baseUrl: 'https://api.hivedb.io',
    enableSGX: true,
    enableLogging: true,
  );
  
  runApp(MyApp(hivedb: hivedb));
}
```

### المصادقة

```dart
// تسجيل مستخدم جديد
final user = await hivedb.auth.register(
  email: 'user@example.com',
  password: 'secure_password',
  fullName: 'John Doe',
);

// تسجيل الدخول
final loginResult = await hivedb.auth.login(
  email: 'user@example.com',
  password: 'secure_password',
);

// التحقق من حالة تسجيل الدخول
final isLoggedIn = await hivedb.isLoggedIn();

// تسجيل الخروج
await hivedb.auth.logout();
```

### إدارة الخلايا

```dart
// إنشاء خلية جديدة
final cell = await hivedb.cells.createCell(
  'my_cell',
  'cell_password',
);

// الحصول على جميع الخلايا
final cells = await hivedb.cells.getUserCells();

// مشاركة خلية مع مستخدم آخر
await hivedb.cells.shareCell(
  'my_cell',
  'friend@example.com',
  permissionLevel: 'editor',
);
```

### إدارة البيانات

```dart
// تخزين بيانات
await hivedb.data.storeData(
  'my_cell',
  'user_preferences',
  {'theme': 'dark', 'notifications': true},
);

// استرجاع بيانات
final data = await hivedb.data.getData('my_cell', 'user_preferences');

// الاستعلام عن البيانات
final query = QueryBuilder()
  .filter('age', 30)
  .greaterThan('score', 80)
  .sortDescending('created_at')
  .limit(10);

final results = await hivedb.data.query('my_cell', query);
```

### العمليات الآمنة (SGX)

```dart
// التحقق من توفر SGX
final sgxAvailable = await hivedb.isSGXAvailable();

// تشفير البيانات
final encrypted = await hivedb.secure.encryptData({
  'sensitive_data': 'confidential information',
});

// فك تشفير البيانات
final decrypted = await hivedb.secure.decryptData(encrypted['encrypted_data']);
```

## المزيد من الأمثلة

### التخزين المؤقت والوضع غير المتصل

```dart
// تعيين وضع عدم الاتصال
hivedb.setOfflineMode(true);

// مزامنة العمليات غير المتصلة
final syncResults = await hivedb.syncOfflineOperations();

// مسح ذاكرة التخزين المؤقت
await hivedb.clearCache();
```

### عمليات الدفعة

```dart
// تخزين مجموعة من البيانات
await hivedb.data.storeBatch(
  'my_cell',
  {
    'key1': 'value1',
    'key2': 'value2',
    'key3': 'value3',
  },
);

// استرجاع مجموعة من البيانات
final batchData = await hivedb.data.getBatch(
  'my_cell',
  ['key1', 'key2', 'key3'],
);
```

## المساهمة

نرحب بالمساهمات! يرجى مراجعة [إرشادات المساهمة](CONTRIBUTING.md) للحصول على مزيد من المعلومات.

## الترخيص

هذا المشروع مرخص بموجب [ترخيص MIT](LICENSE).
