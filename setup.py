#!/usr/bin/env python3
"""
Setup script for Earnings Predictor
Automates the complete setup process
"""

import subprocess
import sys
import os
import time

def run_command(command, description, cwd=None):
    """Run a command and handle errors"""
    print(f"\n{'='*50}")
    print(f"🔧 {description}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return False
        else:
            print(f"✅ Success: {description}")
            if result.stdout:
                print(result.stdout)
            return True
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("🚀 Starting Earnings Predictor Setup")
    print("This will set up the complete application including data collection and model training.")
    print("Estimated time: 10-15 minutes")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    # Check if we're in the right directory
    if not os.path.exists("backend") or not os.path.exists("frontend"):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("❌ Failed to install Python dependencies")
        sys.exit(1)
    
    # Install Node.js dependencies
    if not run_command("npm install", "Installing Node.js dependencies", cwd="frontend"):
        print("❌ Failed to install Node.js dependencies")
        sys.exit(1)
    
    # Create necessary directories
    os.makedirs("backend/data", exist_ok=True)
    os.makedirs("backend/models", exist_ok=True)
    print("✅ Created data and models directories")
    
    # Run data pipeline
    print("\n🔄 Starting data collection (this may take 5-10 minutes)...")
    if not run_command("python data_pipeline.py", "Collecting historical earnings data", cwd="backend"):
        print("❌ Failed to collect data")
        sys.exit(1)
    
    # Train model
    print("\n🤖 Training machine learning model (this may take 2-5 minutes)...")
    if not run_command("python train_model.py", "Training ML model", cwd="backend"):
        print("❌ Failed to train model")
        sys.exit(1)
    
    print("\n🎉 Setup Complete!")
    print("\n" + "="*50)
    print("🚀 TO START THE APPLICATION:")
    print("="*50)
    print("\n1. Start the backend API:")
    print("   cd backend")
    print("   python main.py")
    print("\n2. In a new terminal, start the frontend:")
    print("   cd frontend") 
    print("   npm run dev")
    print("\n3. Open your browser to:")
    print("   Frontend: http://localhost:3000")
    print("   API docs: http://localhost:8000/docs")
    
    print("\n📊 Your app is ready with:")
    print("✅ Historical earnings data collected")
    print("✅ ML model trained and ready")
    print("✅ Frontend and backend configured")
    print("✅ All dependencies installed")
    
    print("\n💡 Tip: The data pipeline collects ~2 years of data for 60 major stocks.")
    print("    You can customize the stock list in backend/data_pipeline.py")

if __name__ == "__main__":
    main()