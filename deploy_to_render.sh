#!/bin/bash

# سكريبت لتسهيل نشر HiveDB على Render
# المؤلف: فريق HiveDB

echo "🔶 جاري تحضير HiveDB للنشر على Render..."

# التحقق من المتطلبات
command -v git >/dev/null 2>&1 || { echo "❌ Git غير مثبت. يرجى تثبيته أولاً."; exit 1; }
command -v curl >/dev/null 2>&1 || { echo "❌ Curl غير مثبت. يرجى تثبيته أولاً."; exit 1; }

# التحقق مما إذا كنا في الدليل الجذر للمشروع
if [ ! -f "render.yaml" ]; then
    echo "❌ لم يتم العثور على ملف render.yaml. تأكد من أنك في الدليل الجذر للمشروع."
    exit 1
fi

# تحضير الخادم للنشر
echo "📦 جاري تحضير واجهة برمجة التطبيقات API..."
if [ ! -f "server/Procfile" ]; then
    echo "web: gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:\$PORT" > server/Procfile
    echo "✅ تم إنشاء ملف Procfile للخادم"
fi

# التحقق من وجود ملف .env وإنشائه إذا لم يكن موجودًا
if [ ! -f "server/.env" ]; then
    echo "جاري إنشاء ملف .env للخادم..."
    cat > server/.env << EOL
DATABASE_URL=\${DATABASE_URL}
SECRET_KEY=\${SECRET_KEY}
ACCESS_TOKEN_EXPIRE_MINUTES=60
LIQUID_CACHE_SIZE=1000
LIQUID_CACHE_TTL=3600
EOL
    echo "✅ تم إنشاء ملف .env للخادم"
fi

# تحضير واجهة المستخدم للنشر
echo "🌐 جاري تحضير واجهة المستخدم..."
if [ ! -f "web_interface/.env" ]; then
    echo "جاري إنشاء ملف .env لواجهة المستخدم..."
    echo "REACT_APP_API_URL=\${RENDER_EXTERNAL_URL}" > web_interface/.env
    echo "✅ تم إنشاء ملف .env لواجهة المستخدم"
fi

# التحقق من وجود تغييرات غير مؤكدة
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️ هناك تغييرات غير مؤكدة في المستودع الخاص بك."
    echo "يُنصح بتأكيد هذه التغييرات قبل النشر:"
    git status --short
    
    read -p "هل تريد المتابعة على أي حال؟ (ن/لا): " confirm
    if [ "$confirm" != "ن" ]; then
        echo "❌ تم إلغاء النشر."
        exit 1
    fi
fi

# تحقق من وجود ملف render.yaml وتحديثه إذا لزم الأمر
if [ -f "render.yaml" ]; then
    echo "✅ تم العثور على ملف render.yaml"
else
    echo "⚠️ لم يتم العثور على ملف render.yaml. جاري إنشاء ملف جديد..."
    cat > render.yaml << EOL
services:
  # خدمة API
  - type: web
    name: hivedb-api
    env: python
    buildCommand: pip install -r server/requirements.txt
    startCommand: cd server && uvicorn main:app --host 0.0.0.0 --port \$PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.0
      - key: DATABASE_URL
        fromDatabase:
          name: hivedb-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true

  # واجهة المستخدم
  - type: web
    name: hivedb-web
    env: static
    buildCommand: cd web_interface && npm install && npm run build
    staticPublishPath: ./web_interface/build
    envVars:
      - key: REACT_APP_API_URL
        fromService:
          type: web
          name: hivedb-api
          envVarKey: RENDER_EXTERNAL_URL

databases:
  - name: hivedb-db
    databaseName: hivedb
    user: hivedb
    plan: free
EOL
    echo "✅ تم إنشاء ملف render.yaml"
fi

echo "🚀 مشروع HiveDB جاهز للنشر على Render."
echo ""
echo "للنشر يدويًا:"
echo "1. انتقل إلى https://dashboard.render.com/select-repo"
echo "2. قم بتوصيل مستودع GitHub الخاص بك"
echo "3. حدد 'Blueprint' وسيقوم Render تلقائيًا بإنشاء الخدمات المحددة في ملف render.yaml"
echo ""
echo "أو لنشر الخدمات بشكل فردي:"
echo "- API: قم بإنشاء خدمة ويب جديدة وأشر إلى مجلد 'server'"
echo "- واجهة المستخدم: قم بإنشاء موقع ثابت جديد وأشر إلى مجلد 'web_interface'"
echo ""
echo "حظًا سعيدًا مع النشر! 🔶"
