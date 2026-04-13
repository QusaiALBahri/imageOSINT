"""
OSINT Image Search & Google Maps Scraper
Quick start script
"""

import os
import sys
import subprocess

def check_python_version():
    """Check if Python version meets requirements"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ is required")
        print(f"Your version: {sys.version_info.major}.{sys.version_info.minor}")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} OK")

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "-r", "requirements.txt", "-q"
        ])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)

def check_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    dirs = ["uploads", "outputs", "modules"]
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
    print("✓ Directories ready")

def main():
    """Main startup sequence"""
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║   OSINT Image Search & Google Maps Scraper             ║
    ║   Powered by Gradio                                    ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    print("\n🔍 Starting OSINT Image Tool...")
    
    # Checks
    print("\n📋 Running checks...")
    check_python_version()
    check_directories()
    
    # Install dependencies
    try:
        import gradio
        import requests
        import bs4
        print("✓ Core dependencies verified")
    except ImportError:
        install_dependencies()
    
    # Start application
    print("\n🚀 Starting Gradio server...")
    print("   Access the app at: http://localhost:7860")
    print("   Press Ctrl+C to stop\n")
    
    try:
        from app import create_interface
        demo = create_interface()
        demo.launch(
            server_name="127.0.0.1",
            server_port=7860,
            share=False,
            show_error=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
