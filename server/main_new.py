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
    
    logger.info("HiveDB server started successfully")

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
    db_file = os.path.join(cell_path, "data.db")
    
    # Check if we should encrypt the data using SGX
    value_to_store = data_item.value
    is_encrypted = False
    
    if sgx_enclave.is_initialized:
        encrypted_data = sgx_enclave.encrypt_data({"value": data_item.value})
        if encrypted_data:
            value_to_store = encrypted_data
            is_encrypted = True
    
    # Store the data
    now = datetime.now().isoformat()
    conn = sqlite3.connect(db_file)
    
    # Check if key exists
    cursor = conn.execute('SELECT 1 FROM data WHERE key = ?', (data_item.key,))
    exists = cursor.fetchone() is not None
    
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
    
    # Get data from cell database
    import sqlite3
    cell_path = os.path.join(CELLS_DIR, f"{cell_key}")
    db_file = os.path.join(cell_path, "data.db")
    
    conn = sqlite3.connect(db_file)
    cursor = conn.execute('SELECT value FROM data WHERE key = ?', (key,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المفتاح غير موجود"
        )
    
    value = row[0]
    
    # Check if the value is encrypted and decrypt it using SGX
    try:
        import base64
        import json
        # Try to decode as base64 and parse as JSON to check if it's encrypted
        decoded = base64.b64decode(value)
        if sgx_enclave.is_initialized:
            decrypted_data = sgx_enclave.decrypt_data(value)
            if decrypted_data and "value" in decrypted_data:
                value = decrypted_data["value"]
    except:
        # Not encrypted or not valid base64, use as is
        pass
    
    # Send audit log
    await kafka_producer.send_audit_event(
        str(current_user.id),
        "retrieve",
        f"cell/{cell_key}/data/{key}",
        {"cell_key": cell_key, "data_key": key}
    )
    
    return {"key": key, "value": value}

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
    cell_path = os.path.join(CELLS_DIR, f"{cell_key}")
    db_file = os.path.join(cell_path, "data.db")
    
    conn = sqlite3.connect(db_file)
    conn.execute('DELETE FROM data WHERE key = ?', (key,))
    conn.commit()
    conn.close()
    
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
                decrypted_data = sgx_enclave.decrypt_data(item["value"])
                if decrypted_data and "value" in decrypted_data:
                    item["value"] = decrypted_data["value"]
        except:
            pass
        
        data.append(item)
    
    # Use query optimizer to process the query
    result = await query_optimizer.optimize_query(query.dict(exclude_none=True), data)
    
    # Send audit log
    await kafka_producer.send_audit_event(
        str(current_user.id),
        "query",
        f"cell/{cell_key}",
        {"cell_key": cell_key, "query": query.dict(exclude_none=True)}
    )
    
    return {"results": result, "count": len(result)}

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
    
    return {
        "users": user_count,
        "cells": cell_count,
        "storage_bytes": total_size,
        "storage_mb": total_size / (1024 * 1024),
        "query_optimizer": optimizer_stats,
        "sgx_enabled": sgx_enclave.is_initialized,
        "kafka_enabled": kafka_producer.is_ready
    }

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
