# HOS Trip Planner

A full-stack web application for planning trucking trips with Hours of Service (HOS) compliance, implementing FMCSA regulations.

## Tech Stack

- **Backend**: Python 3.11+, Django, Django REST Framework
- **Dependency Manager**: pipenv (always latest versions)
- **Database**: PostgreSQL with psycopg
- **Frontend**: Vite + React + TypeScript
- **Maps**: Leaflet with OpenStreetMap tiles
- **HTTP Client**: axios (frontend), requests (backend)

## Project Structure

```
ddl-backend/
├── backend/                 # Django backend
│   ├── backend/            # Django project settings
│   ├── trips/              # Django app
│   │   ├── models.py       # Driver and DailyRod models
│   │   ├── views.py        # API endpoints
│   │   ├── serializers.py  # DRF serializers
│   │   ├── urls.py         # URL routing
│   │   ├── admin.py        # Django admin
│   │   ├── ors_client.py   # OpenRouteService client
│   │   └── hos.py          # HOS scheduler
│   ├── manage.py
│   └── env.example         # Environment variables template
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── MapView.tsx # Interactive map component
│   │   │   └── LogSheet.tsx # HOS log visualization
│   │   ├── App.tsx         # Main application
│   │   ├── main.tsx        # React entry point
│   │   └── index.css       # Global styles
│   ├── package.json
│   ├── vite.config.ts
│   └── env.example         # Frontend environment template
├── Pipfile                 # Python dependencies
└── README.md
```

## Features

### Backend Features
- **HOS Compliance**: Implements FMCSA regulations including:
  - 11-hour maximum driving per day
  - 14-hour on-duty window
  - 30-minute break after 8 hours driving
  - 70-hour maximum in rolling 8 days
  - 34-hour restart when needed
- **Route Planning**: Integration with OpenRouteService API (with mock fallback)
- **Driver Management**: Track drivers and their HOS records
- **RESTful API**: Clean API endpoints for trip planning

### Frontend Features
- **Interactive Map**: Visualize routes with waypoint markers
- **HOS Log Sheet**: Color-coded 24-hour grid showing duty status
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Planning**: Instant trip planning with HOS compliance

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL database
- pipenv (install with `pip install pipenv`)

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
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
   Edit `.env` with your database credentials and API keys:
   ```
   DJANGO_SECRET_KEY=your-secret-key-here
   DATABASE_URL=postgres://username:password@localhost:5432/hos_trip_planner
   ORS_API_KEY=your-openroute-service-api-key
   ```

4. **Set up PostgreSQL database**:
   ```sql
   CREATE DATABASE hos_trip_planner;
   ```

5. **Run Django migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser (optional)**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Start Django development server**:
   ```bash
   python manage.py runserver
   ```
   Backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

3. **Set up environment variables**:
   ```bash
   cp env.example .env
   ```
   Edit `.env` if needed (default should work):
   ```
   VITE_API_URL=http://localhost:8000/api
   ```

4. **Start development server**:
   ```bash
   npm run dev
   ```
   Frontend will be available at `http://localhost:3000`

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

### Backend Development
- Django admin available at `/admin/`
- API documentation available at `/api/`
- Use `python manage.py shell` for database exploration

### Frontend Development
- Hot reload enabled in development
- TypeScript strict mode enabled
- ESLint configured for code quality

### Testing
```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests
cd frontend
npm test
```

## Deployment

### Backend Deployment
1. Set `DEBUG=False` in production
2. Configure proper `ALLOWED_HOSTS`
3. Use production database
4. Set up static file serving
5. Configure CORS for production domain

### Frontend Deployment
1. Build production bundle: `npm run build`
2. Serve static files from `dist/` directory
3. Configure API URL for production backend

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
