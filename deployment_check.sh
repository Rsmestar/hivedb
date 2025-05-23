#!/bin/bash

# سكريبت للتحقق من جاهزية المشروع للنشر على Render
# المؤلف: فريق HiveDB

echo "🔶 جاري التحقق من جاهزية HiveDB للنشر على Render..."

# التحقق من وجود الملفات الرئيسية
echo "📋 التحقق من وجود الملفات الرئيسية..."

FILES_TO_CHECK=(
  "render.yaml"
  "server/requirements.txt"
  "server/main.py"
  "web_interface/package.json"
  "web_interface/src/components/HexLogo.js"
  "web_interface/src/components/HomePage.js"
  "Procfile"
  "README.md"
  "LICENSE"
)

ALL_FILES_EXIST=true

for file in "${FILES_TO_CHECK[@]}"; do
  if [ -f "$file" ]; then
    echo "✅ $file موجود"
  else
    echo "❌ $file غير موجود"
    ALL_FILES_EXIST=false
  fi
done

# التحقق من وجود المتطلبات في ملف requirements.txt
echo -e "\n📦 التحقق من متطلبات الخادم..."
REQUIRED_PACKAGES=(
  "fastapi"
  "uvicorn"
  "gunicorn"
  "sqlalchemy"
  "pydantic"
  "python-jose"
  "passlib"
)

if [ -f "server/requirements.txt" ]; then
  for package in "${REQUIRED_PACKAGES[@]}"; do
    if grep -q "$package" "server/requirements.txt"; then
      echo "✅ $package موجود في requirements.txt"
    else
      echo "⚠️ $package غير موجود في requirements.txt"
    fi
  done
else
  echo "❌ ملف server/requirements.txt غير موجود"
fi

# التحقق من وجود المتطلبات في ملف package.json
echo -e "\n📦 التحقق من متطلبات واجهة المستخدم..."
REQUIRED_DEPENDENCIES=(
  "react"
  "react-dom"
  "react-router-dom"
  "@mui/material"
  "axios"
  "three"
)

if [ -f "web_interface/package.json" ]; then
  for dependency in "${REQUIRED_DEPENDENCIES[@]}"; do
    if grep -q "\"$dependency\"" "web_interface/package.json"; then
      echo "✅ $dependency موجود في package.json"
    else
      echo "⚠️ $dependency غير موجود في package.json"
    fi
  done
else
  echo "❌ ملف web_interface/package.json غير موجود"
fi

# التحقق من ملف render.yaml
echo -e "\n🔧 التحقق من ملف render.yaml..."
if [ -f "render.yaml" ]; then
  if grep -q "hivedb-api" "render.yaml" && grep -q "hivedb-web" "render.yaml"; then
    echo "✅ ملف render.yaml يحتوي على تكوينات الخدمات المطلوبة"
  else
    echo "⚠️ ملف render.yaml قد لا يحتوي على جميع الخدمات المطلوبة"
  fi
else
  echo "❌ ملف render.yaml غير موجود"
fi

# التحقق من وجود نقطة نهاية للتحقق من الصحة في ملف main.py
echo -e "\n🔍 التحقق من وجود نقطة نهاية للتحقق من الصحة..."
if [ -f "server/main.py" ]; then
  if grep -q "health_check" "server/main.py" || grep -q "healthcheck" "server/main.py"; then
    echo "✅ نقطة نهاية للتحقق من الصحة موجودة في main.py"
  else
    echo "⚠️ لم يتم العثور على نقطة نهاية للتحقق من الصحة في main.py"
  fi
else
  echo "❌ ملف server/main.py غير موجود"
fi

# ملخص النتائج
echo -e "\n🔶 ملخص التحقق من الجاهزية:"
if [ "$ALL_FILES_EXIST" = true ]; then
  echo "✅ جميع الملفات الرئيسية موجودة"
else
  echo "❌ بعض الملفات الرئيسية مفقودة"
fi

echo -e "\n🚀 خطوات النشر التالية:"
echo "1. تأكد من أن جميع التغييرات قد تم تأكيدها ودفعها إلى مستودع GitHub"
echo "2. قم بتسجيل الدخول إلى حساب Render الخاص بك"
echo "3. انقر على 'New Blueprint Instance' واختر مستودع GitHub الخاص بك"
echo "4. سيقوم Render تلقائيًا بإنشاء الخدمات المحددة في ملف render.yaml"
echo "5. تحقق من سجلات البناء للتأكد من نجاح النشر"

echo -e "\n🔶 اكتمل التحقق من جاهزية HiveDB للنشر على Render!"
