#!/bin/bash

# Earnings Predictor Deployment Script
# Automates deployment to various cloud platforms

set -e

echo "🚀 Earnings Predictor Deployment Script"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_requirements() {
    print_status "Checking requirements..."
    
    if ! command -v git &> /dev/null; then
        print_error "Git is required but not installed"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        print_error "Node.js/npm is required but not installed"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    print_success "All requirements satisfied"
}

# Build the application
build_app() {
    print_status "Building application..."
    
    # Install Python dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Install Node.js dependencies and build frontend
    print_status "Building frontend..."
    cd frontend
    npm install
    npm run build
    cd ..
    
    print_success "Application built successfully"
}

# Deploy to Railway
deploy_railway() {
    print_status "Deploying to Railway..."
    
    if ! command -v railway &> /dev/null; then
        print_status "Installing Railway CLI..."
        npm install -g @railway/cli
    fi
    
    railway login
    railway link
    railway up
    
    print_success "Deployed to Railway! 🚄"
    railway status
}

# Deploy to Vercel (Frontend only)
deploy_vercel() {
    print_status "Deploying frontend to Vercel..."
    
    if ! command -v vercel &> /dev/null; then
        print_status "Installing Vercel CLI..."
        npm install -g vercel
    fi
    
    cd frontend
    vercel --prod
    cd ..
    
    print_success "Frontend deployed to Vercel! ▲"
}

# Deploy to Render
deploy_render() {
    print_status "Setting up Render deployment..."
    
    # Create render.yaml if it doesn't exist
    if [ ! -f render.yaml ]; then
        cat > render.yaml << EOF
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
    autoDeploy: true
    
  - type: static
    name: earnings-predictor-frontend
    buildCommand: cd frontend && npm install && npm run build
    staticPublishPath: frontend/dist
    envVars:
      - key: NODE_VERSION
        value: 18
    autoDeploy: true
EOF
    fi
    
    print_success "Render configuration created"
    print_status "Push to GitHub and connect to Render manually:"
    print_status "1. Go to https://dashboard.render.com"
    print_status "2. Connect your GitHub repository"
    print_status "3. Render will automatically deploy using render.yaml"
}

# Deploy using Docker to any VPS
deploy_docker() {
    print_status "Preparing Docker deployment..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is required for this deployment method"
        exit 1
    fi
    
    # Build and test locally first
    print_status "Building Docker containers..."
    docker-compose -f docker-compose.prod.yml build
    
    # Create deployment package
    print_status "Creating deployment package..."
    mkdir -p deploy-package
    cp -r backend frontend docker-compose.prod.yml nginx.conf requirements.txt package.json deploy-package/
    
    # Create deployment script for VPS
    cat > deploy-package/vps-deploy.sh << 'EOF'
#!/bin/bash
echo "🐳 Starting VPS deployment..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    sudo apt install -y docker.io docker-compose
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
fi

# Stop existing containers
docker-compose -f docker-compose.prod.yml down

# Build and start new containers
docker-compose -f docker-compose.prod.yml up -d --build

# Initialize data
echo "Initializing data..."
docker-compose -f docker-compose.prod.yml exec -T backend python data_pipeline.py
docker-compose -f docker-compose.prod.yml exec -T backend python train_model.py

echo "✅ Deployment complete!"
echo "Frontend: http://$(curl -s ipinfo.io/ip):80"
echo "Backend: http://$(curl -s ipinfo.io/ip):8000"
EOF
    
    chmod +x deploy-package/vps-deploy.sh
    
    print_success "Docker deployment package created in ./deploy-package/"
    print_status "To deploy to VPS:"
    print_status "1. Copy deploy-package/ to your VPS"
    print_status "2. Run: ./vps-deploy.sh"
}

# Initialize data after deployment
init_data() {
    print_status "Initializing data..."
    
    read -p "Enter your backend URL (e.g., https://your-app.railway.app): " BACKEND_URL
    
    if [ -z "$BACKEND_URL" ]; then
        print_error "Backend URL is required"
        exit 1
    fi
    
    print_status "Triggering data pipeline via API..."
    
    # Try to trigger model retraining which includes data collection
    curl -X POST "$BACKEND_URL/api/predictions/model/retrain" || {
        print_warning "API call failed. You may need to initialize data manually."
    }
    
    print_success "Data initialization requested"
}

# Show deployment status
show_status() {
    print_status "Checking deployment status..."
    
    if [ -f "frontend/.vercel/project.json" ]; then
        print_success "Vercel deployment detected"
    fi
    
    if command -v railway &> /dev/null && railway status &> /dev/null; then
        print_success "Railway deployment detected"
        railway status
    fi
    
    if [ -f "render.yaml" ]; then
        print_success "Render configuration found"
    fi
    
    if [ -d "deploy-package" ]; then
        print_success "Docker deployment package ready"
    fi
}

# Main menu
show_menu() {
    echo ""
    echo "Choose deployment option:"
    echo "1. 🚄 Railway (Backend)"
    echo "2. ▲  Vercel (Frontend)"
    echo "3. 🎨 Render (Full Stack)"
    echo "4. 🐳 Docker (VPS)"
    echo "5. 📊 Initialize Data"
    echo "6. 📈 Show Status"
    echo "7. 🔧 Build Only"
    echo "8. ❌ Exit"
    echo ""
}

# Main script
main() {
    check_requirements
    
    if [ $# -eq 0 ]; then
        # Interactive mode
        while true; do
            show_menu
            read -p "Enter your choice (1-8): " choice
            
            case $choice in
                1)
                    build_app
                    deploy_railway
                    ;;
                2)
                    build_app
                    deploy_vercel
                    ;;
                3)
                    build_app
                    deploy_render
                    ;;
                4)
                    build_app
                    deploy_docker
                    ;;
                5)
                    init_data
                    ;;
                6)
                    show_status
                    ;;
                7)
                    build_app
                    ;;
                8)
                    print_success "Goodbye!"
                    exit 0
                    ;;
                *)
                    print_error "Invalid option"
                    ;;
            esac
            
            echo ""
            read -p "Press Enter to continue..."
        done
    else
        # Command line mode
        case $1 in
            railway)
                build_app
                deploy_railway
                ;;
            vercel)
                build_app
                deploy_vercel
                ;;
            render)
                build_app
                deploy_render
                ;;
            docker)
                build_app
                deploy_docker
                ;;
            init)
                init_data
                ;;
            status)
                show_status
                ;;
            build)
                build_app
                ;;
            *)
                echo "Usage: $0 [railway|vercel|render|docker|init|status|build]"
                exit 1
                ;;
        esac
    fi
}

# Run main function
main "$@"