# Deployment Guide

This guide covers multiple deployment options for the Earnings Predictor application.

## 🚀 Quick Deploy Options

### Option 1: Vercel (Frontend) + Railway (Backend) - **RECOMMENDED**
- **Cost**: Free tier available
- **Setup Time**: 5-10 minutes
- **Best For**: Production use, automatic deployments

### Option 2: Docker + Cloud VPS
- **Cost**: $5-20/month (DigitalOcean, Linode)
- **Setup Time**: 10-15 minutes  
- **Best For**: Full control, custom scaling

### Option 3: Local Docker
- **Cost**: Free
- **Setup Time**: 2 minutes
- **Best For**: Testing, development

---

## 🌐 Option 1: Vercel + Railway (Recommended)

### Step 1: Deploy Backend to Railway

1. **Push to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy to Railway**:
   - Go to [railway.app](https://railway.app)
   - Sign up/login with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-detect Python and deploy

3. **Configure Railway Environment**:
   - In Railway dashboard → Variables tab:
   ```
   PYTHONPATH=/app
   PORT=8000
   ```

4. **Custom Start Command** (if needed):
   - In Railway dashboard → Settings → Deploy
   - Start Command: `cd backend && python main.py`

5. **Get Backend URL**:
   - Railway will provide a URL like: `https://your-app-production.up.railway.app`

### Step 2: Deploy Frontend to Vercel

1. **Configure Frontend Environment**:
   Create `frontend/.env.production`:
   ```
   VITE_API_BASE=https://your-app-production.up.railway.app
   ```

2. **Deploy to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Sign up/login with GitHub
   - Click "New Project"
   - Import your GitHub repository
   - Configure:
     - Framework: Vite
     - Root Directory: `frontend`
     - Build Command: `npm run build`
     - Output Directory: `dist`
   - Add Environment Variable: `VITE_API_BASE=https://your-backend-url`

3. **Deploy**:
   - Vercel will build and deploy automatically
   - Get your frontend URL: `https://your-app.vercel.app`

### Step 3: Initialize Data (One-time setup)

Since Railway doesn't persist files, you'll need to initialize data:

1. **Option A: Manual API calls** (after deployment):
   ```bash
   # Trigger data collection via API
   curl -X POST https://your-backend-url/api/predictions/model/retrain
   ```

2. **Option B: Use Railway CLI**:
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login and connect to your project
   railway login
   railway link
   
   # Run data pipeline
   railway run python data_pipeline.py
   railway run python train_model.py
   ```

---

## 🐳 Option 2: Docker + Cloud VPS

### Step 1: Prepare for Deployment

1. **Create production environment files**:

   `backend/.env.production`:
   ```
   API_HOST=0.0.0.0
   API_PORT=8000
   ENVIRONMENT=production
   ```

   `frontend/.env.production`:
   ```
   VITE_API_BASE=http://your-server-ip:8000
   ```

### Step 2: Deploy to VPS (DigitalOcean/Linode/AWS)

1. **Create a VPS**:
   - DigitalOcean: $5/month droplet
   - Linode: $5/month instance
   - AWS EC2: t2.micro (free tier)

2. **SSH into your server**:
   ```bash
   ssh root@your-server-ip
   ```

3. **Install Docker**:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install docker.io docker-compose -y
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

4. **Clone your repository**:
   ```bash
   git clone https://github.com/yourusername/finproj.git
   cd finproj
   ```

5. **Deploy with Docker Compose**:
   ```bash
   # Build and start services
   docker-compose up -d --build
   
   # Check status
   docker-compose ps
   
   # View logs
   docker-compose logs -f
   ```

6. **Initialize Data**:
   ```bash
   # Run data pipeline
   docker-compose exec backend python data_pipeline.py
   docker-compose exec backend python train_model.py
   ```

7. **Access Your App**:
   - Frontend: `http://your-server-ip:3000`
   - Backend: `http://your-server-ip:8000`

### Step 3: Set Up Domain (Optional)

1. **Configure DNS** (point your domain to server IP)

2. **Set up Nginx reverse proxy**:
   ```bash
   sudo apt install nginx
   ```

3. **Create Nginx config** (`/etc/nginx/sites-available/earnings-predictor`):
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       location / {
           proxy_pass http://localhost:3000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }

       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

4. **Enable site and restart Nginx**:
   ```bash
   sudo ln -s /etc/nginx/sites-available/earnings-predictor /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

---

## 🏠 Option 3: Local Docker (Development)

Perfect for testing before production deployment.

1. **Build and Run**:
   ```bash
   docker-compose up --build
   ```

2. **Initialize Data**:
   ```bash
   # In another terminal
   docker-compose exec backend python data_pipeline.py
   docker-compose exec backend python train_model.py
   ```

3. **Access Locally**:
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000

---

## 🛠 Advanced Deployment Configurations

### Render.com Alternative (Backend)

Create `render.yaml`:
```yaml
services:
  - type: web
    name: earnings-predictor-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: cd backend && python main.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.0
      - key: PORT
        value: 8000
```

### Netlify Alternative (Frontend)

Create `netlify.toml` in root:
```toml
[build]
  base = "frontend/"
  publish = "frontend/dist"
  command = "npm run build"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### Environment-Specific Configurations

Create `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - API_HOST=0.0.0.0
    restart: always

  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
      args:
        - VITE_API_BASE=https://your-api-domain.com
    ports:
      - "80:3000"
    depends_on:
      - backend
    restart: always
```

---

## 🔧 Deployment Checklist

### Before Deploying:

- [ ] Test application locally
- [ ] Set up GitHub repository
- [ ] Configure environment variables
- [ ] Test data pipeline and model training
- [ ] Review API endpoints

### After Deploying:

- [ ] Verify frontend loads correctly
- [ ] Test API endpoints
- [ ] Initialize data pipeline
- [ ] Train ML model
- [ ] Check model status endpoint
- [ ] Test predictions functionality
- [ ] Monitor application logs

### Production Monitoring:

- [ ] Set up error tracking (Sentry)
- [ ] Configure logging
- [ ] Set up uptime monitoring
- [ ] Plan for data updates (cron jobs)
- [ ] Set up backup strategy

---

## 🚨 Troubleshooting Common Issues

### Backend Issues:
```bash
# Check logs
docker-compose logs backend

# Common fixes
- Verify Python dependencies installed
- Check if model files exist
- Ensure data directory has write permissions
```

### Frontend Issues:
```bash
# Check build logs
docker-compose logs frontend

# Common fixes
- Verify VITE_API_BASE environment variable
- Check if backend is accessible
- Clear browser cache
```

### Data Pipeline Issues:
```bash
# Run manually to debug
docker-compose exec backend python data_pipeline.py --debug

# Common fixes
- Check internet connection
- Verify yfinance is working
- Reduce number of symbols if rate limited
```

---

## 💰 Cost Estimates

### Free Tier:
- **Vercel**: Free (hobby projects)
- **Railway**: $5/month after free tier
- **Total**: ~$5/month

### VPS Hosting:
- **DigitalOcean**: $5-20/month
- **Domain**: $10-15/year
- **SSL**: Free (Let's Encrypt)
- **Total**: ~$5-25/month

### Cloud Platform:
- **AWS**: $10-50/month (depending on usage)
- **Google Cloud**: $10-40/month
- **Azure**: $10-45/month

---

## 📈 Scaling Considerations

### For Higher Traffic:
1. **Use Redis** for caching predictions
2. **Add load balancer** for multiple backend instances
3. **Implement CDN** for frontend assets
4. **Use database** instead of CSV files
5. **Add queue system** for batch predictions

### For More Data:
1. **Use PostgreSQL** for historical data
2. **Implement data partitioning**
3. **Add background jobs** for data updates
4. **Use cloud storage** for model artifacts