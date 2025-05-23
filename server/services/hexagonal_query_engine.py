"""
محرك استعلام سداسي متقدم لـ HiveDB
يوفر استعلامات متخصصة للبنية السداسية تتفوق على استعلامات SQL التقليدية في Directus
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
import json
from sqlalchemy.orm import Session
from .database.models import Cell, CellData, Hive

logger = logging.getLogger(__name__)

class HexagonalQueryEngine:
    """محرك استعلام متخصص للبنية السداسية"""
    
    def __init__(self):
        self.directions = ["north", "northeast", "southeast", "south", "southwest", "northwest"]
        self.cache_enabled = True
        self.query_cache = {}
    
    def get_neighbors(self, db: Session, cell_id: str, depth: int = 1) -> List[Dict[str, Any]]:
        """الحصول على الخلايا المجاورة بعمق محدد"""
        cell = db.query(Cell).filter(Cell.cell_id == cell_id).first()
        if not cell:
            return []
            
        # استخراج الإحداثيات
        x, y = map(int, cell.coordinates.split(","))
        
        neighbors = []
        visited = set()
        self._get_neighbors_recursive(db, x, y, depth, neighbors, visited)
        
        return neighbors
    
    def _get_neighbors_recursive(self, db: Session, x: int, y: int, depth: int, 
                                result: List[Dict[str, Any]], visited: set, current_depth: int = 0):
        """استرجاع الخلايا المجاورة بشكل متكرر"""
        if current_depth > depth or f"{x},{y}" in visited:
            return
            
        visited.add(f"{x},{y}")
        
        # الحصول على الخلية الحالية
        cell = db.query(Cell).filter(Cell.coordinates == f"{x},{y}").first()
        if cell:
            # إضافة بيانات الخلية إلى النتائج
            cell_data = db.query(CellData).filter(CellData.cell_id == cell.id).all()
            data_dict = {}
            for data in cell_data:
                if data.value_json:
                    data_dict[data.key] = data.value_json
                else:
                    data_dict[data.key] = data.value_text
                    
            result.append({
                "cell_id": cell.cell_id,
                "coordinates": cell.coordinates,
                "data_type": cell.data_type,
                "data": data_dict,
                "depth": current_depth
            })
        
        # الحصول على الجيران
        if current_depth < depth:
            # إحداثيات الجيران في النظام السداسي
            neighbor_coords = [
                (x, y-1),      # شمال
                (x+1, y-1),    # شمال شرق
                (x+1, y),      # جنوب شرق
                (x, y+1),      # جنوب
                (x-1, y+1),    # جنوب غرب
                (x-1, y)       # شمال غرب
            ]
            
            for nx, ny in neighbor_coords:
                self._get_neighbors_recursive(db, nx, ny, depth, result, visited, current_depth + 1)
    
    def path_query(self, db: Session, start_cell_id: str, end_cell_id: str) -> List[Dict[str, Any]]:
        """البحث عن أقصر مسار بين خليتين"""
        start_cell = db.query(Cell).filter(Cell.cell_id == start_cell_id).first()
        end_cell = db.query(Cell).filter(Cell.cell_id == end_cell_id).first()
        
        if not start_cell or not end_cell:
            return []
            
        # استخراج الإحداثيات
        start_x, start_y = map(int, start_cell.coordinates.split(","))
        end_x, end_y = map(int, end_cell.coordinates.split(","))
        
        # استخدام خوارزمية A* للبحث عن المسار
        path = self._a_star_search(db, (start_x, start_y), (end_x, end_y))
        
        # تحويل المسار إلى قائمة من الخلايا
        result = []
        for i, (x, y) in enumerate(path):
            cell = db.query(Cell).filter(Cell.coordinates == f"{x},{y}").first()
            if cell:
                cell_data = db.query(CellData).filter(CellData.cell_id == cell.id).all()
                data_dict = {}
                for data in cell_data:
                    if data.value_json:
                        data_dict[data.key] = data.value_json
                    else:
                        data_dict[data.key] = data.value_text
                        
                result.append({
                    "cell_id": cell.cell_id,
                    "coordinates": cell.coordinates,
                    "data_type": cell.data_type,
                    "data": data_dict,
                    "step": i
                })
        
        return result
    
    def _a_star_search(self, db: Session, start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """خوارزمية A* للبحث عن أقصر مسار في الشبكة السداسية"""
        import heapq
        
        # دالة تقدير المسافة (heuristic) للشبكة السداسية
        def hex_distance(a, b):
            # مسافة مانهاتن المعدلة للشبكة السداسية
            dx = abs(a[0] - b[0])
            dy = abs(a[1] - b[1])
            return dx + max(0, dy - dx)
        
        # قائمة الأولوية للخلايا التي سيتم استكشافها
        open_set = []
        heapq.heappush(open_set, (0, start))
        
        # الخلايا التي تم زيارتها
        came_from = {}
        
        # تكلفة الوصول إلى كل خلية
        g_score = {start: 0}
        
        # التقدير الكلي للمسافة
        f_score = {start: hex_distance(start, end)}
        
        while open_set:
            # الحصول على الخلية ذات الأولوية الأعلى
            current_f, current = heapq.heappop(open_set)
            
            # إذا وصلنا إلى الهدف
            if current == end:
                # إعادة بناء المسار
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                return path[::-1]
            
            # إحداثيات الجيران
            neighbors = [
                (current[0], current[1]-1),      # شمال
                (current[0]+1, current[1]-1),    # شمال شرق
                (current[0]+1, current[1]),      # جنوب شرق
                (current[0], current[1]+1),      # جنوب
                (current[0]-1, current[1]+1),    # جنوب غرب
                (current[0]-1, current[1])       # شمال غرب
            ]
            
            for neighbor in neighbors:
                # التحقق من وجود خلية في هذه الإحداثيات
                cell = db.query(Cell).filter(Cell.coordinates == f"{neighbor[0]},{neighbor[1]}").first()
                if not cell:
                    continue
                
                # حساب التكلفة
                tentative_g = g_score.get(current, float('inf')) + 1
                
                if tentative_g < g_score.get(neighbor, float('inf')):
                    # هذا مسار أفضل
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + hex_distance(neighbor, end)
                    
                    # إضافة الجار إلى قائمة الاستكشاف
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        # لم يتم العثور على مسار
        return []
    
    def pattern_query(self, db: Session, pattern: Dict[str, Any]) -> List[Dict[str, Any]]:
        """البحث عن أنماط محددة في الشبكة السداسية"""
        # مثال للنمط: {"center": {"type": "user"}, "neighbors": [{"direction": "north", "type": "document"}]}
        
        # البحث عن الخلايا المطابقة للنمط المركزي
        center_cells = self._find_matching_cells(db, pattern.get("center", {}))
        
        results = []
        for cell in center_cells:
            # التحقق من الجيران
            if "neighbors" in pattern:
                if self._check_neighbors(db, cell, pattern["neighbors"]):
                    results.append(self._cell_to_dict(db, cell))
            else:
                results.append(self._cell_to_dict(db, cell))
        
        return results
    
    def _find_matching_cells(self, db: Session, criteria: Dict[str, Any]) -> List[Cell]:
        """البحث عن الخلايا المطابقة للمعايير"""
        query = db.query(Cell)
        
        for key, value in criteria.items():
            if key == "type":
                query = query.filter(Cell.data_type == value)
            elif key == "data":
                # البحث في بيانات الخلية
                for data_key, data_value in value.items():
                    subquery = db.query(CellData.cell_id).filter(
                        CellData.key == data_key
                    )
                    
                    if isinstance(data_value, dict):
                        # معايير متقدمة
                        if "contains" in data_value:
                            subquery = subquery.filter(
                                CellData.value_text.like(f"%{data_value['contains']}%")
                            )
                        elif "gt" in data_value:
                            subquery = subquery.filter(
                                CellData.value_text > str(data_value['gt'])
                            )
                        # يمكن إضافة المزيد من المعايير هنا
                    else:
                        # مطابقة مباشرة
                        subquery = subquery.filter(
                            (CellData.value_text == str(data_value)) | 
                            (CellData.value_json.cast(str) == json.dumps(data_value))
                        )
                    
                    query = query.filter(Cell.id.in_(subquery))
        
        return query.all()
    
    def _check_neighbors(self, db: Session, cell: Cell, neighbor_criteria: List[Dict[str, Any]]) -> bool:
        """التحقق من مطابقة الجيران للمعايير"""
        x, y = map(int, cell.coordinates.split(","))
        
        for criteria in neighbor_criteria:
            direction = criteria.get("direction")
            if direction not in self.directions:
                continue
                
            # الحصول على إحداثيات الجار
            nx, ny = self._get_neighbor_coordinates(x, y, direction)
            
            # البحث عن الخلية المجاورة
            neighbor = db.query(Cell).filter(Cell.coordinates == f"{nx},{ny}").first()
            if not neighbor:
                return False
                
            # التحقق من المعايير
            del criteria["direction"]
            matching_cells = self._find_matching_cells(db, criteria)
            
            if neighbor not in matching_cells:
                return False
        
        return True
    
    def _get_neighbor_coordinates(self, x: int, y: int, direction: str) -> Tuple[int, int]:
        """الحصول على إحداثيات الجار في اتجاه محدد"""
        if direction == "north":
            return (x, y-1)
        elif direction == "northeast":
            return (x+1, y-1)
        elif direction == "southeast":
            return (x+1, y)
        elif direction == "south":
            return (x, y+1)
        elif direction == "southwest":
            return (x-1, y+1)
        elif direction == "northwest":
            return (x-1, y)
        else:
            return (x, y)
    
    def _cell_to_dict(self, db: Session, cell: Cell) -> Dict[str, Any]:
        """تحويل كائن الخلية إلى قاموس"""
        cell_data = db.query(CellData).filter(CellData.cell_id == cell.id).all()
        data_dict = {}
        for data in cell_data:
            if data.value_json:
                data_dict[data.key] = data.value_json
            else:
                data_dict[data.key] = data.value_text
                
        return {
            "cell_id": cell.cell_id,
            "coordinates": cell.coordinates,
            "data_type": cell.data_type,
            "data": data_dict
        }

# إنشاء نسخة واحدة من محرك الاستعلام
hexagonal_query_engine = HexagonalQueryEngine()
