import uvicorn
from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse
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
from routes.mobile import router as mobile_router
from models.models import AIConfig, Process, ProcessStep, JobDescription
from database.multi_tenant import init_master_and_default_tenant
import os
import sys

from fastapi.middleware.cors import CORSMiddleware
from services.file_access_service import gateway, denied
from database.connection import get_db
from pathlib import Path
from config import Config

# Initialize FastAPI application
app = FastAPI(
    title="AMS PRO 5.0 - Quản Lý Công Việc (Multi-Tenant)",
    description="Hệ thống Quản lý công việc Đa công ty & Đa Cơ sở dữ liệu theo Mã Số Thuế",
    version="5.0.4"
)

# Enable CORS for external domains, proxies, and cloudflared tunnels
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_no_cache_header(request: Request, call_next):
    response = await call_next(request)
    if "text/html" in response.headers.get("content-type", ""):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

@app.get("/health")
def health_check():
    """Health check endpoint to verify backend service responsiveness."""
    return {"status": "ok", "service": "AMS PRO 5.0", "version": app.version}


# Mount static folder for CSS, JS, uploads
os.makedirs("static/uploads", exist_ok=True)
@app.api_route('/static/uploads/{storage_name:path}',methods=['GET','HEAD'])
def private_upload(request: Request, storage_name: str, db=Depends(get_db)):
    return gateway(request,storage_name,db)


class PublicStaticFiles(StaticFiles):
    """Defense in depth: parent mount never serves uploads or their aliases."""
    async def get_response(self,path,scope):
        parts=path.replace('\\','/').split('/')
        # StaticFiles normalizes public paths to Windows backslashes itself.
        # Reject request aliases, not those framework-generated separators.
        raw=scope.get('raw_path',b'')
        if '%' in path or b'\\' in raw or any(p.casefold()=='uploads' for p in parts):
            return denied()
        target=(Path(self.directory)/path).resolve()
        forbidden=[Path(Config.UPLOAD_DIR).resolve(),(Path(self.directory)/'uploads').resolve()]
        if any(target.is_relative_to(root) for root in forbidden):
            return denied()
        return await super().get_response(path,scope)

if getattr(sys, 'frozen', False):
    app.mount("/static", PublicStaticFiles(directory=os.path.join(sys._MEIPASS, "static")), name="static")
else:
    os.makedirs("static/css", exist_ok=True)
    os.makedirs("static/js", exist_ok=True)
    app.mount("/static", PublicStaticFiles(directory="static"), name="static")

# Mount an optional local document directory (configure via LOCAL_DOCS_DIR in .env).
# Previously this was a hardcoded personal machine path — removed for portability
# and because it silently exposed a local folder as a public static route.
local_docs_dir = os.getenv("LOCAL_DOCS_DIR", "").strip()
if local_docs_dir and os.path.exists(local_docs_dir):
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
app.include_router(mobile_router)

@app.get("/manifest.json")
def get_manifest():
    return FileResponse("static/manifest.json", media_type="application/json")

@app.get("/sw.js")
def get_service_worker():
    return FileResponse("static/sw.js", media_type="application/javascript")

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
        
@app.exception_handler(404)
def custom_404_handler(request: Request, exc):
    # Only redirect page (HTML) navigation to the dashboard. API/static 404s must
    # stay as real 404 responses, otherwise clients silently get an HTML page
    # instead of an error and API/integration bugs become invisible.
    path = request.url.path
    if path.startswith("/api/") or path.startswith("/static/"):
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=404, content={"success": False, "message": "Not found"})
    return RedirectResponse(url="/dashboard")

if __name__ == "__main__":
    import uvicorn
    from config import Config
    # reload=True spawns a file-watcher subprocess meant for local development only.
    # Set APP_ENV=development in .env to enable it; production defaults to reload=False.
    uvicorn.run("app:app", host=Config.HOST, port=Config.PORT, reload=(Config.APP_ENV == "development"))
