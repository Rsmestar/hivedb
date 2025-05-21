"""
خادم HiveDB الرئيسي المحسن
يوفر واجهة برمجة التطبيقات (API) للتفاعل مع نظام HiveDB مع ميزات متقدمة
"""

import os
import logging
import asyncio
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from prometheus_fastapi_instrumentator import Instrumentator

# Import services
from services.database import get_db, Base, engine
from services.auth.models import User, UserCreate, UserLogin, UserResponse, Token
from services.auth.models import Cell, CellCreate, CellResponse, CellOwnership
from services.auth.auth import (
    get_password_hash, verify_password, authenticate_user,
    create_access_token, get_current_user, get_current_active_user, get_current_admin_user
)
from services.kafka.producer import kafka_producer
from services.kafka.consumer import kafka_consumer
from services.sgx.enclave import sgx_enclave
from services.query_optimizer.optimizer import query_optimizer
from services.liquid_cache.liquid_cache import liquid_cache

# Additional models for SGX secure operations
class SecureDataRequest(BaseModel):
    data: Dict[str, any] = Field(..., description="البيانات المراد تشفيرها أو التحقق منها")
    data_id: Optional[str] = Field(None, description="معرف البيانات الاختياري للتشفير")

class SecureComputeRequest(BaseModel):
    operation: str = Field(..., description="العملية المراد تنفيذها على البيانات المشفرة")
    encrypted_data: Dict[str, str] = Field(..., description="البيانات المشفرة")
    params: Optional[Dict[str, any]] = Field({}, description="معلمات العملية")

class SecureVerifyRequest(BaseModel):
    data: Dict[str, any] = Field(..., description="البيانات المراد التحقق منها")
    hash_value: str = Field(..., description="قيمة التجزئة المتوقعة")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("hivedb")

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="HiveDB API",
    description="واجهة برمجة التطبيقات لنظام قواعد بيانات HiveDB المستوحى من خلية النحل مع ميزات متقدمة",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Ensure storage directories exist
CELLS_DIR = "cells"
os.makedirs(CELLS_DIR, exist_ok=True)

# Data models for API
class CellDataItem(BaseModel):
    key: str
    value: str

class CellDataResponse(BaseModel):
    key: str
    value: str

class KeysResponse(BaseModel):
    keys: List[str]

class QueryRequest(BaseModel):
    filter: Optional[Dict] = None
    sort: Optional[List[str]] = None
    limit: Optional[int] = None

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting HiveDB server...")
    
    # Initialize Kafka producer
    await kafka_producer.start()
    
    # Initialize Kafka consumer for audit logs
    await kafka_consumer.start(["hivedb-audit"])
    
    # Initialize SGX enclave if enabled
    if os.getenv("SGX_ENABLED", "False").lower() in ("true", "1", "t"):
        if sgx_enclave.initialize():
            logger.info("Intel SGX enclave initialized successfully")
        else:
            logger.warning("Failed to initialize Intel SGX enclave, falling back to standard security")
    
    # Initialize query optimizer
    await query_optimizer.initialize()
    
    # Store start time for uptime tracking
    app.state.start_time = datetime.utcnow()
    
    # Log initialization status
    logger.info(f"HiveDB server started successfully with features: SGX={sgx_enclave.is_initialized}, LiquidCache={liquid_cache.enabled}")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    logger.info("Shutting down HiveDB server...")
    
    # Stop Kafka producer
    await kafka_producer.stop()
    
    # Stop Kafka consumer
    await kafka_consumer.stop()
    
    # Destroy SGX enclave
    sgx_enclave.destroy()
    
    # Shutdown query optimizer
    await query_optimizer.shutdown()
    
    # Save liquid cache patterns
    logger.info(f"Saving liquid cache patterns: {len(liquid_cache.query_patterns)} patterns")
    liquid_cache._save_patterns()
    
    logger.info("HiveDB server shutdown complete")

# Authentication endpoints
@app.post("/auth/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="البريد الإلكتروني مسجل بالفعل"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Send event to Kafka
    await kafka_producer.send_user_event(
        db_user.id,
        "user_registered",
        {"email": db_user.email, "username": db_user.username}
    )
    
    # Send audit log
    await kafka_producer.send_audit_event(
        str(db_user.id),
        "register",
        "user",
        {"email": db_user.email}
    )
    
    return db_user

@app.post("/auth/login", response_model=Token)
async def login_for_access_token(form_data: UserLogin, db: Session = Depends(get_db)):
    """Login and get access token"""
    user = authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="بريد إلكتروني أو كلمة مرور غير صحيحة",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    # Send audit log
    await kafka_producer.send_audit_event(
        str(user.id),
        "login",
        "user",
        {"email": user.email}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin
    }

# Cell management endpoints
@app.post("/cells", response_model=CellResponse)
async def create_cell(
    cell_data: CellCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new cell"""
    # Generate a unique cell key
    import uuid
    cell_key = f"cell{str(uuid.uuid4().int)[:10]}"
    
    # Hash the password
    password_hash = get_password_hash(cell_data.password)
    
    # Create cell in database
    db_cell = Cell(
        key=cell_key,
        password_hash=password_hash
    )
    
    db.add(db_cell)
    db.commit()
    db.refresh(db_cell)
    
    # Create ownership record
    cell_ownership = CellOwnership(
        user_id=current_user.id,
        cell_id=db_cell.id,
        permission_level="owner"
    )
    
    db.add(cell_ownership)
    db.commit()
    
    # Create cell directory and database
    cell_path = os.path.join(CELLS_DIR, f"{cell_key}")
    os.makedirs(cell_path, exist_ok=True)
    
    # Initialize cell storage
    import sqlite3
    db_file = os.path.join(cell_path, "data.db")
    conn = sqlite3.connect(db_file)
    conn.execute('CREATE TABLE IF NOT EXISTS data (key TEXT PRIMARY KEY, value TEXT, created_at TEXT, updated_at TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT)')
    conn.execute('INSERT INTO metadata (key, value) VALUES (?, ?)', ('created_at', datetime.now().isoformat()))
    conn.execute('INSERT INTO metadata (key, value) VALUES (?, ?)', ('owner_id', str(current_user.id)))
    conn.commit()
    conn.close()
    
    # Send event to Kafka
    await kafka_producer.send_cell_event(
        cell_key,
        "cell_created",
        {"owner_id": current_user.id}
    )
    
    # Send audit log
    await kafka_producer.send_audit_event(
        str(current_user.id),
        "create",
        f"cell/{cell_key}",
        {"cell_key": cell_key}
    )
    
    return db_cell

@app.get("/cells", response_model=List[CellResponse])
async def get_user_cells(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all cells owned by the current user"""
    # Get all cells owned by the user
    cell_ownerships = db.query(CellOwnership).filter(CellOwnership.user_id == current_user.id).all()
    cell_ids = [ownership.cell_id for ownership in cell_ownerships]
    
    cells = db.query(Cell).filter(Cell.id.in_(cell_ids)).all()
    
    return cells

@app.get("/cells/{cell_key}", response_model=CellResponse)
async def get_cell(
    cell_key: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get cell details"""
    # Get cell
    cell = db.query(Cell).filter(Cell.key == cell_key).first()
    if not cell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الخلية غير موجودة"
        )
    
    # Check if user has access to the cell
    ownership = db.query(CellOwnership).filter(
        CellOwnership.cell_id == cell.id,
        CellOwnership.user_id == current_user.id
    ).first()
    
    if not ownership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ليس لديك حق الوصول إلى هذه الخلية"
        )
    
    return cell

# Cell data endpoints
@app.get("/cells/{cell_key}/keys", response_model=KeysResponse)
async def get_cell_keys(
    cell_key: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all keys in a cell"""
    # Verify cell access
    cell = db.query(Cell).filter(Cell.key == cell_key).first()
    if not cell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الخلية غير موجودة"
        )
    
    ownership = db.query(CellOwnership).filter(
        CellOwnership.cell_id == cell.id,
        CellOwnership.user_id == current_user.id
    ).first()
    
    if not ownership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ليس لديك حق الوصول إلى هذه الخلية"
        )
    
    # Get keys from cell database
    import sqlite3
    cell_path = os.path.join(CELLS_DIR, f"{cell_key}")
    db_file = os.path.join(cell_path, "data.db")
    
    conn = sqlite3.connect(db_file)
    cursor = conn.execute('SELECT key FROM data')
    keys = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return {"keys": keys}

@app.post("/cells/{cell_key}/data", status_code=status.HTTP_200_OK)
async def store_cell_data(
    cell_key: str,
    data_item: CellDataItem,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Store data in a cell"""
    # Verify cell access
    cell = db.query(Cell).filter(Cell.key == cell_key).first()
    if not cell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الخلية غير موجودة"
        )
    
    ownership = db.query(CellOwnership).filter(
        CellOwnership.cell_id == cell.id,
        CellOwnership.user_id == current_user.id
    ).first()
    
    if not ownership or ownership.permission_level not in ["owner", "editor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ليس لديك حق الكتابة في هذه الخلية"
        )
    
    # Store data in cell database
    import sqlite3
    cell_path = os.path.join(CELLS_DIR, f"{cell_key}")
    os.makedirs(cell_path, exist_ok=True)
    db_file = os.path.join(cell_path, "data.db")
    
    # Create table if not exists
    conn = sqlite3.connect(db_file)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS data (
            key TEXT PRIMARY KEY,
            value TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    
    # Check if key exists
    cursor = conn.execute('SELECT key FROM data WHERE key = ?', (data_item.key,))
    exists = cursor.fetchone() is not None
    
    # Check if we should encrypt the data using SGX
    value_to_store = data_item.value
    is_encrypted = False
    
    if sgx_enclave.is_initialized:
        # استخدام معرف الخلية كمعرف للبيانات للمساعدة في اشتقاق المفتاح
        data_id = f"{cell_key}:{data_item.key}"
        encrypted_data = sgx_enclave.encrypt_data({"value": data_item.value}, data_id)
        is_encrypted = True
        value_to_store = encrypted_data
    
    # Insert or update data
    now = datetime.utcnow().isoformat()
    if exists:
        conn.execute(
            'UPDATE data SET value = ?, updated_at = ? WHERE key = ?',
            (value_to_store, now, data_item.key)
        )
    else:
        conn.execute(
            'INSERT INTO data (key, value, created_at, updated_at) VALUES (?, ?, ?, ?)',
            (data_item.key, value_to_store, now, now)
        )
    
    conn.commit()
    conn.close()
    
    # Invalidate cache entries related to this cell
    cache_keys_to_invalidate = liquid_cache.find_related_keys(f"cell_{cell_key}")
    for cache_key in cache_keys_to_invalidate:
        liquid_cache.invalidate(cache_key)
    
    # Also invalidate any specific key for this data
    specific_key = liquid_cache._generate_key("cell_data", {
        "cell_key": cell_key,
        "data_key": data_item.key,
        "user_id": str(current_user.id)
    })
    liquid_cache.invalidate(specific_key)
    
    # Send event to Kafka
    await kafka_producer.send_cell_event(
        cell_key,
        "data_stored",
        {"key": data_item.key, "encrypted": is_encrypted}
    )
    
    # Send audit log
    await kafka_producer.send_audit_event(
        str(current_user.id),
        "store",
        f"cell/{cell_key}/data/{data_item.key}",
        {"cell_key": cell_key, "data_key": data_item.key}
    )
    
    return {"status": "success", "encrypted": is_encrypted}

@app.get("/cells/{cell_key}/data/{key}", response_model=CellDataResponse)
async def get_cell_data(
    cell_key: str,
    key: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get data from a cell"""
    # Generate cache key
    cache_key = liquid_cache._generate_key("cell_data", {
        "cell_key": cell_key,
        "data_key": key,
        "user_id": str(current_user.id)
    })
    
    # Check if result is in cache
    cached_result = liquid_cache.get(cache_key)
    if cached_result:
        logger.debug(f"Cache hit for cell data {cell_key}/{key}")
        return cached_result
    
    # Register this data access pattern
    liquid_cache.register_query("cell_data_access", {
        "cell_key": cell_key,
        "data_key": key
    })
    
    # Verify cell access
    cell = db.query(Cell).filter(Cell.key == cell_key).first()
    if not cell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الخلية غير موجودة"
        )
    
    # Check if user has access to the cell
    if cell.owner_id != current_user.id:
        ownership = db.query(CellOwnership).filter(
            CellOwnership.cell_id == cell.id,
            CellOwnership.user_id == current_user.id
        ).first()
        
        if not ownership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="ليس لديك صلاحية الوصول إلى هذه الخلية"
            )
    
    # Connect to the cell's database
    conn = sqlite3.connect(f"{CELLS_DIR}/{cell_key}.db")
    conn.row_factory = sqlite3.Row
    
    # Execute query
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM data WHERE key = ?', (key,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="البيانات غير موجودة"
        )
    
    # Process data
    value = row["value"]
    
    # Try to decrypt if needed
    try:
        # Check if this looks like encrypted data
        if sgx_enclave.is_initialized and value.startswith("ENC:"):
            try:
                # Attempt to decrypt
                item_data = sgx_enclave.decrypt_data(value)
                if item_data and "value" in item_data:
                    value = item_data["value"]
            except Exception as e:
                logger.error(f"خطأ في فك تشفير البيانات: {e}")
                # إذا فشل فك التشفير، نعيد البيانات المشفرة كما هي
                value = {"error": "decryption_failed", "encrypted_data": value}
    except:
        # Not encrypted or not valid base64, use as is
        pass
    
    # Prepare response
    response = {"key": key, "value": value}
    
    # Cache the result
    liquid_cache.set(cache_key, response)
    
    # Send audit log
    await kafka_producer.send_audit_event(
        str(current_user.id),
        "retrieve",
        f"cell/{cell_key}/data/{key}",
        {"cell_key": cell_key, "data_key": key}
    )
    
    return response

@app.delete("/cells/{cell_key}/data/{key}", status_code=status.HTTP_200_OK)
async def delete_cell_data(
    cell_key: str,
    key: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete data from a cell"""
    # Verify cell access
    cell = db.query(Cell).filter(Cell.key == cell_key).first()
    if not cell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الخلية غير موجودة"
        )
    
    ownership = db.query(CellOwnership).filter(
        CellOwnership.cell_id == cell.id,
        CellOwnership.user_id == current_user.id
    ).first()
    
    if not ownership or ownership.permission_level not in ["owner", "editor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ليس لديك حق الحذف في هذه الخلية"
        )
    
    # Delete data from cell database
    import sqlite3
    conn = sqlite3.connect(f"{CELLS_DIR}/{cell_key}.db")
    cursor = conn.execute('DELETE FROM data WHERE key = ?', (key,))
    conn.commit()
    conn.close()
    
    # Invalidate cache entries related to this cell
    cache_keys_to_invalidate = liquid_cache.find_related_keys(f"cell_{cell_key}")
    for cache_key in cache_keys_to_invalidate:
        liquid_cache.invalidate(cache_key)
    
    # Also invalidate any specific key for this data
    specific_key = liquid_cache._generate_key("cell_data", {
        "cell_key": cell_key,
        "data_key": key,
        "user_id": str(current_user.id)
    })
    liquid_cache.invalidate(specific_key)
    
    # Send event to Kafka
    await kafka_producer.send_cell_event(
        cell_key,
        "data_deleted",
        {"key": key}
    )
    
    # Send audit log
    await kafka_producer.send_audit_event(
        str(current_user.id),
        "delete",
        f"cell/{cell_key}/data/{key}",
        {"cell_key": cell_key, "data_key": key}
    )
    
    return {"status": "success"}

@app.post("/cells/{cell_key}/query", status_code=status.HTTP_200_OK)
async def query_cell_data(
    cell_key: str,
    query: QueryRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Query data in a cell with optimized performance"""
    # Generate cache key for this query
    query_params = query.dict(exclude_none=True)
    cache_key = liquid_cache._generate_key("cell_query", {
        "cell_key": cell_key,
        "query": query_params,
        "user_id": str(current_user.id)
    })
    
    # Check if result is in cache
    cached_result = liquid_cache.get(cache_key)
    if cached_result:
        logger.debug(f"Cache hit for query on cell {cell_key}")
        return cached_result
    
    # Register this query pattern for learning
    liquid_cache.register_query("cell_query", {
        "cell_key": cell_key,
        "query_type": list(query_params.keys()) if query_params else ["all"]
    })
    
    # Verify cell access
    cell = db.query(Cell).filter(Cell.key == cell_key).first()
    if not cell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الخلية غير موجودة"
        )
    
    ownership = db.query(CellOwnership).filter(
        CellOwnership.cell_id == cell.id,
        CellOwnership.user_id == current_user.id
    ).first()
    
    if not ownership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ليس لديك حق الوصول إلى هذه الخلية"
        )
    
    # Get all data from cell database
    import sqlite3
    cell_path = os.path.join(CELLS_DIR, f"{cell_key}")
    db_file = os.path.join(cell_path, "data.db")
    
    conn = sqlite3.connect(db_file)
    cursor = conn.execute('SELECT key, value, created_at, updated_at FROM data')
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to list of dictionaries
    data = []
    for row in rows:
        item = {
            "key": row[0],
            "value": row[1],
            "created_at": row[2],
            "updated_at": row[3]
        }
        
        # Decrypt if needed
        try:
            if sgx_enclave.is_initialized:
                try:
                    # استخدام وظيفة البحث الآمن في البيانات المشفرة إذا كان الاستعلام يتضمن بحثًا
                    if query_params.get("search"):
                        search_result = sgx_enclave.secure_compute_on_encrypted(
                            "search",
                            item["value"],
                            {"query": query_params["search"]}
                        )
                        # إذا كان البحث ناجحًا ووجدت تطابقات، نفك تشفير البيانات
                        if search_result and search_result.get("count", 0) > 0:
                            decrypted_data = sgx_enclave.decrypt_data(item["value"])
                            if decrypted_data and "value" in decrypted_data:
                                item["value"] = decrypted_data["value"]
                                item["matched_search"] = True
                    else:
                        # فك تشفير البيانات العادي إذا لم يكن هناك بحث
                        decrypted_data = sgx_enclave.decrypt_data(item["value"])
                        if decrypted_data and "value" in decrypted_data:
                            item["value"] = decrypted_data["value"]
                except Exception as e:
                    logger.error(f"خطأ في معالجة البيانات المشفرة: {e}")
                    item["decryption_error"] = True
        except:
            pass
        
        data.append(item)
    
    # Use query optimizer to process the query
    result = await query_optimizer.optimize_query(query.dict(exclude_none=True), data)
    
    # Prepare response
    response = {"results": result, "count": len(result)}
    
    # Cache the result
    liquid_cache.set(cache_key, response)
    
    # Send audit log
    await kafka_producer.send_audit_event(
        str(current_user.id),
        "query",
        f"cell/{cell_key}",
        {"cell_key": cell_key, "query": query.dict(exclude_none=True)}
    )
    
    return response

# Admin endpoints
@app.get("/admin/stats", status_code=status.HTTP_200_OK)
async def get_admin_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get system statistics (admin only)"""
    # Get user count
    user_count = db.query(User).count()
    
    # Get cell count
    cell_count = db.query(Cell).count()
    
    # Get query optimizer stats
    optimizer_stats = query_optimizer.get_statistics()
    
    # Get storage usage
    import os
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(CELLS_DIR):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    
    # إحصائيات النظام
    system_stats = {
        "total_users": db.query(User).count(),
        "total_cells": db.query(Cell).count(),
        "active_users_24h": db.query(User).filter(User.last_login > datetime.utcnow() - timedelta(days=1)).count(),
        "sgx_enabled": sgx_enclave.is_initialized,
        "sgx_mode": "simulation" if sgx_enclave.simulation_mode else "hardware",
        "sgx_features": {
            "secure_compute": True,
            "remote_attestation": True,
            "data_integrity": True
        },
        "liquid_cache": liquid_cache.get_stats(),
        "liquid_cache_enabled": liquid_cache.enabled,
        "liquid_cache_patterns": len(liquid_cache.query_patterns),
        "kafka_enabled": kafka_producer.is_connected and kafka_consumer.is_connected,
        "server_uptime": str(datetime.utcnow() - app.state.start_time),
        "server_version": app.version
    }
    
    return {
        "users": user_count,
        "cells": cell_count,
        "storage_bytes": total_size,
        "storage_mb": total_size / (1024 * 1024),
        "query_optimizer": optimizer_stats,
        "sgx_enabled": sgx_enclave.is_initialized,
        "kafka_enabled": kafka_producer.is_ready,
        "system_stats": system_stats,
        "liquid_cache": liquid_cache.get_stats()
    }

@app.get("/admin/cache/stats", status_code=status.HTTP_200_OK)
async def get_cache_stats(current_user: User = Depends(get_current_admin_user)):
    """Get detailed liquid cache statistics (admin only)"""
    return {
        "stats": liquid_cache.get_stats(),
        "hot_patterns": liquid_cache.get_hot_patterns(limit=20),
        "layers": [len(layer) for layer in liquid_cache.cache_layers],
        "total_patterns": len(liquid_cache.query_patterns)
    }

@app.post("/admin/cache/clear", status_code=status.HTTP_200_OK)
async def clear_cache(current_user: User = Depends(get_current_admin_user)):
    """Clear the liquid cache (admin only)"""
    liquid_cache.clear()
    return {"status": "success", "message": "Liquid cache cleared successfully"}

@app.get("/admin/cache/hints", status_code=status.HTTP_200_OK)
async def get_cache_hints(current_user: User = Depends(get_current_admin_user)):
    """Get hints for data that should be preloaded in cache (admin only)"""
    hints = liquid_cache.get_preload_hints()
    return {
        "hints": hints,
        "count": len(hints),
        "patterns_analyzed": len(liquid_cache.query_patterns)
    }

@app.post("/admin/cache/preload", status_code=status.HTTP_200_OK)
async def preload_cache(current_user: User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    """Preload cache with frequently accessed data (admin only)"""
    # Get hints for preloading
    hints = liquid_cache.get_preload_hints(limit=50)
    preloaded = 0
    
    # Process each hint
    for hint in hints:
        try:
            if hint["type"] == "cell_data":
                # Preload cell data
                cell_key = hint["cell_key"]
                data_key = hint["data_key"]
                
                # Check if cell exists
                cell = db.query(Cell).filter(Cell.key == cell_key).first()
                if not cell:
                    continue
                
                # Connect to the cell's database
                conn = sqlite3.connect(f"{CELLS_DIR}/{cell_key}.db")
                conn.row_factory = sqlite3.Row
                
                # Execute query
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM data WHERE key = ?', (data_key,))
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    # Generate cache key
                    cache_key = liquid_cache._generate_key("cell_data", {
                        "cell_key": cell_key,
                        "data_key": data_key,
                        "user_id": "preload"
                    })
                    
                    # Cache the data
                    liquid_cache.set(cache_key, {"key": data_key, "value": row["value"]})
                    preloaded += 1
            
            elif hint["type"] == "cell_query":
                # Preload query results
                cell_key = hint["cell_key"]
                query_type = hint.get("query_type", ["all"])
                
                # Create a basic query
                query = {}
                if "filter" in query_type:
                    query["filter"] = {}
                if "sort" in query_type:
                    query["sort"] = ["created_at"]
                if "limit" in query_type:
                    query["limit"] = 100
                
                # Generate cache key
                cache_key = liquid_cache._generate_key("cell_query", {
                    "cell_key": cell_key,
                    "query": query,
                    "user_id": "preload"
                })
                
                # We don't actually execute the query, just register the pattern
                liquid_cache.register_query("cell_query", {
                    "cell_key": cell_key,
                    "query_type": query_type
                })
                preloaded += 1
        except Exception as e:
            logger.error(f"Error preloading cache item: {e}")
    
    return {
        "status": "success", 
        "preloaded": preloaded,
        "total_hints": len(hints),
        "cache_size": liquid_cache.get_stats()["size"]
    }

# SGX Secure Operations API Endpoints

@app.post("/api/secure/encrypt", response_model=Dict[str, any])
async def secure_encrypt_data(request: SecureDataRequest, current_user: User = Depends(get_current_active_user)):
    """تشفير البيانات باستخدام Intel SGX
    
    يقوم بتشفير البيانات المقدمة باستخدام تقنية Intel SGX للحصول على أقصى درجات الأمان.
    البيانات المشفرة يمكن تخزينها بأمان ولا يمكن الوصول إليها إلا من خلال واجهة برمجة التطبيقات المصرح بها.
    """
    if not sgx_enclave.is_initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="خدمة التشفير الآمن غير متاحة حالياً"
        )
    
    try:
        # تشفير البيانات باستخدام SGX
        encrypted_data = sgx_enclave.encrypt_data(request.data, request.data_id)
        if not encrypted_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="فشل تشفير البيانات"
            )
        
        # تسجيل الحدث في Kafka
        await kafka_producer.send_event(
            "secure_operations",
            {
                "operation": "encrypt",
                "user_id": current_user.id,
                "timestamp": datetime.utcnow().isoformat(),
                "data_id": encrypted_data.get("data_id"),
                "success": True
            }
        )
        
        return {
            "status": "success",
            "encrypted_data": encrypted_data
        }
    except Exception as e:
        logger.error(f"خطأ في تشفير البيانات: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطأ في تشفير البيانات: {str(e)}"
        )

@app.post("/api/secure/decrypt", response_model=Dict[str, any])
async def secure_decrypt_data(encrypted_data: Dict[str, str], current_user: User = Depends(get_current_active_user)):
    """فك تشفير البيانات باستخدام Intel SGX
    
    يقوم بفك تشفير البيانات المشفرة مسبقاً باستخدام تقنية Intel SGX.
    يجب أن تكون البيانات قد تم تشفيرها باستخدام نفس نظام SGX.
    """
    if not sgx_enclave.is_initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="خدمة التشفير الآمن غير متاحة حالياً"
        )
    
    try:
        # فك تشفير البيانات باستخدام SGX
        decrypted_data = sgx_enclave.decrypt_data(encrypted_data)
        if not decrypted_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="فشل فك تشفير البيانات"
            )
        
        # تسجيل الحدث في Kafka
        await kafka_producer.send_event(
            "secure_operations",
            {
                "operation": "decrypt",
                "user_id": current_user.id,
                "timestamp": datetime.utcnow().isoformat(),
                "data_id": encrypted_data.get("data_id"),
                "success": True
            }
        )
        
        return {
            "status": "success",
            "decrypted_data": decrypted_data
        }
    except Exception as e:
        logger.error(f"خطأ في فك تشفير البيانات: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطأ في فك تشفير البيانات: {str(e)}"
        )

@app.post("/api/secure/verify", response_model=Dict[str, any])
async def secure_verify_data(request: SecureVerifyRequest, current_user: User = Depends(get_current_active_user)):
    """التحقق من سلامة البيانات باستخدام Intel SGX
    
    يتحقق من سلامة البيانات عن طريق مقارنة قيمة التجزئة المحسوبة مع القيمة المتوقعة.
    يستخدم تقنية Intel SGX لضمان أن عملية التحقق تتم في بيئة آمنة.
    """
    if not sgx_enclave.is_initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="خدمة التشفير الآمن غير متاحة حالياً"
        )
    
    try:
        # التحقق من سلامة البيانات
        is_valid = sgx_enclave.verify_data_integrity(request.data, request.hash_value)
        
        return {
            "status": "success",
            "is_valid": is_valid
        }
    except Exception as e:
        logger.error(f"خطأ في التحقق من سلامة البيانات: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطأ في التحقق من سلامة البيانات: {str(e)}"
        )

@app.post("/api/secure/compute", response_model=Dict[str, any])
async def secure_compute_on_encrypted(request: SecureComputeRequest, current_user: User = Depends(get_current_active_user)):
    """إجراء عمليات على البيانات المشفرة باستخدام Intel SGX
    
    يتيح إجراء عمليات مثل البحث والتجميع والتصفية على البيانات المشفرة دون الحاجة إلى فك تشفيرها بالكامل.
    يستخدم تقنية Intel SGX لضمان أن العمليات تتم في بيئة آمنة.
    
    العمليات المدعومة:
    - search: البحث في البيانات المشفرة
    - aggregate: حساب إحصائيات على البيانات المشفرة
    - filter: تصفية البيانات المشفرة حسب معايير محددة
    """
    if not sgx_enclave.is_initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="خدمة التشفير الآمن غير متاحة حالياً"
        )
    
    supported_operations = ["search", "aggregate", "filter"]
    if request.operation not in supported_operations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"العملية غير مدعومة. العمليات المدعومة هي: {', '.join(supported_operations)}"
        )
    
    try:
        # إجراء العملية على البيانات المشفرة
        result = sgx_enclave.secure_compute_on_encrypted(
            request.operation,
            request.encrypted_data,
            request.params
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="فشل إجراء العملية على البيانات المشفرة"
            )
        
        # تسجيل الحدث في Kafka
        await kafka_producer.send_event(
            "secure_operations",
            {
                "operation": f"secure_compute_{request.operation}",
                "user_id": current_user.id,
                "timestamp": datetime.utcnow().isoformat(),
                "data_id": request.encrypted_data.get("data_id"),
                "success": True
            }
        )
        
        return {
            "status": "success",
            "operation": request.operation,
            "result": result
        }
    except Exception as e:
        logger.error(f"خطأ في إجراء العملية على البيانات المشفرة: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطأ في إجراء العملية على البيانات المشفرة: {str(e)}"
        )

@app.get("/api/secure/attestation", response_model=Dict[str, any])
async def secure_remote_attestation(current_user: User = Depends(get_current_admin_user)):
    """إجراء التحقق عن بعد من بيئة Intel SGX
    
    يقوم بإنشاء اقتباس يمكن التحقق منه بواسطة طرف بعيد للتأكد من أن الكود يعمل في بيئة SGX حقيقية.
    هذه العملية مهمة للتحقق من أن البيانات تتم معالجتها في بيئة آمنة وموثوقة.
    
    ملاحظة: هذه العملية متاحة فقط للمستخدمين الإداريين.
    """
    try:
        # إجراء التحقق عن بعد
        attestation_result = sgx_enclave.secure_remote_attestation()
        
        return {
            "status": "success",
            "attestation_data": attestation_result
        }
    except Exception as e:
        logger.error(f"خطأ في إجراء التحقق عن بعد: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطأ في إجراء التحقق عن بعد: {str(e)}"
        )

# Root endpoint
@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "name": "HiveDB API",
        "version": "1.0.0",
        "description": "واجهة برمجة التطبيقات لنظام قواعد بيانات HiveDB المستوحى من خلية النحل مع ميزات متقدمة"
    }

# Run the server
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
