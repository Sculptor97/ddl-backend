# DDL Backend - HOS Trip Planner API

A Django REST API backend for planning trucking trips with Hours of Service (HOS) compliance, implementing FMCSA regulations.

## Tech Stack

- **Backend**: Python 3.11+, Django, Django REST Framework
- **Dependency Manager**: pipenv (always latest versions)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Deployment**: Render (with free tier support)
- **HTTP Client**: requests
- **External APIs**: OpenRouteService, Mapbox

## Project Structure

```
ddl-backend/
├── backend/                 # Django project settings
│   ├── settings.py         # Django configuration
│   ├── urls.py             # Main URL routing
│   ├── wsgi.py             # WSGI configuration
│   └── asgi.py             # ASGI configuration
├── trips/                  # Django app
│   ├── models.py           # Driver and DailyRod models
│   ├── views.py            # API endpoints
│   ├── serializers.py      # DRF serializers
│   ├── urls.py             # App URL routing
│   ├── admin.py            # Django admin
│   ├── ors_client.py       # OpenRouteService client
│   └── hos.py              # HOS scheduler
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
├── Pipfile                 # Pipenv dependencies
├── Procfile                # Render deployment config
├── render.yaml             # Render blueprint config
├── env.example             # Environment variables template
├── deploy.sh               # Deployment script
├── RENDER_DEPLOYMENT.md    # Render deployment guide
└── README.md
```

## Features

- **HOS Compliance**: Implements FMCSA regulations including:
  - 11-hour maximum driving per day
  - 14-hour on-duty window
  - 30-minute break after 8 hours driving
  - 70-hour maximum in rolling 8 days
  - 34-hour restart when needed
- **Route Planning**: Integration with OpenRouteService API for real-time routing
- **Driver Management**: Track drivers and their HOS records
- **RESTful API**: Clean API endpoints for trip planning
- **Health Monitoring**: Built-in health check endpoint
- **Production Ready**: Configured for deployment on Render

## Setup Instructions

### Prerequisites
- Python 3.11+
- pipenv (install with `pip install pipenv`)
- Git repository access

### Local Development Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ddl-backend
   ```

2. **Install Python dependencies**:
   ```bash
   pipenv install
   pipenv shell
   ```

3. **Set up environment variables**:
   ```bash
   cp env.example .env
   ```
   Edit `.env` with your API keys:
   ```
   DJANGO_SECRET_KEY=your-secret-key-here
   ORS_API_KEY=your-openroute-service-api-key
   MAPBOX_ACCESS_TOKEN=your-mapbox-access-token
   DEBUG=True
   ENVIRONMENT=development
   ```

4. **Run Django migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create superuser (optional)**:
   ```bash
   python manage.py createsuperuser
   ```

6. **Start Django development server**:
   ```bash
   python manage.py runserver
   ```
   API will be available at `http://localhost:8000`

### Production Deployment

For production deployment on Render, see the detailed [Render Deployment Guide](RENDER_DEPLOYMENT.md).

## API Usage

### Plan Trip Endpoint

**POST** `/api/plan-trip/`

**Request Body**:
```json
{
  "current_location": [-74.0059, 40.7128],
  "pickup": [-73.9352, 40.7306],
  "dropoff": [-73.9857, 40.7484],
  "driver_id": 1,
  "current_cycle_used_hours": 0.0
}
```

**Response**:
```json
{
  "route": {
    "distance": 12.5,
    "duration": 1.2,
    "geometry": {
      "type": "LineString",
      "coordinates": [[-74.0059, 40.7128], [-73.9352, 40.7306], [-73.9857, 40.7484]]
    }
  },
  "daily_logs": [
    {
      "date": "2024-01-15",
      "entries": [
        {
          "start_time": "08:00",
          "end_time": "09:00",
          "status": "on_duty",
          "location": "Pickup Location",
          "duration": 1.0
        },
        {
          "start_time": "09:00",
          "end_time": "10:12",
          "status": "driving",
          "location": "Route to Dropoff (12.5 mi)",
          "duration": 1.2
        },
        {
          "start_time": "10:12",
          "end_time": "11:12",
          "status": "on_duty",
          "location": "Dropoff Location",
          "duration": 1.0
        }
      ],
      "totals": {
        "driving_hours": 1.2,
        "on_duty_hours": 3.2,
        "off_duty_hours": 0.0
      }
    }
  ],
  "total_distance": 12.5,
  "total_duration": 1.2
}
```

## HOS Regulations Implemented

### FMCSA Compliance Rules

1. **11-Hour Driving Limit**: Maximum 11 hours driving per day
2. **14-Hour On-Duty Window**: Maximum 14 hours on-duty per day
3. **30-Minute Break**: Required after 8 hours of driving
4. **70-Hour Rule**: Maximum 70 hours on-duty in rolling 8-day period
5. **34-Hour Restart**: Required when 70-hour limit is exceeded
6. **10-Hour Off-Duty**: Required between duty periods

### Status Types
- **Driving**: Time spent operating the vehicle (orange)
- **On Duty**: Time spent working but not driving (blue)
- **Off Duty**: Rest time (green)

## Development

### API Endpoints
- **Health Check**: `GET /health/` - Service health status
- **Admin Panel**: `GET /admin/` - Django admin interface
- **API Base**: `GET /api/` - API endpoints
- **Plan Trip**: `POST /api/plan-trip/` - Main trip planning endpoint

### Development Tools
- Django admin available at `/admin/`
- Use `python manage.py shell` for database exploration
- Logs available in `logs/django.log` (local development)

### Testing
```bash
# Run Django tests
python manage.py test

# Check deployment configuration
python manage.py check --deploy
```

## API Documentation

### Available Endpoints

- **`GET /health/`** - Health check endpoint
- **`GET /admin/`** - Django admin interface
- **`GET /api/drivers/`** - List all drivers
- **`GET /api/drivers/{id}/logs/`** - Get driver HOS logs
- **`POST /api/plan-trip/`** - Plan a trip with HOS compliance

### Authentication

Currently, the API is open for development. For production use, consider implementing:
- API key authentication
- JWT tokens
- OAuth2 integration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please create an issue in the repository.
