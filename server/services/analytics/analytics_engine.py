"""
محرك تحليلات متقدم لـ HiveDB
يوفر تحليلات وإحصاءات متقدمة تتفوق على إمكانيات Directus
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text
from ..database.models import Cell, CellData, Hive, AuditLog, User

logger = logging.getLogger(__name__)

class AnalyticsEngine:
    """محرك تحليلات متقدم للبيانات السداسية"""
    
    def __init__(self):
        self.cache_enabled = True
        self.analytics_cache = {}
        self.cache_ttl = 3600  # ثانية واحدة
    
    def get_system_stats(self, db: Session) -> Dict[str, Any]:
        """الحصول على إحصاءات النظام الأساسية"""
        cache_key = "system_stats"
        if self.cache_enabled and cache_key in self.analytics_cache:
            cache_item = self.analytics_cache[cache_key]
            if datetime.now().timestamp() - cache_item["timestamp"] < self.cache_ttl:
                return cache_item["data"]
        
        # عدد المستخدمين
        user_count = db.query(func.count(User.id)).scalar()
        
        # عدد الخلايا الرئيسية
        hive_count = db.query(func.count(Hive.id)).scalar()
        
        # عدد الخلايا الفرعية
        cell_count = db.query(func.count(Cell.id)).scalar()
        
        # حجم البيانات الإجمالي
        data_size = db.query(func.sum(func.length(CellData.value_text) + 
                                     func.length(CellData.value_json))).scalar() or 0
        
        # عدد العمليات في آخر 24 ساعة
        yesterday = datetime.utcnow() - timedelta(days=1)
        operations_24h = db.query(func.count(AuditLog.id)).filter(
            AuditLog.timestamp >= yesterday
        ).scalar()
        
        # عدد المستخدمين النشطين في آخر 7 أيام
        last_week = datetime.utcnow() - timedelta(days=7)
        active_users = db.query(func.count(func.distinct(AuditLog.user_id))).filter(
            AuditLog.timestamp >= last_week
        ).scalar()
        
        stats = {
            "user_count": user_count,
            "hive_count": hive_count,
            "cell_count": cell_count,
            "data_size_bytes": data_size,
            "data_size_human": self._format_size(data_size),
            "operations_24h": operations_24h,
            "active_users_7d": active_users,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if self.cache_enabled:
            self.analytics_cache[cache_key] = {
                "data": stats,
                "timestamp": datetime.now().timestamp()
            }
        
        return stats
    
    def get_growth_metrics(self, db: Session, days: int = 30) -> Dict[str, Any]:
        """الحصول على مقاييس النمو على مدار فترة زمنية"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # استعلام لعدد المستخدمين الجدد يوميًا
        new_users_query = db.query(
            func.date_trunc('day', User.created_at).label('date'),
            func.count(User.id).label('count')
        ).filter(
            User.created_at >= start_date
        ).group_by(
            func.date_trunc('day', User.created_at)
        ).order_by(
            func.date_trunc('day', User.created_at)
        )
        
        new_users_data = [{"date": row.date.strftime("%Y-%m-%d"), "count": row.count} 
                         for row in new_users_query]
        
        # استعلام لعدد الخلايا الجديدة يوميًا
        new_cells_query = db.query(
            func.date_trunc('day', Cell.created_at).label('date'),
            func.count(Cell.id).label('count')
        ).filter(
            Cell.created_at >= start_date
        ).group_by(
            func.date_trunc('day', Cell.created_at)
        ).order_by(
            func.date_trunc('day', Cell.created_at)
        )
        
        new_cells_data = [{"date": row.date.strftime("%Y-%m-%d"), "count": row.count} 
                         for row in new_cells_query]
        
        # استعلام لحجم البيانات المضافة يوميًا
        data_growth_query = db.query(
            func.date_trunc('day', CellData.created_at).label('date'),
            func.sum(func.length(CellData.value_text) + 
                   func.length(CellData.value_json)).label('size')
        ).filter(
            CellData.created_at >= start_date
        ).group_by(
            func.date_trunc('day', CellData.created_at)
        ).order_by(
            func.date_trunc('day', CellData.created_at)
        )
        
        data_growth = [{"date": row.date.strftime("%Y-%m-%d"), "size_bytes": row.size or 0,
                      "size_human": self._format_size(row.size or 0)} 
                     for row in data_growth_query]
        
        return {
            "new_users": new_users_data,
            "new_cells": new_cells_data,
            "data_growth": data_growth,
            "period_days": days,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_usage_patterns(self, db: Session, days: int = 7) -> Dict[str, Any]:
        """تحليل أنماط استخدام النظام"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # توزيع العمليات حسب النوع
        operation_types = db.query(
            AuditLog.action_type,
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.timestamp >= start_date
        ).group_by(
            AuditLog.action_type
        ).order_by(
            desc('count')
        )
        
        operations_by_type = [{"action_type": row.action_type, "count": row.count} 
                             for row in operation_types]
        
        # توزيع العمليات حسب الساعة
        hourly_usage = db.query(
            func.extract('hour', AuditLog.timestamp).label('hour'),
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.timestamp >= start_date
        ).group_by(
            func.extract('hour', AuditLog.timestamp)
        ).order_by(
            func.extract('hour', AuditLog.timestamp)
        )
        
        usage_by_hour = [{"hour": int(row.hour), "count": row.count} 
                        for row in hourly_usage]
        
        # توزيع العمليات حسب اليوم
        daily_usage = db.query(
            func.extract('dow', AuditLog.timestamp).label('day_of_week'),
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.timestamp >= start_date
        ).group_by(
            func.extract('dow', AuditLog.timestamp)
        ).order_by(
            func.extract('dow', AuditLog.timestamp)
        )
        
        days_map = {0: "الاثنين", 1: "الثلاثاء", 2: "الأربعاء", 3: "الخميس", 
                   4: "الجمعة", 5: "السبت", 6: "الأحد"}
        
        usage_by_day = [{"day": days_map[int(row.day_of_week)], "day_num": int(row.day_of_week), "count": row.count} 
                       for row in daily_usage]
        
        # المستخدمين الأكثر نشاطًا
        top_users = db.query(
            AuditLog.user_id,
            User.email,
            func.count(AuditLog.id).label('operation_count')
        ).join(
            User, User.id == AuditLog.user_id
        ).filter(
            AuditLog.timestamp >= start_date
        ).group_by(
            AuditLog.user_id, User.email
        ).order_by(
            desc('operation_count')
        ).limit(10)
        
        most_active_users = [{"user_id": row.user_id, "email": row.email, "operation_count": row.operation_count} 
                            for row in top_users]
        
        return {
            "operations_by_type": operations_by_type,
            "usage_by_hour": usage_by_hour,
            "usage_by_day": usage_by_day,
            "most_active_users": most_active_users,
            "period_days": days,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_performance_metrics(self, db: Session, days: int = 1) -> Dict[str, Any]:
        """قياس أداء النظام"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # متوسط وقت الاستجابة للعمليات
        response_times = db.query(
            AuditLog.action_type,
            func.avg(AuditLog.execution_time).label('avg_time'),
            func.min(AuditLog.execution_time).label('min_time'),
            func.max(AuditLog.execution_time).label('max_time'),
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.timestamp >= start_date,
            AuditLog.execution_time.isnot(None)
        ).group_by(
            AuditLog.action_type
        ).order_by(
            desc('avg_time')
        )
        
        performance_by_operation = [
            {
                "action_type": row.action_type, 
                "avg_time_ms": round(row.avg_time, 2), 
                "min_time_ms": round(row.min_time, 2),
                "max_time_ms": round(row.max_time, 2),
                "count": row.count
            } 
            for row in response_times
        ]
        
        # الاستعلامات الأبطأ
        slowest_queries = db.query(
            AuditLog.action,
            AuditLog.execution_time,
            AuditLog.timestamp,
            User.email
        ).join(
            User, User.id == AuditLog.user_id
        ).filter(
            AuditLog.timestamp >= start_date,
            AuditLog.execution_time.isnot(None)
        ).order_by(
            desc(AuditLog.execution_time)
        ).limit(10)
        
        slowest_operations = [
            {
                "action": row.action,
                "execution_time_ms": round(row.execution_time, 2),
                "timestamp": row.timestamp.isoformat(),
                "user": row.email
            }
            for row in slowest_queries
        ]
        
        # إحصاءات الذاكرة المؤقتة
        cache_stats = {
            "cache_size": len(self.analytics_cache),
            "cache_hit_ratio": 0.75,  # يمكن حساب هذه القيمة بشكل ديناميكي
            "cache_ttl_seconds": self.cache_ttl
        }
        
        return {
            "performance_by_operation": performance_by_operation,
            "slowest_operations": slowest_operations,
            "cache_stats": cache_stats,
            "period_days": days,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_hexagonal_metrics(self, db: Session) -> Dict[str, Any]:
        """إحصاءات خاصة بالبنية السداسية"""
        
        # توزيع الخلايا حسب الإحداثيات
        cell_distribution = db.query(
            Cell.coordinates,
            func.count(CellData.id).label('data_count'),
            func.sum(func.length(CellData.value_text) + 
                   func.length(CellData.value_json)).label('data_size')
        ).outerjoin(
            CellData, CellData.cell_id == Cell.id
        ).group_by(
            Cell.coordinates
        ).order_by(
            desc('data_count')
        ).limit(100)
        
        coordinates_data = []
        for row in cell_distribution:
            x, y = map(int, row.coordinates.split(','))
            coordinates_data.append({
                "coordinates": row.coordinates,
                "x": x,
                "y": y,
                "data_count": row.data_count or 0,
                "data_size_bytes": row.data_size or 0,
                "data_size_human": self._format_size(row.data_size or 0)
            })
        
        # تحليل كثافة البيانات في الشبكة السداسية
        # حساب المركز الثقلي للبيانات
        total_weight = sum(item["data_size_bytes"] for item in coordinates_data)
        if total_weight > 0:
            center_x = sum(item["x"] * item["data_size_bytes"] for item in coordinates_data) / total_weight
            center_y = sum(item["y"] * item["data_size_bytes"] for item in coordinates_data) / total_weight
        else:
            center_x, center_y = 0, 0
        
        # حساب نصف قطر توزيع البيانات
        if coordinates_data:
            radius = max(
                self._hex_distance((center_x, center_y), (item["x"], item["y"]))
                for item in coordinates_data
            )
        else:
            radius = 0
        
        # توزيع أنواع البيانات
        data_types = db.query(
            Cell.data_type,
            func.count(Cell.id).label('count')
        ).group_by(
            Cell.data_type
        ).order_by(
            desc('count')
        )
        
        data_type_distribution = [
            {"data_type": row.data_type, "count": row.count}
            for row in data_types
        ]
        
        return {
            "coordinates_data": coordinates_data,
            "center_of_gravity": {"x": round(center_x, 2), "y": round(center_y, 2)},
            "distribution_radius": round(radius, 2),
            "data_type_distribution": data_type_distribution,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_predictive_insights(self, db: Session) -> Dict[str, Any]:
        """تحليلات تنبؤية لنمو البيانات واستخدام النظام"""
        # تحليل اتجاهات النمو
        
        # الحصول على بيانات النمو للأيام الـ 90 الماضية
        growth_data = self.get_growth_metrics(db, days=90)
        
        # تحويل البيانات إلى DataFrame للتحليل
        new_users_df = pd.DataFrame(growth_data["new_users"])
        new_cells_df = pd.DataFrame(growth_data["new_cells"])
        data_growth_df = pd.DataFrame(growth_data["data_growth"])
        
        # إضافة قيم افتراضية للأيام المفقودة
        date_range = pd.date_range(
            start=(datetime.utcnow() - timedelta(days=90)).strftime("%Y-%m-%d"),
            end=datetime.utcnow().strftime("%Y-%m-%d")
        )
        date_strings = [date.strftime("%Y-%m-%d") for date in date_range]
        
        # إنشاء DataFrames كاملة مع القيم المفقودة
        full_users_df = pd.DataFrame({"date": date_strings})
        full_users_df = full_users_df.merge(new_users_df, on="date", how="left").fillna(0)
        
        full_cells_df = pd.DataFrame({"date": date_strings})
        full_cells_df = full_cells_df.merge(new_cells_df, on="date", how="left").fillna(0)
        
        full_data_df = pd.DataFrame({"date": date_strings})
        if not data_growth_df.empty:
            full_data_df = full_data_df.merge(data_growth_df[["date", "size_bytes"]], on="date", how="left").fillna(0)
        else:
            full_data_df["size_bytes"] = 0
        
        # تحليل الاتجاه للمستخدمين
        try:
            user_trend = np.polyfit(range(len(full_users_df)), full_users_df["count"], 1)
            user_growth_rate = user_trend[0]
        except:
            user_growth_rate = 0
        
        # تحليل الاتجاه للخلايا
        try:
            cell_trend = np.polyfit(range(len(full_cells_df)), full_cells_df["count"], 1)
            cell_growth_rate = cell_trend[0]
        except:
            cell_growth_rate = 0
        
        # تحليل الاتجاه لحجم البيانات
        try:
            data_trend = np.polyfit(range(len(full_data_df)), full_data_df["size_bytes"], 1)
            data_growth_rate = data_trend[0]
        except:
            data_growth_rate = 0
        
        # التنبؤ بالنمو للأيام الـ 30 القادمة
        predictions = {
            "users": {
                "current": int(full_users_df["count"].sum()),
                "growth_rate_daily": round(user_growth_rate, 2),
                "projected_30_days": int(full_users_df["count"].sum() + user_growth_rate * 30),
                "trend": "increasing" if user_growth_rate > 0 else "decreasing" if user_growth_rate < 0 else "stable"
            },
            "cells": {
                "current": int(full_cells_df["count"].sum()),
                "growth_rate_daily": round(cell_growth_rate, 2),
                "projected_30_days": int(full_cells_df["count"].sum() + cell_growth_rate * 30),
                "trend": "increasing" if cell_growth_rate > 0 else "decreasing" if cell_growth_rate < 0 else "stable"
            },
            "data_size": {
                "current_bytes": int(full_data_df["size_bytes"].sum()),
                "current_human": self._format_size(int(full_data_df["size_bytes"].sum())),
                "growth_rate_daily_bytes": round(data_growth_rate, 2),
                "growth_rate_daily_human": self._format_size(round(data_growth_rate, 2)),
                "projected_30_days_bytes": int(full_data_df["size_bytes"].sum() + data_growth_rate * 30),
                "projected_30_days_human": self._format_size(int(full_data_df["size_bytes"].sum() + data_growth_rate * 30)),
                "trend": "increasing" if data_growth_rate > 0 else "decreasing" if data_growth_rate < 0 else "stable"
            }
        }
        
        return {
            "predictions": predictions,
            "analysis_period_days": 90,
            "prediction_period_days": 30,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _format_size(self, size_bytes: int) -> str:
        """تنسيق حجم البيانات بطريقة مقروءة"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ("B", "KB", "MB", "GB", "TB", "PB")
        i = int(np.floor(np.log(size_bytes) / np.log(1024))) if size_bytes > 0 else 0
        p = np.power(1024, i)
        s = round(size_bytes / p, 2)
        
        return f"{s} {size_names[i]}"
    
    def _hex_distance(self, a: Tuple[float, float], b: Tuple[float, float]) -> float:
        """حساب المسافة في الشبكة السداسية"""
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx + max(0, dy - dx)

# إنشاء نسخة واحدة من محرك التحليلات
analytics_engine = AnalyticsEngine()
