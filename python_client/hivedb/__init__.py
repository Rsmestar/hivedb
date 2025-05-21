"""
HiveDB - نظام قواعد بيانات ثوري مستوحى من خلية النحل
مكتبة Python الرسمية للتفاعل مع نظام HiveDB
"""

from .client import connect, Cell
from .utils import encrypt, decrypt, generate_cell_key

__version__ = "0.1.0"
__all__ = ["connect", "Cell", "encrypt", "decrypt", "generate_cell_key"]
