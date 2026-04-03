import PyInstaller.__main__
import os

def build():
    # Application name
    name = "PyBridge"
    # Entry point
    script = "gui.py"
    
    # PyInstaller arguments
    params = [
        script,
        f"--name={name}",
        "--onefile",
        "--noconsole",
        "--collect-all=customtkinter",
        "--collect-all=pywinstyles",
        "--clean",
        # Uncomment and add icon file if available
        # f"--icon=icon.ico",
    ]
    
    print(f"Building {name} executable...")
    PyInstaller.__main__.run(params)
    print("\nBuild complete! Look for the executable in the 'dist' folder.")

if __name__ == "__main__":
    build()
