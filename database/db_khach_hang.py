import sqlite3
import os
import hashlib
import uuid
import time
import random
from contextvars import ContextVar
from config_khach_hang import Config, SCHEMA, Tables

active_company: ContextVar[str] = ContextVar("active_company", default="default")

def get_db():
    try:
        company = active_company.get()
    except LookupError:
        company = "default"
        
    if company == "default":
        db_path = Config.DATABASE_PATH
    else:
        db_path = os.path.join(os.path.dirname(Config.DATABASE_PATH), f"qlcv_khach_hang_{company}.db")
        
    db_exists = os.path.exists(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    if not db_exists:
        init_db_connection(conn)
        seed_new_db(conn)
        
    return conn

def init_db_connection(conn):
    cursor = conn.cursor()
    for table, cols in SCHEMA.items():
        col_defs = []
        for col in cols:
            if col == "id" and table not in [Tables.CONFIG, Tables.SESSION]:
                col_defs.append("id TEXT PRIMARY KEY")
            elif col == "key" and table == Tables.CONFIG:
                col_defs.append("key TEXT PRIMARY KEY")
            elif col == "token" and table == Tables.SESSION:
                col_defs.append("token TEXT PRIMARY KEY")
            else:
                col_defs.append(f"{col} TEXT")
        
        sql = f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(col_defs)})"
        cursor.execute(sql)
    conn.commit()

def seed_new_db(conn):
    cursor = conn.cursor()
    
    def local_gen_salt():
        return str(uuid.uuid4()).replace("-", "")
        
    def local_hash_password(password, salt):
        message = f"{password}:{salt}"
        return hashlib.sha256(message.encode("utf-8")).hexdigest()
        
    def local_base36encode(number):
        if number < 0:
            return ""
        alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
        base36 = ""
        while number:
            number, i = divmod(number, 36)
            base36 = alphabet[i] + base36
        return base36 or alphabet[0]
        
    def local_gen_id(prefix):
        timestamp = local_base36encode(int(time.time() * 1000))
        rand_val = random.randint(100000, 99999999)
        rand_part = local_base36encode(rand_val)[:5]
        return f"{prefix}_{timestamp}_{rand_part}"
        
    from datetime import datetime
    
    # Tạo Admin mặc định
    salt = local_gen_salt()
    pw_hash = local_hash_password(Config.DEFAULT_ADMIN_PASS, salt)
    user_id = local_gen_id("USR")
    cursor.execute(
        f"INSERT INTO {Tables.USERS} (id, email, passwordHash, salt, name, role, status, createdAt, lastLogin) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (user_id, Config.DEFAULT_ADMIN_EMAIL.lower(), pw_hash, salt, Config.DEFAULT_ADMIN_NAME, "Admin", "active", datetime.now().isoformat(), "")
    )
    
    # Tạo cấu hình mặc định
    cursor.execute(f"INSERT INTO {Tables.CONFIG} (key, value) VALUES (?, ?)", ("kpi_revenue_target", "100000000"))
    cursor.execute(f"INSERT INTO {Tables.CONFIG} (key, value) VALUES (?, ?)", ("kpi_deal_target", "20"))
    cursor.execute(f"INSERT INTO {Tables.CONFIG} (key, value) VALUES (?, ?)", ("ai_provider", "claude"))
    
    # Tạo templates mẫu
    cursor.execute(
        f"INSERT INTO {Tables.TEMPLATES} (id, name, trigger, subject, body, active, createdAt) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (local_gen_id("TPL"), "Chào mừng khách mới", "status:Lead", "Cảm ơn {{name}} đã quan tâm!", "Xin chào {{name}},\n\nCảm ơn bạn đã để lại thông tin. Đội ngũ của chúng tôi sẽ liên hệ sớm.\n\nTrân trọng.", "no", datetime.now().isoformat())
    )
    cursor.execute(
        f"INSERT INTO {Tables.TEMPLATES} (id, name, trigger, subject, body, active, createdAt) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (local_gen_id("TPL"), "Cảm ơn đã chốt deal", "status:Đã chốt", "Cảm ơn {{name}} đã tin tưởng!", "Xin chào {{name}},\n\nCảm ơn bạn đã đồng hành. Chúng tôi rất vui được phục vụ bạn.\n\nTrân trọng.", "no", datetime.now().isoformat())
    )
    conn.commit()

def init_db():
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
    
    conn = get_db()
    conn.close()

def read_all(table_name: str) -> list[dict]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def insert(table_name: str, data: dict) -> dict:
    conn = get_db()
    cursor = conn.cursor()
    
    # Lọc data chỉ lấy các cột có trong SCHEMA của bảng đó
    valid_cols = SCHEMA[table_name]
    filtered_data = {k: v for k, v in data.items() if k in valid_cols}
    
    cols = list(filtered_data.keys())
    vals = list(filtered_data.values())
    placeholders = ", ".join(["?"] * len(vals))
    
    sql = f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({placeholders})"
    cursor.execute(sql, vals)
    conn.commit()
    conn.close()
    return filtered_data

def update_by_id(table_name: str, id_val: str, patch: dict) -> bool:
    conn = get_db()
    cursor = conn.cursor()
    
    # Xác định cột khóa chính
    id_col = "id"
    if table_name == Tables.CONFIG:
        id_col = "key"
    elif table_name == Tables.SESSION:
        id_col = "token"
        
    valid_cols = SCHEMA[table_name]
    filtered_patch = {k: v for k, v in patch.items() if k in valid_cols and k != id_col}
    
    if not filtered_patch:
        conn.close()
        return False
        
    set_clause = ", ".join([f"{k} = ?" for k in filtered_patch.keys()])
    vals = list(filtered_patch.values()) + [id_val]
    
    sql = f"UPDATE {table_name} SET {set_clause} WHERE {id_col} = ?"
    cursor.execute(sql, vals)
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated

def delete_by_id(table_name: str, id_val: str) -> bool:
    conn = get_db()
    cursor = conn.cursor()
    
    id_col = "id"
    if table_name == Tables.CONFIG:
        id_col = "key"
    elif table_name == Tables.SESSION:
        id_col = "token"
        
    sql = f"DELETE FROM {table_name} WHERE {id_col} = ?"
    cursor.execute(sql, (id_val,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def find_by_id(table_name: str, id_val: str) -> dict | None:
    conn = get_db()
    cursor = conn.cursor()
    
    id_col = "id"
    if table_name == Tables.CONFIG:
        id_col = "key"
    elif table_name == Tables.SESSION:
        id_col = "token"
        
    sql = f"SELECT * FROM {table_name} WHERE {id_col} = ?"
    cursor.execute(sql, (id_val,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None
