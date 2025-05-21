# أمثلة استخدام HiveDB

هذا المجلد يحتوي على أمثلة عملية لاستخدام نظام HiveDB في سيناريوهات مختلفة.

## قائمة الأمثلة

1. [مذكرات شخصية](./personal_diary/) - تطبيق مذكرات شخصية بسيط باستخدام HiveDB
2. [إدارة كلمات المرور](./password_manager/) - مدير كلمات مرور آمن باستخدام HiveDB
3. [مشاركة الملاحظات](./note_sharing/) - تطبيق لمشاركة الملاحظات بين المستخدمين

## كيفية تشغيل الأمثلة

1. تأكد من تثبيت مكتبة HiveDB:

```bash
pip install -e ../python_client
```

2. انتقل إلى مجلد المثال الذي تريد تشغيله:

```bash
cd personal_diary
```

3. قم بتشغيل المثال:

```bash
python main.py
```

## مثال سريع

هذا مثال بسيط لاستخدام HiveDB لتخزين واسترجاع البيانات:

```python
import hivedb
import getpass
import uuid

def create_new_cell():
    """إنشاء خلية جديدة"""
    password = getpass.getpass("أدخل كلمة مرور للخلية الجديدة: ")
    cell_key = f"cell{str(uuid.uuid4().int)[:10]}"
    
    print(f"تم إنشاء خلية جديدة بمفتاح: {cell_key}")
    print("احتفظ بهذا المفتاح في مكان آمن!")
    
    return cell_key, password

def connect_to_cell():
    """الاتصال بخلية موجودة"""
    cell_key = input("أدخل مفتاح الخلية: ")
    password = getpass.getpass("أدخل كلمة المرور: ")
    
    return cell_key, password

def main():
    print("=== مرحبًا بك في تطبيق HiveDB ===")
    print("1. إنشاء خلية جديدة")
    print("2. الاتصال بخلية موجودة")
    
    choice = input("اختر رقم العملية: ")
    
    if choice == "1":
        cell_key, password = create_new_cell()
    elif choice == "2":
        cell_key, password = connect_to_cell()
    else:
        print("اختيار غير صالح")
        return
    
    # الاتصال بالخلية
    try:
        cell = hivedb.connect(cell_key, password)
        print(f"تم الاتصال بالخلية {cell_key} بنجاح")
    except Exception as e:
        print(f"خطأ في الاتصال: {e}")
        return
    
    # قائمة العمليات
    while True:
        print("\n=== العمليات المتاحة ===")
        print("1. تخزين بيانات")
        print("2. استرجاع بيانات")
        print("3. حذف بيانات")
        print("4. عرض جميع المفاتيح")
        print("5. خروج")
        
        op = input("اختر رقم العملية: ")
        
        if op == "1":
            key = input("أدخل المفتاح: ")
            value = input("أدخل القيمة: ")
            cell.store(key, value)
            print("تم تخزين البيانات بنجاح")
        
        elif op == "2":
            key = input("أدخل المفتاح: ")
            value = cell.get(key)
            if value:
                print(f"القيمة: {value}")
            else:
                print("المفتاح غير موجود")
        
        elif op == "3":
            key = input("أدخل المفتاح: ")
            cell.delete(key)
            print("تم حذف البيانات بنجاح")
        
        elif op == "4":
            keys = cell.list_keys()
            if keys:
                print("المفاتيح المخزنة:")
                for i, key in enumerate(keys, 1):
                    print(f"{i}. {key}")
            else:
                print("لا توجد بيانات مخزنة")
        
        elif op == "5":
            print("شكرًا لاستخدام HiveDB")
            break
        
        else:
            print("اختيار غير صالح")

if __name__ == "__main__":
    main()
```

## تطوير أمثلة جديدة

نرحب بمساهماتكم في إضافة أمثلة جديدة! إذا كنت ترغب في المساهمة، يرجى اتباع الخطوات التالية:

1. إنشاء مجلد جديد لمثالك
2. إضافة ملف README.md يشرح المثال
3. إضافة التعليقات المناسبة في الكود
4. إرسال طلب سحب (Pull Request)

## الترخيص

جميع الأمثلة مرخصة بموجب MIT License، نفس ترخيص مشروع HiveDB.
