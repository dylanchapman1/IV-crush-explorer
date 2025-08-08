#!/usr/bin/env python3
"""
Simplified start script for Render deployment
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import and run the simplified app
try:
    from backend.main import app
    import uvicorn
except ImportError:
    # Fallback to simple version without pandas dependencies
    import uvicorn
    sys.path.insert(0, 'backend')
    from main_simple import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)