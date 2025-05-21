"""
خدمة الذاكرة السائلة (Liquid Cache) لـ HiveDB

توفر هذه الخدمة نظام تخزين مؤقت ذكي يتكيف مع أنماط استخدام المستخدم لتحسين أداء الاستعلامات.
تستخدم خوارزميات تعلم آلي بسيطة للتنبؤ بالاستعلامات المستقبلية وتحميلها مسبقًا.
"""

import os
import time
import json
import logging
import threading
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from datetime import datetime, timedelta
import heapq
from collections import defaultdict, Counter
import numpy as np
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# إعداد التسجيل
logger = logging.getLogger(__name__)

# إعدادات الذاكرة السائلة
LIQUID_CACHE_ENABLED = os.getenv("LIQUID_CACHE_ENABLED", "True").lower() in ("true", "1", "t")
LIQUID_CACHE_SIZE = int(os.getenv("LIQUID_CACHE_SIZE", "1000"))  # عدد العناصر الأقصى في الذاكرة
LIQUID_CACHE_TTL = int(os.getenv("LIQUID_CACHE_TTL", "3600"))  # وقت انتهاء الصلاحية بالثواني
LIQUID_CACHE_PREDICTION_THRESHOLD = float(os.getenv("LIQUID_CACHE_PREDICTION_THRESHOLD", "0.7"))  # حد التنبؤ
LIQUID_CACHE_LEARNING_RATE = float(os.getenv("LIQUID_CACHE_LEARNING_RATE", "0.1"))  # معدل التعلم
LIQUID_CACHE_LAYERS = int(os.getenv("LIQUID_CACHE_LAYERS", "3"))  # عدد طبقات الذاكرة

class CacheItem:
    """عنصر في الذاكرة المؤقتة مع بيانات التعلم"""
    
    def __init__(self, key: str, value: Any, ttl: int = LIQUID_CACHE_TTL):
        self.key = key
        self.value = value
        self.created_at = time.time()
        self.last_accessed = time.time()
        self.access_count = 1
        self.ttl = ttl
        self.layer = 0  # الطبقة الحالية (0 = أسرع، أعلى = أبطأ)
        self.predicted_score = 0.0  # درجة التنبؤ بالاستخدام المستقبلي
    
    def access(self):
        """تسجيل وصول إلى هذا العنصر"""
        self.last_accessed = time.time()
        self.access_count += 1
        
    def is_expired(self) -> bool:
        """التحقق مما إذا كان العنصر منتهي الصلاحية"""
        return time.time() > self.created_at + self.ttl
    
    def time_since_last_access(self) -> float:
        """الوقت منذ آخر وصول بالثواني"""
        return time.time() - self.last_accessed
    
    def to_dict(self) -> Dict[str, Any]:
        """تحويل العنصر إلى قاموس"""
        return {
            "key": self.key,
            "created_at": self.created_at,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count,
            "ttl": self.ttl,
            "layer": self.layer,
            "predicted_score": self.predicted_score,
            "age_seconds": time.time() - self.created_at,
            "is_expired": self.is_expired()
        }

class QueryPattern:
    """نمط استعلام مع بيانات التعلم"""
    
    def __init__(self, pattern: str):
        self.pattern = pattern
        self.count = 1
        self.last_seen = time.time()
        self.next_patterns: Dict[str, int] = defaultdict(int)
        self.avg_interval = 0.0
        self.last_intervals: List[float] = []
    
    def update(self):
        """تحديث النمط عند رؤيته"""
        now = time.time()
        interval = now - self.last_seen
        
        # تحديث متوسط الفاصل الزمني
        self.last_intervals.append(interval)
        if len(self.last_intervals) > 10:
            self.last_intervals.pop(0)
        
        if self.last_intervals:
            self.avg_interval = sum(self.last_intervals) / len(self.last_intervals)
        
        self.count += 1
        self.last_seen = now
    
    def add_next_pattern(self, next_pattern: str):
        """إضافة نمط تالي"""
        self.next_patterns[next_pattern] += 1
    
    def get_next_patterns(self, threshold: float = 0.2) -> List[Tuple[str, float]]:
        """الحصول على الأنماط التالية المحتملة مع احتمالاتها"""
        if not self.next_patterns:
            return []
        
        total = sum(self.next_patterns.values())
        patterns = [(pattern, count / total) for pattern, count in self.next_patterns.items()]
        return [p for p in patterns if p[1] >= threshold]
    
    def to_dict(self) -> Dict[str, Any]:
        """تحويل النمط إلى قاموس"""
        return {
            "pattern": self.pattern,
            "count": self.count,
            "last_seen": self.last_seen,
            "avg_interval": self.avg_interval,
            "next_patterns": dict(self.next_patterns)
        }

class LiquidCache:
    """
    نظام الذاكرة السائلة (Liquid Cache) لـ HiveDB
    
    يوفر تخزين مؤقت ذكي متعدد الطبقات يتكيف مع أنماط استخدام المستخدم.
    يستخدم خوارزميات تنبؤ لتحميل البيانات المتوقعة مسبقًا وتحسين زمن الاستجابة.
    """
    
    def __init__(self):
        self.enabled = LIQUID_CACHE_ENABLED
        self.max_size = LIQUID_CACHE_SIZE
        self.default_ttl = LIQUID_CACHE_TTL
        self.prediction_threshold = LIQUID_CACHE_PREDICTION_THRESHOLD
        self.learning_rate = LIQUID_CACHE_LEARNING_RATE
        self.num_layers = LIQUID_CACHE_LAYERS
        
        # الذاكرة المؤقتة متعددة الطبقات
        self.cache_layers: List[Dict[str, CacheItem]] = [dict() for _ in range(self.num_layers)]
        
        # تعلم أنماط الاستعلام
        self.query_patterns: Dict[str, QueryPattern] = {}
        self.last_queries: List[str] = []
        self.max_pattern_history = 100
        
        # إحصائيات
        self.hits = 0
        self.misses = 0
        self.predictions = 0
        self.successful_predictions = 0
        
        # قفل للتزامن
        self.lock = threading.RLock()
        
        # مؤقت لتنظيف الذاكرة
        self.cleanup_interval = 300  # 5 دقائق
        self.last_cleanup = time.time()
        
        # تحميل أنماط الاستعلام المحفوظة إن وجدت
        self._load_patterns()
        
        logger.info(f"تم تهيئة الذاكرة السائلة: {self.num_layers} طبقات، حجم أقصى {self.max_size}")
    
    def _generate_key(self, query_type: str, params: Dict[str, Any]) -> str:
        """توليد مفتاح فريد للاستعلام"""
        # ترتيب المعلمات للحصول على مفتاح متسق
        sorted_params = json.dumps(params, sort_keys=True)
        key = f"{query_type}:{sorted_params}"
        return hashlib.md5(key.encode()).hexdigest()
    
    def _extract_pattern(self, query_type: str, params: Dict[str, Any]) -> str:
        """استخراج نمط من الاستعلام (مبسط للمعلمات)"""
        # استخراج المعلمات الأساسية فقط للنمط
        pattern_params = {}
        for k, v in params.items():
            if k in ["cell_key", "collection", "type", "limit", "sort"]:
                pattern_params[k] = v
        
        return f"{query_type}:{json.dumps(pattern_params, sort_keys=True)}"
    
    def _update_patterns(self, pattern: str):
        """تحديث أنماط الاستعلام"""
        with self.lock:
            # إضافة أو تحديث النمط الحالي
            if pattern not in self.query_patterns:
                self.query_patterns[pattern] = QueryPattern(pattern)
            else:
                self.query_patterns[pattern].update()
            
            # تحديث العلاقات بين الأنماط
            if self.last_queries:
                last_pattern = self.last_queries[-1]
                if last_pattern in self.query_patterns:
                    self.query_patterns[last_pattern].add_next_pattern(pattern)
            
            # إضافة النمط إلى التاريخ
            self.last_queries.append(pattern)
            if len(self.last_queries) > self.max_pattern_history:
                self.last_queries.pop(0)
            
            # حفظ الأنماط كل 100 تحديث
            if sum(p.count for p in self.query_patterns.values()) % 100 == 0:
                self._save_patterns()
    
    def _predict_next_queries(self, pattern: str) -> List[Tuple[str, float]]:
        """التنبؤ بالاستعلامات التالية المحتملة"""
        if pattern not in self.query_patterns:
            return []
        
        return self.query_patterns[pattern].get_next_patterns(threshold=0.3)
    
    def _preload_predicted_queries(self, pattern: str, load_func):
        """تحميل مسبق للاستعلامات المتوقعة"""
        if not self.enabled or not load_func:
            return
        
        predictions = self._predict_next_queries(pattern)
        if not predictions:
            return
        
        self.predictions += len(predictions)
        
        # تنفيذ التحميل المسبق في خيط منفصل
        def preload_worker():
            for next_pattern, probability in predictions:
                if probability >= self.prediction_threshold:
                    try:
                        # استخراج نوع الاستعلام والمعلمات من النمط
                        parts = next_pattern.split(":", 1)
                        if len(parts) != 2:
                            continue
                        
                        query_type = parts[0]
                        try:
                            params = json.loads(parts[1])
                        except:
                            continue
                        
                        # تنفيذ الاستعلام وتخزينه مسبقًا
                        key = self._generate_key(query_type, params)
                        if not self.get(key):
                            result = load_func(query_type, params)
                            if result:
                                self.set(key, result, predicted=True)
                                self.successful_predictions += 1
                                logger.debug(f"تم التحميل المسبق للاستعلام: {next_pattern} (احتمال: {probability:.2f})")
                    except Exception as e:
                        logger.error(f"خطأ في التحميل المسبق: {e}")
        
        threading.Thread(target=preload_worker).start()
    
    def _move_between_layers(self, key: str, from_layer: int, to_layer: int):
        """نقل عنصر بين طبقات الذاكرة"""
        with self.lock:
            if key in self.cache_layers[from_layer]:
                item = self.cache_layers[from_layer].pop(key)
                item.layer = to_layer
                self.cache_layers[to_layer][key] = item
    
    def _update_item_layer(self, item: CacheItem):
        """تحديث طبقة العنصر بناءً على نمط الاستخدام"""
        current_layer = item.layer
        
        # حساب الطبقة المناسبة بناءً على عدد مرات الوصول والوقت منذ آخر وصول
        score = item.access_count / max(1, item.time_since_last_access() / 3600)
        
        # تعديل الدرجة بناءً على درجة التنبؤ
        score = score * (1 + item.predicted_score)
        
        # تحديد الطبقة المناسبة
        if score > 10:
            target_layer = 0  # أعلى طبقة (الأسرع)
        elif score > 5:
            target_layer = 1
        elif score > 1:
            target_layer = min(2, self.num_layers - 1)
        else:
            target_layer = min(3, self.num_layers - 1)  # أدنى طبقة (الأبطأ)
        
        # نقل العنصر إذا تغيرت الطبقة
        if target_layer != current_layer and target_layer < self.num_layers:
            self._move_between_layers(item.key, current_layer, target_layer)
    
    def _cleanup(self, force: bool = False):
        """تنظيف العناصر منتهية الصلاحية وإدارة حجم الذاكرة"""
        now = time.time()
        if not force and now - self.last_cleanup < self.cleanup_interval:
            return
        
        with self.lock:
            self.last_cleanup = now
            
            # إزالة العناصر منتهية الصلاحية
            for layer in range(self.num_layers):
                expired_keys = [k for k, v in self.cache_layers[layer].items() if v.is_expired()]
                for key in expired_keys:
                    del self.cache_layers[layer][key]
            
            # التحقق من حجم الذاكرة
            total_size = sum(len(layer) for layer in self.cache_layers)
            if total_size <= self.max_size:
                return
            
            # إزالة العناصر الأقل استخدامًا من الطبقات الأدنى
            items_to_remove = total_size - self.max_size
            for layer in reversed(range(self.num_layers)):  # البدء من الطبقة الأدنى
                if items_to_remove <= 0:
                    break
                
                layer_items = list(self.cache_layers[layer].items())
                # ترتيب العناصر حسب الأقل استخدامًا والأقدم
                layer_items.sort(key=lambda x: (x[1].access_count, -x[1].time_since_last_access()))
                
                # إزالة العناصر
                for i in range(min(items_to_remove, len(layer_items))):
                    del self.cache_layers[layer][layer_items[i][0]]
                    items_to_remove -= 1
    
    def _save_patterns(self):
        """حفظ أنماط الاستعلام"""
        try:
            patterns_dir = os.path.join(os.path.dirname(__file__), "patterns")
            os.makedirs(patterns_dir, exist_ok=True)
            
            patterns_file = os.path.join(patterns_dir, "query_patterns.json")
            with open(patterns_file, "w") as f:
                patterns_data = {
                    pattern: p.to_dict() 
                    for pattern, p in self.query_patterns.items()
                    if p.count >= 3  # حفظ الأنماط المتكررة فقط
                }
                json.dump(patterns_data, f)
            
            logger.debug(f"تم حفظ {len(patterns_data)} نمط استعلام")
        except Exception as e:
            logger.error(f"خطأ في حفظ أنماط الاستعلام: {e}")
    
    def _load_patterns(self):
        """تحميل أنماط الاستعلام المحفوظة"""
        try:
            patterns_file = os.path.join(os.path.dirname(__file__), "patterns", "query_patterns.json")
            if not os.path.exists(patterns_file):
                return
            
            with open(patterns_file, "r") as f:
                patterns_data = json.load(f)
            
            for pattern, data in patterns_data.items():
                p = QueryPattern(pattern)
                p.count = data["count"]
                p.last_seen = data["last_seen"]
                p.avg_interval = data["avg_interval"]
                p.next_patterns = defaultdict(int, data["next_patterns"])
                self.query_patterns[pattern] = p
            
            logger.info(f"تم تحميل {len(self.query_patterns)} نمط استعلام")
        except Exception as e:
            logger.error(f"خطأ في تحميل أنماط الاستعلام: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """الحصول على عنصر من الذاكرة المؤقتة"""
        if not self.enabled:
            return None
        
        self._cleanup()
        
        with self.lock:
            # البحث في جميع الطبقات
            for layer in range(self.num_layers):
                if key in self.cache_layers[layer]:
                    item = self.cache_layers[layer][key]
                    
                    # التحقق من انتهاء الصلاحية
                    if item.is_expired():
                        del self.cache_layers[layer][key]
                        self.misses += 1
                        return None
                    
                    # تحديث إحصائيات الوصول
                    item.access()
                    self.hits += 1
                    
                    # تحديث طبقة العنصر
                    self._update_item_layer(item)
                    
                    return item.value
            
            self.misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl: int = None, predicted: bool = False) -> None:
        """تخزين عنصر في الذاكرة المؤقتة"""
        if not self.enabled:
            return
        
        self._cleanup()
        
        with self.lock:
            # إنشاء عنصر جديد
            item = CacheItem(key, value, ttl or self.default_ttl)
            
            # تعيين درجة التنبؤ إذا كان العنصر متوقعًا
            if predicted:
                item.predicted_score = 0.8
            
            # تحديد الطبقة المناسبة للعنصر الجديد
            target_layer = 1 if predicted else min(2, self.num_layers - 1)
            item.layer = target_layer
            
            # تخزين العنصر
            self.cache_layers[target_layer][key] = item
            
            # التحقق من حجم الذاكرة
            total_size = sum(len(layer) for layer in self.cache_layers)
            if total_size > self.max_size:
                self._cleanup(force=True)
    
    def delete(self, key: str) -> bool:
        """حذف عنصر من الذاكرة المؤقتة"""
        if not self.enabled:
            return False
        
        with self.lock:
            for layer in range(self.num_layers):
                if key in self.cache_layers[layer]:
                    del self.cache_layers[layer][key]
                    return True
            
            return False
    
    def clear(self) -> None:
        """مسح جميع العناصر من الذاكرة المؤقتة"""
        with self.lock:
            for layer in range(self.num_layers):
                self.cache_layers[layer].clear()
    
    def register_query(self, query_type: str, params: Dict[str, Any], result: Any = None, load_func=None) -> str:
        """تسجيل استعلام وتحديث أنماط التعلم"""
        if not self.enabled:
            return ""
        
        # توليد مفتاح ونمط للاستعلام
        key = self._generate_key(query_type, params)
        pattern = self._extract_pattern(query_type, params)
        
        # تحديث أنماط الاستعلام
        self._update_patterns(pattern)
        
        # تخزين النتيجة إذا كانت متوفرة
        if result is not None:
            self.set(key, result)
        
        # تحميل مسبق للاستعلامات المتوقعة
        if load_func:
            self._preload_predicted_queries(pattern, load_func)
        
        return key
    
    def get_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات الذاكرة المؤقتة"""
        with self.lock:
            total_items = sum(len(layer) for layer in self.cache_layers)
            layer_stats = [len(layer) for layer in self.cache_layers]
            
            hit_rate = 0
            if self.hits + self.misses > 0:
                hit_rate = self.hits / (self.hits + self.misses)
            
            prediction_rate = 0
            if self.predictions > 0:
                prediction_rate = self.successful_predictions / self.predictions
            
            return {
                "enabled": self.enabled,
                "total_items": total_items,
                "max_size": self.max_size,
                "layer_stats": layer_stats,
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": hit_rate,
                "predictions": self.predictions,
                "successful_predictions": self.successful_predictions,
                "prediction_rate": prediction_rate,
                "patterns_count": len(self.query_patterns),
                "last_cleanup": self.last_cleanup
            }
    
    def get_hot_patterns(self, limit: int = 10) -> List[Dict[str, Any]]:
        """الحصول على أكثر أنماط الاستعلام استخدامًا"""
        with self.lock:
            patterns = list(self.query_patterns.values())
            patterns.sort(key=lambda p: p.count, reverse=True)
            
            return [p.to_dict() for p in patterns[:limit]]

# إنشاء نسخة واحدة من الذاكرة السائلة
liquid_cache = LiquidCache()
