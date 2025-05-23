#!/bin/bash

# سكريبت لإنشاء ملف ZIP للمشروع جاهز للرفع إلى Render
echo "🔶 جاري إنشاء ملف ZIP لمشروع HiveDB..."

# إنشاء مجلد مؤقت للنسخة المضغوطة
TEMP_DIR="hivedb_render_upload"
mkdir -p $TEMP_DIR

# نسخ الملفات الضرورية فقط
echo "📋 نسخ الملفات الضرورية..."
cp -r server $TEMP_DIR/
cp -r web_interface $TEMP_DIR/
cp render.yaml $TEMP_DIR/
cp Procfile $TEMP_DIR/
cp README.md $TEMP_DIR/
cp LICENSE $TEMP_DIR/

# حذف الملفات غير الضرورية
echo "🧹 تنظيف الملفات غير الضرورية..."
find $TEMP_DIR -name "node_modules" -type d -exec rm -rf {} +
find $TEMP_DIR -name "__pycache__" -type d -exec rm -rf {} +
find $TEMP_DIR -name "*.pyc" -type f -delete
find $TEMP_DIR -name ".DS_Store" -type f -delete

# إنشاء ملف ZIP
echo "📦 إنشاء ملف ZIP..."
zip -r hivedb_render_upload.zip $TEMP_DIR

# تنظيف
rm -rf $TEMP_DIR

echo "✅ تم إنشاء ملف hivedb_render_upload.zip بنجاح!"
echo "🚀 يمكنك الآن رفع هذا الملف إلى خدمة استضافة تدعم رفع ملفات ZIP مثل Netlify أو Vercel."
echo "⚠️ ملاحظة: Render لا يدعم رفع ملفات ZIP مباشرة، لكن يمكنك استخدام مستودع Git مؤقت كما هو موضح في الخطوات التالية."
