# مكتبة HiveDB لـ Python

مكتبة Python الرسمية للتفاعل مع نظام قواعد بيانات HiveDB المستوحى من خلية النحل.

## التثبيت

```bash
pip install hivedb
```

## الاستخدام الأساسي

```python
import hivedb

# الاتصال بالخلية
my_cell = hivedb.connect(
  cell_key="cell1024563254136",
  password="IloveBees123"
)

# تخزين بيانات (مفتاح ← قيمة)
my_cell.store("cat_name", "Whiskers")

# جلب البيانات
print(my_cell.get("cat_name"))  # يُعطي: Whiskers

# تخزين كائن JSON
user_data = {
    "name": "أحمد",
    "age": 28,
    "interests": ["البرمجة", "الطبيعة", "القراءة"]
}
my_cell.store_json("user_profile", user_data)

# جلب كائن JSON
profile = my_cell.get_json("user_profile")
print(profile["name"])  # يُعطي: أحمد
```

## المميزات

- ✅ واجهة برمجة بسيطة وسهلة الاستخدام
- 🔒 تشفير تلقائي للبيانات
- 🚀 أداء عالي مع تخزين محلي مؤقت
- 🌐 دعم الاتصال عبر الإنترنت والوضع غير المتصل
- 📦 دعم تخزين البيانات المعقدة (JSON، الصور، الملفات)

## الوثائق الكاملة

للمزيد من المعلومات والأمثلة المتقدمة، يرجى زيارة [الوثائق الرسمية](https://docs.hivedb.io).
