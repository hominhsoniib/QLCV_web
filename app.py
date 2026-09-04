import uvicorn
from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from database.connection import engine, Base, SessionLocal
from sqlalchemy import text
from services.sheet_service import seed_database_from_excel
from routes.auth import router as auth_router
from routes.tasks import router as tasks_router
from routes.master import router as master_router
from routes.documents import router as documents_router
from routes.personal import router as personal_router
from routes.ai import router as ai_router
from routes.processes import router as processes_router
from routes.jds import router as jds_router
from routes.org_chart import router as org_chart_router
from routes.companies import router as companies_router
from models.models import AIConfig, Process, ProcessStep, JobDescription
from database.multi_tenant import init_master_and_default_tenant
import os
import sys

# Initialize FastAPI application
app = FastAPI(
    title="AMS PRO 5.0 - Quản Lý Công Việc (Multi-Tenant)",
    description="Hệ thống Quản lý công việc Đa công ty & Đa Cơ sở dữ liệu theo Mã Số Thuế",
    version="5.0.4"
)

@app.middleware("http")
async def add_no_cache_header(request: Request, call_next):
    response = await call_next(request)
    if "text/html" in response.headers.get("content-type", ""):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


# Mount static folder for CSS, JS, uploads
os.makedirs("static/uploads", exist_ok=True)
app.mount("/static/uploads", StaticFiles(directory="static/uploads"), name="static_uploads")

if getattr(sys, 'frozen', False):
    app.mount("/static", StaticFiles(directory=os.path.join(sys._MEIPASS, "static")), name="static")
else:
    os.makedirs("static/css", exist_ok=True)
    os.makedirs("static/js", exist_ok=True)
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount user's local document directory if it exists
local_docs_dir = "D:/POWER BI-VBA EXCEL/QLCV-QT-MTCV"
if os.path.exists(local_docs_dir):
    app.mount("/local_docs", StaticFiles(directory=local_docs_dir), name="local_docs")

# Include Routers
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(master_router)
app.include_router(companies_router)
app.include_router(documents_router)
app.include_router(personal_router)
app.include_router(ai_router)
app.include_router(processes_router)
app.include_router(jds_router)
app.include_router(org_chart_router)

from routes.khach_hang import router as khach_hang_router
app.include_router(khach_hang_router)

async def khach_hang_background_loop():
    import asyncio
    from services.khach_hang_auth import clean_expired_sessions
    from services.khach_hang_automation import check_follow_ups_due
    while True:
        try:
            clean_expired_sessions()
            check_follow_ups_due()
        except Exception as e:
            print(f"[KHACH HANG BACKGROUND TASK] Error: {e}")
        await asyncio.sleep(3600)

@app.on_event("startup")
async def startup_db_init():
    """Event handler triggered on application startup.
    Initializes Master System Registry for Multi-Tenant Companies & Databases.
    """
    print("[MULTI-TENANT] Initializing master system multi-tenant registry...")
    init_master_and_default_tenant()
    
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        cursor = db.execute(text("PRAGMA table_info(departments)"))
        columns = [row[1] for row in cursor.fetchall()]
        added = False
        for col in ['chuc_nang', 'nhiem_vu', 'quyen_han', 'kpi_chinh', 'kpi_phu']:
            if col not in columns:
                print(f"Adding missing column {col} to departments table...")
                db.execute(text(f"ALTER TABLE departments ADD COLUMN {col} TEXT DEFAULT ''"))
                added = True
        if added:
            db.commit()
            print("Successfully updated departments table schema!")
            
        cursor = db.execute(text("PRAGMA table_info(employees)"))
        emp_columns = [row[1] for row in cursor.fetchall()]
        if 'email' not in emp_columns:
            print("Adding missing column email to employees table...")
            db.execute(text("ALTER TABLE employees ADD COLUMN email TEXT"))
            db.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_employees_email ON employees(email)"))
            db.commit()
            print("Successfully updated employees table schema with email column!")
            
        print("Importing seed data from Excel spreadsheet...")
        seeded = seed_database_from_excel(db, "seed.xlsx")
        if seeded:
            print("Database successfully synchronized and seeded from spreadsheet Excel file!")
        else:
            print("No Excel seed file detected, or seeding was skipped. Default Admin account guaranteed.")
    except Exception as e:
         print("Failed to auto-migrate database or seed on startup:", e)
    finally:
        db.close()
        
    import asyncio
    asyncio.create_task(khach_hang_background_loop())

@app.exception_handler(404)
def custom_404_handler(request: Request, exc):
    return RedirectResponse(url="/dashboard")

if __name__ == "__main__":
    import uvicorn
    from config import Config
    uvicorn.run("app:app", host=Config.HOST, port=Config.PORT, reload=True)
