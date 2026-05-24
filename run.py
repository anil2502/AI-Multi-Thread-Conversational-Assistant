# import subprocess
# import sys
# import os

# def run_workspace():
#     print("🚀 Booting up the Lexi Agentic AI Workspace...")

#     # Define platform-dependent shell executing requirements
#     use_shell = sys.platform == "win32"

#     # 1. Define backend service commands (Uvicorn)
#     backend_dir = os.path.join(os.path.dirname(__file__), "backend")
#     backend_cmd = [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8000"]

#     # 2. Define frontend service commands (Streamlit)
#     frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
#     frontend_cmd = [sys.executable, "-m", "streamlit", "run", "src/app.py", "--server.port", "8501"]

#     try:
#         # Launch applications concurrently in background subprocess layers
#         backend_process = subprocess.Popen(backend_cmd, cwd=backend_dir)
#         frontend_process = subprocess.Popen(frontend_cmd, cwd=frontend_dir)

#         print("\n⚡ FastAPI Backend running on http://127.0.0.1:8000")
#         print("🎨 Streamlit Frontend running on http://127.0.0.1:8501")
#         print("Press Ctrl+C to stop both applications simultaneously safely.\n")

#         backend_process.wait()
#         frontend_process.wait()

#     except KeyboardInterrupt:
#         print("\n🛑 Shutting down workspace processes safely...")
#         backend_process.terminate()
#         frontend_process.terminate()
#         print("👋 Environment stopped successfully.")

# if __name__ == "__main__":
#     run_workspace()


#######################################################################################################################

import subprocess
import sys
import os
import time
import urllib.request

def is_backend_alive(url="http://127.0.0.1:8000", timeout=1):
    """Attempts to connect to the backend to see if it's awake yet."""
    try:
        # We use a simple HTTP request with a short timeout
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.status == 200
    except Exception:
        return False

def run_workspace():
    print("🚀 Booting up the Lexi Agentic AI Workspace...")

    # Define paths and commands
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    backend_cmd = [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8000"]

    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
    frontend_cmd = [sys.executable, "-m", "streamlit", "run", "src/app.py", "--server.port", "8501"]

    backend_process = None
    frontend_process = None

    try:
        # STEP 1: Start the Backend Process first
        print("⏳ Launching FastAPI Backend...")
        backend_process = subprocess.Popen(backend_cmd, cwd=backend_dir)

        # STEP 2: Wait until the backend answers HTTP requests
        print("🔍 Waiting for Backend to compile and go live...")
        max_retries = 30  # Give it up to 30 seconds to start
        retry_count = 0
        
        while retry_count < max_retries:
            # Check if the backend process crashed during startup
            if backend_process.poll() is not None:
                print("❌ Backend process crashed unexpectedly on startup.")
                return

            if is_backend_alive():
                print("✅ Backend is officially live!")
                break
                
            time.sleep(1)
            retry_count += 1
        else:
            print("❌ Timeout: Backend took too long to start up.")
            backend_process.terminate()
            return

        # STEP 3: Now that backend is live, start the Frontend safely
        print("🎨 Launching Streamlit Frontend...")
        frontend_process = subprocess.Popen(frontend_cmd, cwd=frontend_dir)

        print("\n⚡ Services Running Smoothly:")
        print("   FastAPI Backend:   http://127.0.0.1:8000")
        print("   Streamlit Frontend: http://127.0.0.1:8501")
        print("Press Ctrl+C to stop both applications safely.\n")

        # Keep the manager script open
        backend_process.wait()
        frontend_process.wait()

    except KeyboardInterrupt:
        print("\n🛑 Shutting down workspace processes safely...")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        print("👋 Environment stopped successfully.")

if __name__ == "__main__":
    run_workspace()