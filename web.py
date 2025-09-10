#!/usr/bin/env python3
"""
Aeonforge Enterprise System - Railway Deployment Entry Point
Complete Phase 8-10 Integration: Database, Payments, AI Analytics
"""
import sys
import os
import asyncio

# Add current directory to Python path for phase imports
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

# Import enterprise integration
try:
    from phase8_10_integration import create_enterprise_app
    print("Loading Aeonforge Enterprise System (Phase 8-10)")
    app = create_enterprise_app()
    print("Enterprise system initialized successfully")
except ImportError as e:
    print(f"Enterprise system not available, falling back to hybrid API: {e}")
    # Fallback to hybrid API
    from main_hybrid import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Aeonforge Enterprise System on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)