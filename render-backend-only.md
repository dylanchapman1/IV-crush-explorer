# Backend-Only Deployment to Render

Since Railway is having persistent issues, let's deploy just the backend to Render.

## Quick Render Setup (5 minutes)

### Step 1: Create backend-only branch
```bash
# Create a clean backend-only repository structure
git checkout -b render-backend
mkdir temp-deploy
cp -r backend/* temp-deploy/
cp requirements-minimal.txt temp-deploy/requirements.txt
cp start.py temp-deploy/
rm -rf *
mv temp-deploy/* .
rmdir temp-deploy
git add .
git commit -m "Backend only for Render deployment"
git push origin render-backend
```

### Step 2: Deploy to Render
1. Go to [render.com](https://render.com)
2. "New +" → "Web Service"
3. Connect GitHub repo
4. Select branch: `render-backend`
5. Configure:
   - **Name**: earnings-predictor-backend
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python start.py`

### Step 3: Environment Variables in Render
Add these in Render dashboard:
- `PYTHON_VERSION`: `3.9`
- `PORT`: `10000`

## Alternative: Use the existing render.yaml

The render.yaml file I created earlier should work automatically:

1. Push current code to GitHub
2. Connect to Render
3. Render will use the render.yaml configuration automatically