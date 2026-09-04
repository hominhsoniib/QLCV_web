from sqlalchemy import Column, String, Integer, DateTime, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os

MasterBase = declarative_base()

class MasterCompany(MasterBase):
    __tablename__ = "master_companies"
    
    tax_code = Column(String, primary_key=True, index=True) # Mã Số Thuế (MST)
    code = Column(String, default="")                       # Mã ký hiệu công ty (VD: CTY01)
    name = Column(String, nullable=False)                    # Tên đầy đủ công ty
    short_name = Column(String, default="")                 # Tên viết tắt / Tên giao dịch
    legal_rep = Column(String, default="")                  # Người đại diện pháp luật
    address = Column(String, default="")                    # Địa chỉ trụ sở chính
    phone = Column(String, default="")                      # Số điện thoại liên hệ
    email = Column(String, default="")                      # Email liên hệ công ty
    website = Column(String, default="")                    # Website công ty
    business_field = Column(String, default="")             # Lĩnh vực hoạt động
    db_path = Column(String, nullable=False)                # Đường dẫn file SQLite DB của công ty
    status = Column(String, default="ACTIVE")               # ACTIVE / INACTIVE
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class GlobalUserIndex(MasterBase):
    __tablename__ = "global_user_index"
    
    email = Column(String, primary_key=True, index=True)   # Email đăng nhập nhân viên
    tax_code = Column(String, nullable=False, index=True)  # Mã số thuế công ty sở hữu
    ma_nv = Column(String, nullable=True)                  # Mã nhân viên trong DB công ty
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
