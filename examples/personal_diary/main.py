#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
تطبيق مذكرات شخصية باستخدام HiveDB
يوضح كيفية استخدام HiveDB لتخزين واسترجاع المذكرات اليومية
"""

import hivedb
import getpass
import json
import os
import sys
import datetime
import uuid
from tabulate import tabulate

# تكوين المسارات
CONFIG_DIR = os.path.expanduser("~/.hivedb_diary")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

def setup_config_dir():
    """إنشاء مجلد التكوين إذا لم يكن موجودًا"""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

def save_config(cell_key):
    """حفظ مفتاح الخلية في ملف التكوين"""
    setup_config_dir()
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump({"cell_key": cell_key}, f)

def load_config():
    """تحميل مفتاح الخلية من ملف التكوين"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f).get("cell_key")
    return None

def clear_screen():
    """مسح الشاشة لتحسين واجهة المستخدم"""
    os.system('cls' if os.name == 'nt' else 'clear')

def create_new_cell():
    """إنشاء خلية جديدة للمذكرات"""
    print("=== إنشاء مذكرات جديدة ===")
    print("سنقوم بإنشاء خلية جديدة لتخزين مذكراتك بشكل آمن.")
    print("ملاحظة: تأكد من حفظ كلمة المرور في مكان آمن، لا يمكن استردادها إذا نسيتها!")
    
    password = getpass.getpass("أدخل كلمة مرور (8 أحرف على الأقل): ")
    if len(password) < 8:
        print("خطأ: يجب أن تكون كلمة المرور 8 أحرف على الأقل")
        return None, None
    
    confirm_password = getpass.getpass("أكد كلمة المرور: ")
    if password != confirm_password:
        print("خطأ: كلمات المرور غير متطابقة")
        return None, None
    
    # إنشاء مفتاح خلية فريد
    cell_key = f"cell{str(uuid.uuid4().int)[:10]}"
    
    print("\n=== معلومات المذكرات الجديدة ===")
    print(f"مفتاح الخلية: {cell_key}")
    print("احتفظ بهذا المفتاح وكلمة المرور في مكان آمن!")
    print("سيتم حفظ مفتاح الخلية محليًا، لكن لن يتم تخزين كلمة المرور.")
    
    # حفظ مفتاح الخلية في ملف التكوين
    save_config(cell_key)
    
    return cell_key, password

def connect_to_cell():
    """الاتصال بخلية موجودة"""
    cell_key = load_config()
    
    if cell_key:
        print(f"تم العثور على مفتاح خلية محفوظ: {cell_key}")
        use_saved = input("هل تريد استخدام هذا المفتاح؟ (ن/ل) [ن]: ").lower() != 'ل'
        
        if not use_saved:
            cell_key = input("أدخل مفتاح الخلية: ")
    else:
        cell_key = input("أدخل مفتاح الخلية: ")
    
    password = getpass.getpass("أدخل كلمة المرور: ")
    
    return cell_key, password

def format_diary_entry(entry):
    """تنسيق مدخل المذكرة للعرض"""
    date = entry.get("date", "غير معروف")
    title = entry.get("title", "بدون عنوان")
    mood = entry.get("mood", "غير محدد")
    content = entry.get("content", "")
    
    return f"""
=== {title} ===
التاريخ: {date}
المزاج: {mood}

{content}
"""

def add_diary_entry(cell):
    """إضافة مدخل جديد للمذكرات"""
    clear_screen()
    print("=== إضافة مذكرة جديدة ===")
    
    # الحصول على التاريخ الحالي
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    date = input(f"التاريخ [اليوم: {today}]: ") or today
    
    title = input("العنوان: ")
    mood = input("المزاج (سعيد، حزين، متحمس، إلخ): ")
    
    print("المحتوى (أدخل 'END' في سطر منفصل للانتهاء):")
    content_lines = []
    while True:
        line = input()
        if line == "END":
            break
        content_lines.append(line)
    
    content = "\n".join(content_lines)
    
    # إنشاء مدخل المذكرة
    entry = {
        "date": date,
        "title": title,
        "mood": mood,
        "content": content,
        "created_at": datetime.datetime.now().isoformat()
    }
    
    # تخزين المدخل في الخلية
    entry_id = f"entry_{date}_{uuid.uuid4().hex[:8]}"
    cell.store_json(entry_id, entry)
    
    print("\nتم حفظ المذكرة بنجاح!")
    input("اضغط Enter للمتابعة...")

def view_diary_entries(cell):
    """عرض جميع مدخلات المذكرات"""
    clear_screen()
    print("=== جميع المذكرات ===")
    
    # الحصول على جميع المفاتيح
    keys = cell.list_keys()
    
    # تصفية مفاتيح المذكرات
    entry_keys = [key for key in keys if key.startswith("entry_")]
    
    if not entry_keys:
        print("لا توجد مذكرات مخزنة بعد.")
        input("اضغط Enter للمتابعة...")
        return
    
    # جمع معلومات المذكرات
    entries = []
    for key in entry_keys:
        entry = cell.get_json(key)
        if entry:
            entries.append({
                "id": key,
                "date": entry.get("date", ""),
                "title": entry.get("title", ""),
                "mood": entry.get("mood", "")
            })
    
    # ترتيب المذكرات حسب التاريخ (الأحدث أولاً)
    entries.sort(key=lambda x: x["date"], reverse=True)
    
    # عرض المذكرات في جدول
    table_data = [[i+1, e["date"], e["title"], e["mood"]] for i, e in enumerate(entries)]
    print(tabulate(table_data, headers=["#", "التاريخ", "العنوان", "المزاج"]))
    
    print("\nاختر رقم المذكرة لعرضها، أو اكتب 'r' للعودة:")
    choice = input("> ")
    
    if choice.lower() == 'r':
        return
    
    try:
        index = int(choice) - 1
        if 0 <= index < len(entries):
            view_diary_entry(cell, entries[index]["id"])
    except ValueError:
        pass

def view_diary_entry(cell, entry_id):
    """عرض مدخل مذكرة محدد"""
    clear_screen()
    
    entry = cell.get_json(entry_id)
    if not entry:
        print("خطأ: لم يتم العثور على المذكرة")
        input("اضغط Enter للمتابعة...")
        return
    
    print(format_diary_entry(entry))
    
    print("\nالخيارات:")
    print("1. تعديل المذكرة")
    print("2. حذف المذكرة")
    print("3. العودة")
    
    choice = input("> ")
    
    if choice == "1":
        edit_diary_entry(cell, entry_id, entry)
    elif choice == "2":
        delete_diary_entry(cell, entry_id, entry)

def edit_diary_entry(cell, entry_id, entry):
    """تعديل مدخل مذكرة"""
    clear_screen()
    print("=== تعديل المذكرة ===")
    print("(اترك الحقل فارغًا للاحتفاظ بالقيمة الحالية)")
    
    date = input(f"التاريخ [{entry.get('date', '')}]: ") or entry.get('date', '')
    title = input(f"العنوان [{entry.get('title', '')}]: ") or entry.get('title', '')
    mood = input(f"المزاج [{entry.get('mood', '')}]: ") or entry.get('mood', '')
    
    print(f"المحتوى الحالي:\n{entry.get('content', '')}")
    print("\nأدخل المحتوى الجديد (أدخل 'END' في سطر منفصل للانتهاء):")
    print("(أدخل 'KEEP' للاحتفاظ بالمحتوى الحالي)")
    
    first_line = input()
    if first_line == "KEEP":
        content = entry.get('content', '')
    else:
        content_lines = [first_line]
        while True:
            line = input()
            if line == "END":
                break
            content_lines.append(line)
        content = "\n".join(content_lines)
    
    # تحديث المدخل
    updated_entry = {
        "date": date,
        "title": title,
        "mood": mood,
        "content": content,
        "created_at": entry.get("created_at", ""),
        "updated_at": datetime.datetime.now().isoformat()
    }
    
    cell.store_json(entry_id, updated_entry)
    
    print("\nتم تحديث المذكرة بنجاح!")
    input("اضغط Enter للمتابعة...")

def delete_diary_entry(cell, entry_id, entry):
    """حذف مدخل مذكرة"""
    clear_screen()
    print("=== حذف المذكرة ===")
    print(f"عنوان: {entry.get('title', '')}")
    print(f"تاريخ: {entry.get('date', '')}")
    
    confirm = input("هل أنت متأكد من حذف هذه المذكرة؟ (ن/ل): ").lower()
    
    if confirm == 'ن':
        cell.delete(entry_id)
        print("\nتم حذف المذكرة بنجاح!")
    else:
        print("\nتم إلغاء الحذف.")
    
    input("اضغط Enter للمتابعة...")

def search_diary_entries(cell):
    """البحث في مدخلات المذكرات"""
    clear_screen()
    print("=== البحث في المذكرات ===")
    
    search_term = input("أدخل مصطلح البحث: ")
    if not search_term:
        return
    
    # الحصول على جميع المفاتيح
    keys = cell.list_keys()
    
    # تصفية مفاتيح المذكرات
    entry_keys = [key for key in keys if key.startswith("entry_")]
    
    # البحث في المذكرات
    results = []
    for key in entry_keys:
        entry = cell.get_json(key)
        if entry:
            # البحث في العنوان والمحتوى
            title = entry.get("title", "").lower()
            content = entry.get("content", "").lower()
            
            if search_term.lower() in title or search_term.lower() in content:
                results.append({
                    "id": key,
                    "date": entry.get("date", ""),
                    "title": entry.get("title", ""),
                    "mood": entry.get("mood", "")
                })
    
    if not results:
        print("لم يتم العثور على نتائج.")
        input("اضغط Enter للمتابعة...")
        return
    
    # عرض نتائج البحث
    print(f"\nتم العثور على {len(results)} نتيجة:")
    table_data = [[i+1, r["date"], r["title"], r["mood"]] for i, r in enumerate(results)]
    print(tabulate(table_data, headers=["#", "التاريخ", "العنوان", "المزاج"]))
    
    print("\nاختر رقم المذكرة لعرضها، أو اكتب 'r' للعودة:")
    choice = input("> ")
    
    if choice.lower() == 'r':
        return
    
    try:
        index = int(choice) - 1
        if 0 <= index < len(results):
            view_diary_entry(cell, results[index]["id"])
    except ValueError:
        pass

def export_diary(cell):
    """تصدير جميع المذكرات إلى ملف JSON"""
    clear_screen()
    print("=== تصدير المذكرات ===")
    
    # الحصول على جميع المفاتيح
    keys = cell.list_keys()
    
    # تصفية مفاتيح المذكرات
    entry_keys = [key for key in keys if key.startswith("entry_")]
    
    if not entry_keys:
        print("لا توجد مذكرات لتصديرها.")
        input("اضغط Enter للمتابعة...")
        return
    
    # جمع جميع المذكرات
    entries = {}
    for key in entry_keys:
        entry = cell.get_json(key)
        if entry:
            entries[key] = entry
    
    # تحديد مسار الملف للتصدير
    export_path = input("أدخل مسار الملف للتصدير (مثال: ~/diary_export.json): ")
    export_path = os.path.expanduser(export_path)
    
    try:
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)
        
        print(f"\nتم تصدير {len(entries)} مذكرة بنجاح إلى {export_path}")
    except Exception as e:
        print(f"خطأ في التصدير: {e}")
    
    input("اضغط Enter للمتابعة...")

def import_diary(cell):
    """استيراد المذكرات من ملف JSON"""
    clear_screen()
    print("=== استيراد المذكرات ===")
    
    # تحديد مسار الملف للاستيراد
    import_path = input("أدخل مسار ملف الاستيراد: ")
    import_path = os.path.expanduser(import_path)
    
    if not os.path.exists(import_path):
        print("خطأ: الملف غير موجود")
        input("اضغط Enter للمتابعة...")
        return
    
    try:
        with open(import_path, 'r', encoding='utf-8') as f:
            entries = json.load(f)
        
        if not isinstance(entries, dict):
            print("خطأ: تنسيق الملف غير صالح")
            input("اضغط Enter للمتابعة...")
            return
        
        # استيراد المذكرات
        for key, entry in entries.items():
            if key.startswith("entry_") and isinstance(entry, dict):
                cell.store_json(key, entry)
        
        print(f"\nتم استيراد {len(entries)} مذكرة بنجاح")
    except Exception as e:
        print(f"خطأ في الاستيراد: {e}")
    
    input("اضغط Enter للمتابعة...")

def show_stats(cell):
    """عرض إحصائيات المذكرات"""
    clear_screen()
    print("=== إحصائيات المذكرات ===")
    
    # الحصول على جميع المفاتيح
    keys = cell.list_keys()
    
    # تصفية مفاتيح المذكرات
    entry_keys = [key for key in keys if key.startswith("entry_")]
    
    if not entry_keys:
        print("لا توجد مذكرات بعد.")
        input("اضغط Enter للمتابعة...")
        return
    
    # جمع المذكرات
    entries = []
    moods = {}
    total_words = 0
    
    for key in entry_keys:
        entry = cell.get_json(key)
        if entry:
            entries.append(entry)
            
            # حساب المزاج
            mood = entry.get("mood", "").lower()
            if mood:
                moods[mood] = moods.get(mood, 0) + 1
            
            # حساب الكلمات
            content = entry.get("content", "")
            total_words += len(content.split())
    
    # ترتيب المذكرات حسب التاريخ
    entries.sort(key=lambda x: x.get("date", ""))
    
    # الإحصائيات
    print(f"إجمالي عدد المذكرات: {len(entries)}")
    print(f"أول مذكرة: {entries[0].get('date', '') if entries else 'لا يوجد'}")
    print(f"آخر مذكرة: {entries[-1].get('date', '') if entries else 'لا يوجد'}")
    print(f"إجمالي عدد الكلمات: {total_words}")
    print(f"متوسط الكلمات لكل مذكرة: {total_words // len(entries) if entries else 0}")
    
    # عرض المزاج الأكثر شيوعًا
    if moods:
        print("\nالمزاج الأكثر شيوعًا:")
        mood_data = sorted(moods.items(), key=lambda x: x[1], reverse=True)
        for mood, count in mood_data[:5]:
            print(f"- {mood}: {count} مرة")
    
    input("\nاضغط Enter للمتابعة...")

def main():
    """الدالة الرئيسية للتطبيق"""
    clear_screen()
    print("=== مرحبًا بك في تطبيق المذكرات الشخصية ===")
    print("تطبيق آمن لحفظ مذكراتك اليومية باستخدام HiveDB")
    print("\n1. إنشاء مذكرات جديدة")
    print("2. فتح مذكرات موجودة")
    
    choice = input("\nاختر رقم العملية: ")
    
    cell_key = None
    password = None
    
    if choice == "1":
        cell_key, password = create_new_cell()
    elif choice == "2":
        cell_key, password = connect_to_cell()
    else:
        print("اختيار غير صالح")
        return
    
    if not cell_key or not password:
        print("لم يتم توفير معلومات الاتصال الصحيحة")
        return
    
    # الاتصال بالخلية
    try:
        cell = hivedb.connect(cell_key, password)
        print(f"تم الاتصال بالخلية {cell_key} بنجاح")
    except Exception as e:
        print(f"خطأ في الاتصال: {e}")
        return
    
    # حلقة القائمة الرئيسية
    while True:
        clear_screen()
        print("=== تطبيق المذكرات الشخصية ===")
        print("1. إضافة مذكرة جديدة")
        print("2. عرض جميع المذكرات")
        print("3. البحث في المذكرات")
        print("4. إحصائيات المذكرات")
        print("5. تصدير المذكرات")
        print("6. استيراد المذكرات")
        print("0. خروج")
        
        choice = input("\nاختر رقم العملية: ")
        
        if choice == "1":
            add_diary_entry(cell)
        elif choice == "2":
            view_diary_entries(cell)
        elif choice == "3":
            search_diary_entries(cell)
        elif choice == "4":
            show_stats(cell)
        elif choice == "5":
            export_diary(cell)
        elif choice == "6":
            import_diary(cell)
        elif choice == "0":
            print("شكرًا لاستخدام تطبيق المذكرات الشخصية")
            break
        else:
            print("اختيار غير صالح")
            input("اضغط Enter للمتابعة...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nتم إنهاء التطبيق")
    except Exception as e:
        print(f"حدث خطأ غير متوقع: {e}")
