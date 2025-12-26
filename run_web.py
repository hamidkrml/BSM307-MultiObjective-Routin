#!/usr/bin/env python3
"""
BSM307 Web Server Launcher
FastAPI web server'ı başlatır
Docker uyumlu
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from src.api.server import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print("=" * 70)
    print("BSM307 Multi-Objective Routing - Web Server")
    print("=" * 70)
    print(f"\n🚀 Starting server on http://{host}:{port}")
    print(f"📋 Container içinde: http://localhost:{port}")
    print(f"📋 Host'tan erişim: http://localhost:8001 (Docker port mapping)")
    print("\n")
    
    uvicorn.run(app, host=host, port=port, log_level="info")

