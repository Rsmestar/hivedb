# HiveDB - نظام قواعد بيانات ثوري مستوحى من خلية النحل

HiveDB هو نظام قواعد بيانات مبتكر مستوحى من هيكل خلية النحل، يوفر طريقة فريدة لتخزين البيانات واسترجاعها باستخدام هيكل سداسي.

## المميزات الرئيسية

- 🔷 **هيكل بيانات سداسي**: تخزين البيانات في خلايا سداسية مترابطة
- 🔒 **أمان متقدم**: دعم التشفير وآليات الأمان المتقدمة
- 🚀 **أداء عالي**: تحسين الاستعلامات وتخزين مؤقت سائل
- 📊 **مراقبة متكاملة**: دعم Prometheus و Grafana لمراقبة النظام
- 🌐 **واجهة ويب**: واجهة مستخدم رسومية سهلة الاستخدام
- 🔌 **واجهة برمجة تطبيقات RESTful**: للتكامل السهل مع التطبيقات الأخرى

## المكونات الرئيسية

1. **مكتبة Rust الأساسية**: توفر وظائف قواعد البيانات الأساسية
2. **خادم API**: مبني باستخدام FastAPI لتوفير واجهة برمجة تطبيقات RESTful
3. **واجهة المستخدم**: تطبيق ويب مبني باستخدام React
4. **أدوات المراقبة**: Prometheus و Grafana لمراقبة الأداء والصحة

## متطلبات النظام

- Python 3.9+
- Node.js 14+
- Rust 1.56+
- PostgreSQL 14+
- Redis 7+

## التثبيت والتشغيل المحلي

### تثبيت المتطلبات

```bash
# تثبيت متطلبات Python
cd server
pip install -r requirements.txt

# تثبيت متطلبات واجهة المستخدم
cd ../web_interface
npm install
```

### تشغيل الخادم

```bash
cd server
uvicorn main:app --reload
```

### تشغيل واجهة المستخدم

```bash
cd web_interface
npm start
```

## النشر على Render

تم تبسيط المشروع للنشر السهل على منصة Render. اتبع الخطوات التالية:

### النشر التلقائي باستخدام render.yaml

1. قم بإنشاء حساب على [Render](https://render.com)
2. اربط حسابك بمستودع GitHub الخاص بالمشروع
3. انقر على زر "New Blueprint Instance"
4. حدد مستودع المشروع
5. سيقوم Render تلقائيًا بإنشاء الخدمات المحددة في ملف `render.yaml`

### النشر اليدوي

#### نشر خادم API:

1. انتقل إلى لوحة تحكم Render وانقر على "New Web Service"
2. حدد مستودع GitHub الخاص بالمشروع
3. اضبط الإعدادات التالية:
   - **Name**: hivedb-api
   - **Environment**: Python
   - **Build Command**: `pip install -r server/requirements.txt`
   - **Start Command**: `cd server && gunicorn -k uvicorn.workers.UvicornWorker main:app`
   - **Add Environment Variable**: `PORT=8000`

#### نشر واجهة المستخدم:

1. انقر على "New Static Site"
2. حدد نفس المستودع
3. اضبط الإعدادات التالية:
   - **Name**: hivedb-web
   - **Build Command**: `cd web_interface && npm install && npm run build`
   - **Publish Directory**: `web_interface/build`
   - **Add Environment Variable**: `REACT_APP_API_URL=https://[your-api-url]`

## المساهمة

نرحب بالمساهمات! يرجى اتباع هذه الخطوات:

1. انسخ المستودع (Fork)
2. أنشئ فرعًا جديدًا (`git checkout -b feature/amazing-feature`)
3. قم بإجراء تغييراتك
4. أرسل التغييرات (`git push origin feature/amazing-feature`)
5. افتح طلب سحب (Pull Request)

## الترخيص

هذا المشروع مرخص تحت رخصة MIT - انظر ملف [LICENSE](LICENSE) للتفاصيل.
