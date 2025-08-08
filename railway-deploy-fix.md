# Railway Deployment Troubleshooting

## Common Issues and Fixes

### Issue 1: Mixed Python/Node.js Detection
Railway might be confused by having both package.json and requirements.txt

**Solution A: Use Railway Dashboard**
1. Go to [railway.app](https://railway.app)
2. Delete current project if it exists
3. Create "New Project" → "Empty Project"
4. Connect GitHub repo manually
5. Set these variables in Railway dashboard:
   - `NIXPACKS_PYTHON_VERSION`: `3.9`
   - `PORT`: `8000`
   - `PYTHONPATH`: `/app/backend`

**Solution B: Separate Backend Deployment**
Deploy only the backend folder:

1. Create a new branch with just backend:
```bash
git checkout -b railway-backend
mkdir temp-backend
cp -r backend/* temp-backend/
cp requirements.txt temp-backend/
rm -rf *
mv temp-backend/* .
git add .
git commit -m "Backend only for Railway"
git push origin railway-backend
```

2. Deploy this branch to Railway

### Issue 2: Start Command Problems
The main.py might not be starting correctly.

**Fix: Use the updated files**
- Updated `railway.json` with proper uvicorn command
- Updated `main.py` with PORT environment variable
- Added `nixpacks.toml` for explicit configuration

### Issue 3: Dependencies Issue
Some packages might be failing to install.

**Solution: Minimal requirements**
Create a minimal requirements.txt for Railway:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pandas==2.1.3
numpy==1.25.2
yfinance==0.2.28
requests==2.31.0
python-multipart==0.0.6
pydantic==2.5.0
```

## Alternative: Try Render Instead

If Railway keeps failing, Render is often more reliable:

1. Push your changes to GitHub:
```bash
git add .
git commit -m "Fix Railway deployment"
git push origin main
```

2. Go to [render.com](https://render.com)
3. "New" → "Web Service"
4. Connect GitHub repo
5. Configure:
   - Name: earnings-predictor-backend
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `cd backend && python main.py`

## Try Railway Again

With the fixes applied:

1. Commit changes:
```bash
git add .
git commit -m "Fix Railway deployment configuration"
git push origin main
```

2. Try Railway again:
```bash
railway up --detach
```

3. If it still fails, check logs:
```bash
railway logs --tail
```