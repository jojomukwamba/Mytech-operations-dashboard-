import os
import sys
import webbrowser
import threading
import time
import subprocess

def open_browser():
    # Wait a few seconds for the Django server to start, then open the browser
    time.sleep(3)
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    print("======================================")
    print("      Starting FTP Ops Server...      ")
    print("======================================")
    print("Please keep this window open while using the app.")
    
    # Start the browser thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Paths to the virtual environment python and manage.py
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    venv_python = os.path.join(base_dir, "venv", "Scripts", "python.exe")
    manage_py = os.path.join(base_dir, "manage.py")
    
    # Run the server
    if os.path.exists(venv_python) and os.path.exists(manage_py):
        try:
            subprocess.call([venv_python, manage_py, "runserver"])
        except KeyboardInterrupt:
            print("\nShutting down server...")
    else:
        print(f"Error: Could not find the virtual environment at {venv_python}")
        print("Make sure you run this executable from inside the OPERATIONS DASH BOARD folder.")
        input("Press Enter to exit...")
