# Railway Deployment Fix

## The Issue
The `railway link` command fails when you don't have existing projects in your Railway workspace.

## Solution Options

### Option 1: Create Project via Railway Dashboard (Recommended)

1. **Go to Railway Dashboard:**
   - Visit [railway.app](https://railway.app)
   - Sign in with GitHub

2. **Create New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `finproj` repository
   - Railway will automatically detect it's a Python app

3. **Configure Settings:**
   - Railway will auto-configure most settings
   - The app should deploy automatically

4. **Then link locally:**
   ```bash
   railway link
   # Now you should see your project to select
   ```

### Option 2: Create Project via CLI

1. **Create a new project:**
   ```bash
   railway new
   ```

2. **When prompted:**
   - Project name: `earnings-predictor`
   - Template: `Empty Project`

3. **Link the project:**
   ```bash
   railway link
   ```

### Option 3: Use Deploy Command Directly

Skip the linking step entirely:
```bash
railway up --detach
```

This creates and deploys the project in one command.

## Complete Railway Deployment Steps

1. **Login to Railway:**
   ```bash
   railway login
   ```

2. **Create and deploy project:**
   ```bash
   railway new earnings-predictor
   railway up --detach
   ```

3. **Set environment variables (if needed):**
   ```bash
   railway variables set PYTHON_VERSION=3.9.18
   railway variables set PORT=8000
   ```

4. **Get your app URL:**
   ```bash
   railway status
   ```

5. **Initialize data:**
   ```bash
   railway run python data_pipeline.py
   railway run python train_model.py
   ```

## Alternative: Use Railway Dashboard Only

If CLI continues to have issues:

1. Push code to GitHub
2. Go to Railway dashboard
3. "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway handles everything automatically
6. Use the provided URL for your API

## Environment Variables to Set in Railway

In the Railway dashboard → Variables tab:
- `PYTHON_VERSION`: `3.9.18`
- `PORT`: `8000`
- `ENVIRONMENT`: `production`

The `railway.json` and `Procfile` files will handle the rest of the configuration automatically.