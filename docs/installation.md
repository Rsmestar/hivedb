# دليل تثبيت HiveDB

هذا الدليل يوضح كيفية تثبيت نظام HiveDB بشكل كامل على بيئة التطوير أو الإنتاج.

## متطلبات النظام

### المتطلبات الأساسية

- نظام تشغيل: Linux، macOS، أو Windows
- Python 3.8 أو أحدث
- Node.js 16 أو أحدث
- PostgreSQL 14 أو أحدث
- Rust 1.56 أو أحدث (لنواة النظام)

### المتطلبات للتطوير

- Docker و Docker Compose (موصى به بشدة)
- Git
- Visual Studio Code أو أي محرر نصوص متقدم

### المكونات المدعومة

- PostgreSQL (لتخزين البيانات الهيكلية)
- Redis (للتخزين المؤقت وإدارة الجلسات)
- Apache Kafka (لمعالجة الرسائل والأحداث)
- Prometheus و Grafana (للمراقبة)
- Intel SGX (للأمان المتقدم وتشفير البيانات)

## تثبيت نواة النظام (Rust)

1. تثبيت Rust إذا لم يكن مثبتًا بالفعل:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

2. تثبيت نواة HiveDB:

```bash
cd /path/to/hivedb
cargo build --release
```

3. اختبار التثبيت:

```bash
cargo test
```

## تثبيت خادم API (Python)

1. إنشاء بيئة Python افتراضية (اختياري ولكن موصى به):

```bash
python -m venv venv
source venv/bin/activate  # على Linux/macOS
# أو
venv\Scripts\activate  # على Windows
```

2. تثبيت المتطلبات:

```bash
cd server
pip install -r requirements.txt
```

3. إنشاء مجلد التخزين:

```bash
mkdir -p cells
```

4. تكوين الخادم (اختياري):

يمكنك تعديل إعدادات الخادم عن طريق إنشاء ملف `.env` في مجلد `server`:

```
HOST=0.0.0.0
PORT=8000
CELLS_DIR=cells
SESSION_SECRET=your-secret-key
```

## تثبيت واجهة المستخدم (React)

1. تثبيت المتطلبات:

```bash
cd web_interface
npm install
```

2. تكوين واجهة المستخدم:

قم بإنشاء ملف `.env.local` في مجلد `web_interface`:

```
REACT_APP_API_URL=http://localhost:8000
```

## تثبيت مكتبة Python

1. تثبيت المكتبة:

```bash
cd python_client
pip install -e .
```

## تشغيل النظام

### تشغيل الخادم

```bash
cd server
python main.py
```

أو باستخدام uvicorn مباشرة:

```bash
cd server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### تشغيل واجهة المستخدم

```bash
cd web_interface
npm start
```

## النشر للإنتاج

### نشر الخادم

يمكنك نشر خادم FastAPI باستخدام Gunicorn و Uvicorn:

```bash
pip install gunicorn
cd server
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### نشر واجهة المستخدم

لبناء نسخة الإنتاج من واجهة المستخدم:

```bash
cd web_interface
npm run build
```

ثم يمكنك استضافة المحتوى الثابت الناتج في مجلد `build` على أي خادم ويب مثل Nginx أو Apache.

### نشر باستخدام Docker Compose (موصى به)

يوفر HiveDB ملف `docker-compose.yml` لتسهيل نشر النظام بالكامل مع جميع المكونات الضرورية:

1. تأكد من تثبيت Docker و Docker Compose على نظامك:

```bash
docker --version
docker-compose --version
```

2. قم بإنشاء ملف `.env` في المجلد الرئيسي للمشروع (اختياري):

```
SESSION_SECRET=your-secure-secret-key
POSTGRES_PASSWORD=your-secure-database-password
API_URL=http://localhost:8000
GRAFANA_PASSWORD=your-secure-grafana-password
SGX_ENABLED=false
```

3. تشغيل جميع الخدمات باستخدام Docker Compose:

```bash
docker-compose up -d
```

هذا سيقوم بتشغيل:
- خادم API على المنفذ 8000
- واجهة المستخدم على المنفذ 80
- قاعدة بيانات PostgreSQL على المنفذ 5432
- خادم Redis على المنفذ 6379
- Kafka على المنفذ 9092
- Prometheus للمراقبة على المنفذ 9090
- Grafana للوحات المعلومات على المنفذ 3000

4. مراقبة السجلات:

```bash
docker-compose logs -f
```

5. إيقاف جميع الخدمات:

```bash
docker-compose down
```

### نشر باستخدام Docker (الطريقة اليدوية)

إذا كنت ترغب في بناء وتشغيل الحاويات يدويًا:

1. بناء صورة Docker للخادم:

```bash
cd server
docker build -t hivedb-server .
```

2. بناء صورة Docker لواجهة المستخدم:

```bash
cd web_interface
docker build -t hivedb-ui .
```

3. تشغيل الحاويات:

```bash
docker run -d -p 8000:8000 --name hivedb-server hivedb-server
docker run -d -p 80:80 --name hivedb-ui hivedb-ui
```

## المكونات الإضافية

### PostgreSQL

يستخدم HiveDB قاعدة بيانات PostgreSQL لتخزين البيانات الهيكلية مثل معلومات المستخدمين والخلايا:

- **المنفذ الافتراضي**: 5432
- **اسم المستخدم الافتراضي**: hivedb
- **قاعدة البيانات الافتراضية**: hivedb

للاتصال بقاعدة البيانات مباشرة:

```bash
docker exec -it hivedb-postgres psql -U hivedb -d hivedb
```

### Redis

يستخدم HiveDB Redis للتخزين المؤقت وإدارة الجلسات:

- **المنفذ الافتراضي**: 6379

للاتصال بخادم Redis مباشرة:

```bash
docker exec -it hivedb-redis redis-cli
```

### Kafka

يستخدم HiveDB Kafka لمعالجة الرسائل والأحداث بين مكونات النظام:

- **المنفذ الافتراضي**: 9092

لإنشاء موضوع (topic) جديد:

```bash
docker exec -it hivedb-kafka kafka-topics.sh --create --topic my-topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

### Prometheus و Grafana

يستخدم HiveDB Prometheus و Grafana لمراقبة أداء النظام:

- **منفذ Prometheus الافتراضي**: 9090
- **منفذ Grafana الافتراضي**: 3000
- **بيانات اعتماد Grafana الافتراضية**: admin/admin

يمكنك الوصول إلى واجهة Grafana من خلال المتصفح على العنوان: http://localhost:3000

## استكشاف الأخطاء وإصلاحها

### مشاكل الاتصال بالخادم

إذا واجهت مشاكل في الاتصال بالخادم، تحقق من:

- أن الخادم يعمل على المنفذ الصحيح (تحقق باستخدام `docker-compose ps`)
- أن إعدادات CORS مكونة بشكل صحيح
- أن عنوان API في واجهة المستخدم صحيح

### مشاكل Docker Compose

إذا واجهت مشاكل في تشغيل Docker Compose:

```bash
# تحقق من حالة الحاويات
docker-compose ps

# تحقق من سجلات خدمة معينة
docker-compose logs api

# إعادة بناء الصور
docker-compose build --no-cache

# إعادة تشغيل خدمة معينة
docker-compose restart api
```

### مشاكل قاعدة البيانات

إذا واجهت مشاكل في قاعدة البيانات:

- تحقق من اتصال PostgreSQL: `docker exec -it hivedb-postgres pg_isready -U hivedb`
- تأكد من أن مجلد `cells` موجود ولديه أذونات الكتابة المناسبة
- تحقق من سجلات الخادم للحصول على أي أخطاء في قاعدة البيانات

### مشاكل واجهة المستخدم

إذا واجهت مشاكل في واجهة المستخدم:

- تأكد من تثبيت جميع الحزم بشكل صحيح
- تحقق من وحدة تحكم المتصفح للحصول على أي أخطاء JavaScript
- تحقق من سجلات خدمة الويب: `docker-compose logs web`
