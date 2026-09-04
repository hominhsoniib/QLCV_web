from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import Request
from config import Config

# Primary default engine & base
if Config.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(Config.DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(Config.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db(request: Request = None):
    """FastAPI database session dependency supporting Multi-Tenant dynamic routing.
    Extracts company_mst from the authenticated user's session cookie to load their tenant DB.
    """
    tax_code = "0312345678"
    if request:
        try:
            from services.auth_service import AuthService
            session_data = AuthService.get_session(request)
            if session_data and session_data.get("company_mst"):
                tax_code = session_data.get("company_mst")
        except Exception:
            pass
            
    from database.multi_tenant import get_tenant_session
    db = get_tenant_session(tax_code)
    try:
        yield db
    finally:
        db.close()
