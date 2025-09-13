#!/bin/bash

# DDL Backend Deployment Script
set -e

echo "🚀 Starting DDL Backend deployment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please copy env.example to .env and configure it."
    exit 1
fi

# Load environment variables
source .env

# Check required environment variables
if [ -z "$DJANGO_SECRET_KEY" ] || [ "$DJANGO_SECRET_KEY" = "your-secret-key-here" ]; then
    echo "❌ DJANGO_SECRET_KEY not set or using default value"
    exit 1
fi

if [ -z "$ORS_API_KEY" ]; then
    echo "❌ ORS_API_KEY not set"
    exit 1
fi

if [ -z "$MAPBOX_ACCESS_TOKEN" ]; then
    echo "❌ MAPBOX_ACCESS_TOKEN not set"
    exit 1
fi

echo "✅ Environment variables validated"

# Create necessary directories
mkdir -p logs staticfiles media

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "🗄️  Running database migrations..."
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
echo "👤 Creating superuser (if needed)..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

# Run tests
echo "🧪 Running tests..."
python manage.py check --deploy

echo "✅ Deployment completed successfully!"
echo ""
echo "To start the application:"
echo "  Development: python manage.py runserver"
echo "  Production:  gunicorn --config gunicorn.conf.py backend.wsgi:application"
echo "  Docker:      docker-compose up -d"
echo ""
echo "Health check: http://localhost:8000/health/"
echo "Admin panel:  http://localhost:8000/admin/ (admin/admin123)"
