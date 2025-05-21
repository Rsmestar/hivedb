# أمثلة متقدمة لاستخدام HiveDB

هذا الملف يحتوي على أمثلة متقدمة لاستخدام HiveDB مع المكونات الإضافية مثل PostgreSQL وRedis وKafka.

## استخدام HiveDB مع PostgreSQL

### الاتصال بقاعدة البيانات مباشرة

```python
import psycopg2
from hivedb import config

# الحصول على معلومات الاتصال من تكوين HiveDB
conn_string = config.get_database_url()

# الاتصال بقاعدة البيانات
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

# استعلام عن المستخدمين
cursor.execute("SELECT id, email, created_at FROM users")
users = cursor.fetchall()

for user in users:
    print(f"المستخدم: {user[1]}, تاريخ الإنشاء: {user[2]}")

conn.close()
```

### استخدام SQLAlchemy مع HiveDB

```python
from sqlalchemy import create_engine, text
from hivedb import config

# إنشاء محرك SQLAlchemy
engine = create_engine(config.get_database_url())

# تنفيذ استعلام
with engine.connect() as connection:
    result = connection.execute(text("SELECT COUNT(*) FROM cells"))
    cell_count = result.scalar()
    print(f"عدد الخلايا في النظام: {cell_count}")
```

## استخدام HiveDB مع Redis للتخزين المؤقت

### تخزين واسترجاع البيانات من Redis

```python
import redis
from hivedb import config
import json

# الاتصال بـ Redis
redis_client = redis.from_url(config.get_redis_url())

# تخزين بيانات في التخزين المؤقت
user_data = {
    "id": 123,
    "name": "أحمد",
    "preferences": {
        "theme": "dark",
        "language": "ar"
    }
}

redis_client.setex(
    "user:123:profile",  # المفتاح
    3600,               # وقت انتهاء الصلاحية (بالثواني)
    json.dumps(user_data)  # البيانات (محولة إلى JSON)
)

# استرجاع البيانات من التخزين المؤقت
cached_data = redis_client.get("user:123:profile")
if cached_data:
    user = json.loads(cached_data)
    print(f"مرحبًا {user['name']}!")
else:
    print("لم يتم العثور على بيانات المستخدم في التخزين المؤقت")
```

### استخدام Redis للقفل والتزامن

```python
import redis
from hivedb import config
import time

redis_client = redis.from_url(config.get_redis_url())

def with_lock(resource_name, timeout=10):
    """مساعد للتنفيذ مع قفل Redis"""
    lock_key = f"lock:{resource_name}"
    lock_id = str(time.time())
    
    # محاولة الحصول على القفل
    acquired = redis_client.set(lock_key, lock_id, ex=timeout, nx=True)
    if not acquired:
        return False
    
    try:
        # تنفيذ العملية المطلوبة هنا
        print(f"تم الحصول على القفل لـ {resource_name}")
        # ... العمليات المتزامنة ...
        return True
    finally:
        # تحرير القفل إذا كان لا يزال لنا
        if redis_client.get(lock_key) == lock_id:
            redis_client.delete(lock_key)
            print(f"تم تحرير القفل لـ {resource_name}")

# استخدام القفل لمزامنة الوصول إلى مورد
if with_lock("cell:update:123456"):
    print("تم تنفيذ العملية بنجاح")
else:
    print("فشل في الحصول على القفل، المورد مشغول")
```

## استخدام HiveDB مع Kafka للرسائل

### إرسال رسائل إلى Kafka

```python
from kafka import KafkaProducer
from hivedb import config
import json

# إنشاء منتج Kafka
producer = KafkaProducer(
    bootstrap_servers=config.get_kafka_servers(),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# إرسال حدث تسجيل دخول المستخدم
login_event = {
    "event_type": "user_login",
    "user_id": 123,
    "timestamp": "2023-05-21T10:30:00Z",
    "ip_address": "192.168.1.1",
    "device": "mobile"
}

producer.send('user_events', login_event)
producer.flush()
```

### استهلاك رسائل من Kafka

```python
from kafka import KafkaConsumer
from hivedb import config
import json

# إنشاء مستهلك Kafka
consumer = KafkaConsumer(
    'user_events',
    bootstrap_servers=config.get_kafka_servers(),
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# استهلاك الرسائل
for message in consumer:
    event = message.value
    print(f"تم استلام حدث: {event['event_type']} للمستخدم {event['user_id']}")
    
    # معالجة الحدث حسب النوع
    if event['event_type'] == 'user_login':
        print(f"تسجيل دخول من الجهاز: {event['device']}")
    elif event['event_type'] == 'data_update':
        print(f"تحديث البيانات في الخلية: {event.get('cell_id')}")
```

## استخدام HiveDB مع Intel SGX للأمان المتقدم

### تشفير البيانات باستخدام SGX

```python
from hivedb.security import sgx
from hivedb import config

# التحقق من دعم SGX
if config.is_sgx_enabled():
    # إنشاء بيئة آمنة
    secure_enclave = sgx.create_enclave()
    
    # تشفير البيانات داخل البيئة الآمنة
    sensitive_data = "بيانات سرية للغاية"
    encrypted_data = secure_enclave.encrypt(sensitive_data)
    
    print("تم تشفير البيانات بنجاح")
    
    # تخزين البيانات المشفرة
    # ... تخزين encrypted_data ...
    
    # فك تشفير البيانات (يتم فقط داخل البيئة الآمنة)
    decrypted_data = secure_enclave.decrypt(encrypted_data)
    assert decrypted_data == sensitive_data
    
    # إغلاق البيئة الآمنة
    secure_enclave.destroy()
else:
    print("SGX غير مدعوم أو غير ممكّن على هذا النظام")
```

## استخدام HiveDB مع Prometheus للمراقبة

### إضافة مقاييس مخصصة

```python
from prometheus_client import Counter, Gauge, Histogram
from hivedb.monitoring import metrics

# إنشاء عدادات مخصصة
login_counter = Counter(
    'hivedb_user_logins_total',
    'عدد عمليات تسجيل الدخول',
    ['status']  # نجاح أو فشل
)

cell_size_gauge = Gauge(
    'hivedb_cell_size_bytes',
    'حجم الخلية بالبايت',
    ['cell_id']
)

query_time = Histogram(
    'hivedb_query_duration_seconds',
    'وقت تنفيذ الاستعلام بالثواني',
    ['query_type']
)

# استخدام المقاييس في التطبيق
def handle_login(username, password):
    # ... منطق تسجيل الدخول ...
    if login_successful:
        login_counter.labels(status='success').inc()
    else:
        login_counter.labels(status='failure').inc()

def update_cell_data(cell_id, data):
    # ... منطق تحديث البيانات ...
    cell_size = calculate_cell_size(cell_id)
    cell_size_gauge.labels(cell_id=cell_id).set(cell_size)

def execute_query(query_type, query_params):
    with query_time.labels(query_type=query_type).time():
        # ... تنفيذ الاستعلام ...
        return result
```

## استخدام HiveDB في وضع عدم الاتصال

### مزامنة البيانات عند استعادة الاتصال

```python
from hivedb import HiveDBClient
import time

# إنشاء عميل مع دعم وضع عدم الاتصال
client = HiveDBClient(
    api_url="https://api.hivedb.example.com",
    offline_mode=True,
    sync_interval=60  # مزامنة كل 60 ثانية عند توفر الاتصال
)

# الاتصال بخلية
cell = client.connect_cell("cell123456", "password123")

# العمل في وضع عدم الاتصال
while True:
    try:
        # محاولة تخزين البيانات
        cell.store("sensor_reading", {
            "temperature": 25.5,
            "humidity": 60,
            "timestamp": time.time()
        })
        
        print("تم تخزين القراءة (قد تكون في وضع عدم الاتصال)")
        
        # محاولة المزامنة
        sync_status = client.sync()
        if sync_status.get("synced", False):
            print(f"تمت المزامنة: {sync_status.get('items_synced')} عناصر")
        
    except Exception as e:
        print(f"خطأ: {e}")
    
    time.sleep(10)  # انتظار 10 ثوانٍ قبل القراءة التالية
```

## استخدام HiveDB مع WebAssembly

### تشغيل شيفرة آمنة داخل المتصفح

```javascript
// مثال JavaScript لتشغيل وظائف HiveDB في المتصفح باستخدام WebAssembly

// استيراد وحدة HiveDB WebAssembly
import { initHiveDB, createCell, queryData } from 'hivedb-wasm';

async function runSecureComputation() {
  // تهيئة وحدة WebAssembly
  await initHiveDB();
  
  // إنشاء خلية محلية (تعمل بالكامل في المتصفح)
  const cell = await createCell({
    password: 'secure-local-password'
  });
  
  // تخزين بيانات محلية
  await cell.store('user_data', {
    name: 'سارة',
    age: 28,
    location: 'الرياض'
  });
  
  // تنفيذ استعلام محلي آمن
  const results = await queryData(cell, {
    filter: { age: { $gt: 20 } }
  });
  
  console.log('نتائج الاستعلام:', results);
  
  // تشفير البيانات للتخزين أو النقل
  const encryptedData = await cell.exportEncrypted();
  
  // يمكن إرسال encryptedData إلى الخادم للتخزين
  // البيانات مشفرة ولا يمكن فك تشفيرها إلا باستخدام كلمة المرور الأصلية
}

runSecureComputation();
```

## استخدام لغة استعلام HiveDB (HQL)

### استعلامات متقدمة باستخدام HQL

```python
from hivedb import HiveDBClient

client = HiveDBClient(api_url="https://api.hivedb.example.com")
cell = client.connect_cell("cell123456", "password123")

# استعلام باستخدام HQL
results = cell.query_hql("""
    SELECT * FROM cell.data
    WHERE data.type = 'product'
    AND data.price > 100
    AND data.category IN ('electronics', 'computers')
    ORDER BY data.price DESC
    LIMIT 10
""")

for item in results:
    print(f"المنتج: {item['name']}, السعر: {item['price']}")

# استعلام متقدم مع تجميع
summary = cell.query_hql("""
    SELECT 
        data.category AS category,
        COUNT(*) AS count,
        AVG(data.price) AS avg_price,
        MIN(data.price) AS min_price,
        MAX(data.price) AS max_price
    FROM cell.data
    WHERE data.type = 'product'
    GROUP BY data.category
    HAVING COUNT(*) > 5
    ORDER BY avg_price DESC
""")

for category in summary:
    print(f"الفئة: {category['category']}")
    print(f"  عدد المنتجات: {category['count']}")
    print(f"  متوسط السعر: {category['avg_price']}")
    print(f"  أقل سعر: {category['min_price']}")
    print(f"  أعلى سعر: {category['max_price']}")
```

## استخدام HiveDB في تطبيقات Flutter

### مثال لتطبيق Flutter مع HiveDB

```dart
import 'package:flutter/material.dart';
import 'package:hivedb_flutter/hivedb_flutter.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'تطبيق HiveDB',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final HiveDBClient client = HiveDBClient(
    config: HiveDBConfig(
      apiUrl: 'https://api.hivedb.example.com',
      offlineMode: true,
      cacheTTL: Duration(hours: 1),
    ),
  );
  
  Cell? cell;
  List<Map<String, dynamic>> items = [];
  bool isLoading = false;
  
  @override
  void initState() {
    super.initState();
    _connectToCell();
  }
  
  Future<void> _connectToCell() async {
    setState(() => isLoading = true);
    
    try {
      // الاتصال بالخلية
      cell = await client.connectCell(
        'cell123456',
        'password123',
      );
      
      // استرجاع البيانات
      await _loadData();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('خطأ في الاتصال: $e')),
      );
    } finally {
      setState(() => isLoading = false);
    }
  }
  
  Future<void> _loadData() async {
    if (cell == null) return;
    
    try {
      final result = await cell!.query({
        'sort': ['createdAt'],
        'limit': 20,
      });
      
      setState(() {
        items = List<Map<String, dynamic>>.from(result['results']);
      });
    } catch (e) {
      print('خطأ في استرجاع البيانات: $e');
    }
  }
  
  Future<void> _addItem() async {
    if (cell == null) return;
    
    final newItem = {
      'title': 'عنصر جديد',
      'description': 'وصف العنصر الجديد',
      'createdAt': DateTime.now().toIso8601String(),
    };
    
    try {
      await cell!.store('item_${DateTime.now().millisecondsSinceEpoch}', newItem);
      _loadData();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('خطأ في إضافة العنصر: $e')),
      );
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('HiveDB مثال')),
      body: isLoading
          ? Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: items.length,
              itemBuilder: (context, index) {
                final item = items[index];
                return ListTile(
                  title: Text(item['title'] ?? 'بلا عنوان'),
                  subtitle: Text(item['description'] ?? ''),
                );
              },
            ),
      floatingActionButton: FloatingActionButton(
        onPressed: _addItem,
        child: Icon(Icons.add),
      ),
    );
  }
}
```

هذه الأمثلة توضح الاستخدامات المتقدمة لـ HiveDB مع المكونات الإضافية المختلفة. يمكن تعديلها حسب احتياجات المشروع الخاص بك.
