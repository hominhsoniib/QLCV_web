import os
import sys
# Pre-import numpy and pandas to resolve PyInstaller circular loading namespace bugs
try:
    import numpy
    import pandas
except ImportError:
    pass

import threading
import time
import webbrowser

# --- MONKEYPATCH FASTAPI FOR PYINSTALLER FROZEN ENV ---
if getattr(sys, 'frozen', False):
    # Under PyInstaller, sys._MEIPASS contains the path to the temporary folder where files are extracted.
    bundle_dir = sys._MEIPASS
    
    # 1. Patch Jinja2Templates to resolve to extracted templates folder
    from fastapi.templating import Jinja2Templates
    original_jinja_init = Jinja2Templates.__init__
    
    def custom_jinja_init(self, directory, *args, **kwargs):
        if directory == "templates":
            directory = os.path.join(bundle_dir, "templates")
        elif isinstance(directory, str) and not os.path.isabs(directory):
            # Resolve relative paths relative to bundle dir
            directory = os.path.join(bundle_dir, directory)
        original_jinja_init(self, directory, *args, **kwargs)
        
    Jinja2Templates.__init__ = custom_jinja_init

    # 2. Patch StaticFiles to resolve to extracted static folder
    from fastapi.staticfiles import StaticFiles
    original_static_init = StaticFiles.__init__
    
    def custom_static_init(self, directory=None, *args, **kwargs):
        if directory == "static":
            directory = os.path.join(bundle_dir, "static")
        elif isinstance(directory, str) and not os.path.isabs(directory):
            directory = os.path.join(bundle_dir, directory)
        original_static_init(self, directory=directory, *args, **kwargs)
        
    StaticFiles.__init__ = custom_static_init

else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

# Make sure imports from current directory work
sys.path.insert(0, bundle_dir)

# --- RUNNERS FOR BOTH APPLICATIONS ---

def start_fastapi():
    """Start the FastAPI backend server using Uvicorn."""
    import uvicorn
    from app import app
    from config import Config
    
    # Ensure port and host are read from configuration
    host = "127.0.0.1"
    port = Config.PORT if Config.PORT else 8000
    
    print(f"[*] Starting FastAPI backend at http://{host}:{port} ...")
    # Set reload=False when compiled because uvicorn reloader will fail in frozen executable!
    uvicorn.run(app, host=host, port=port, reload=False)

def auto_open_browser():
    """Automatically open the browser once servers are online."""
    from config import Config
    port = Config.PORT if Config.PORT else 8000
    
    # Wait for FastAPI server to start
    time.sleep(3)
    url = f"http://localhost:{port}"
    print(f"[+] Opening browser to {url} ...")
    webbrowser.open(url)

if __name__ == "__main__":
    # If the --fastapi flag is present, run FastAPI and exit immediately
    if "--fastapi" in sys.argv:
        start_fastapi()
        sys.exit(0)

    print("=====================================================================")
    print("                 AMS PRO 5.0 - SERVICE LAUNCHER                      ")
    print("=====================================================================")
    
    if getattr(sys, 'frozen', False):
        import shutil
        # Copy qlcv.db to CWD if missing
        cwd_qlcv = os.path.join(os.getcwd(), "qlcv.db")
        if not os.path.exists(cwd_qlcv):
            bundled_qlcv = os.path.join(bundle_dir, "qlcv.db")
            if os.path.exists(bundled_qlcv):
                print("[*] First-time setup: copying qlcv.db to workspace...")
                try:
                    shutil.copy2(bundled_qlcv, cwd_qlcv)
                except Exception as e:
                    print(f"[!] Warning: Could not copy qlcv.db: {e}")

    # 1. Start FastAPI as a separate subprocess
    import subprocess
    if getattr(sys, 'frozen', False):
        fastapi_proc = subprocess.Popen([sys.executable, "--fastapi"])
    else:
        fastapi_proc = subprocess.Popen([sys.executable, "main_launcher.py", "--fastapi"])
        
    # 2. Start browser opener thread
    browser_thread = threading.Thread(target=auto_open_browser, daemon=True)
    browser_thread.start()
    
    # 3. Wait for FastAPI subprocess to exit
    try:
        while True:
            time.sleep(1)
            if fastapi_proc.poll() is not None:
                break
    except KeyboardInterrupt:
        print("\n[+] Exiting application. Goodbye!")
    finally:
        print("[*] Terminating background processes...")
        if 'fastapi_proc' in locals():
            fastapi_proc.terminate()
            try:
                fastapi_proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                fastapi_proc.kill()
        sys.exit(0)
