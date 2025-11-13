import os
import platform
import subprocess

def activate_ttsenv():
    """
    Activates the virtual environment named 'ttsenv'.
    Works on both Windows and Unix-based systems.
    Returns the environment's activation process handle.
    """
    system = platform.system()

    if system == "Windows":
        activate_script = os.path.join("ttsenv", "Scripts", "activate.bat")
        command = f'cmd /k "{activate_script}"'
    else:
        activate_script = os.path.join("ttsenv", "bin", "activate")
        command = f'bash --rcfile "{activate_script}"'

    if not os.path.exists(activate_script):
        raise FileNotFoundError(f"Could not find virtual environment activation script: {activate_script}")

    print(f"🚀 Activating environment: {activate_script}")
    process = subprocess.Popen(command, shell=True)
    return process


def deactivate_ttsenv(process):
    """
    Deactivates the given virtual environment process.
    """
    if process and process.poll() is None:
        print("🛑 Deactivating virtual environment...")
        process.terminate()
        process.wait()
        print("✅ Environment deactivated.")
    else:
        print("⚠️ Environment is not active or already closed.")

