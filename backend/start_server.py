#!/usr/bin/env python3
"""
Start the FastAPI server with proper configuration.
Run this from the backend directory: python start_server.py
"""

import sys
import os
import uvicorn

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Starting AI Medical Dispatch Backend Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("🗺️ Maps API endpoints at: http://localhost:8000/maps/")
    print("\n⚠️  Make sure you have:")
    print("   1. Installed dependencies: pip install -r requirements.txt")
    print("   2. Set up .env file with GOOGLE_MAPS_API_KEY")
    print("   3. Started your database")
    print("\n" + "="*50)
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_dirs=["app"]
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("Check that all dependencies are installed and .env is configured")
