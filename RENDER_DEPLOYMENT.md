# Render Deployment Guide for DDL Backend

This guide will walk you through deploying your Django application to Render, a modern cloud platform with a generous free tier.

## Why Render?

- ✅ **Free Tier Available**: Web services and PostgreSQL databases
- ✅ **Easy Deployment**: Simple Git-based deployment
- ✅ **Automatic SSL**: HTTPS certificates included
- ✅ **Built-in Monitoring**: Health checks and logging
- ✅ **No Credit Card Required**: For free tier usage

## Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, or Bitbucket)
3. **API Keys**: Have your ORS API Key and Mapbox Access Token ready

## Step-by-Step Deployment

### 1. Prepare Your Repository

Ensure your code is pushed to a Git repository:

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Create a New Web Service on Render

1. Go to [render.com](https://render.com) and sign in
2. Click **"New +"** → **"Web Service"**
3. Connect your Git repository
4. Select your repository and branch

### 3. Configure Your Web Service

**Basic Settings:**
- **Name**: `ddl-backend` (or your preferred name)
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `main` (or your default branch)
- **Root Directory**: Leave empty (if your Django app is in the root)

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
- **Start Command**: `gunicorn backend.wsgi:application`

### 4. Set Environment Variables

In the Render dashboard, go to **Environment** tab and add:

```bash
# Required
DJANGO_SECRET_KEY=your-very-secure-secret-key-here
ENVIRONMENT=production
DEBUG=false

# API Keys
ORS_API_KEY=your-openroute-service-api-key
MAPBOX_ACCESS_TOKEN=your-mapbox-access-token

# Optional
ALLOWED_HOSTS=your-app-name.onrender.com
```

### 5. Create a PostgreSQL Database

1. In Render dashboard, click **"New +"** → **"PostgreSQL"**
2. **Name**: `ddl-backend-db`
3. **Database**: `ddl_backend`
4. **User**: `ddl_backend_user`
5. **Plan**: `Free`
6. Click **"Create Database"**

### 6. Connect Database to Web Service

1. Go to your web service settings
2. In **Environment** tab, add:
   ```bash
   DATABASE_URL=postgresql://ddl_backend_user:password@hostname:port/ddl_backend
   ```
   (Render will provide the exact connection string)

### 7. Deploy Your Application

1. Click **"Create Web Service"**
2. Render will automatically:
   - Build your application
   - Install dependencies
   - Collect static files
   - Deploy your app

### 8. Run Database Migrations

After deployment, run migrations:

1. Go to your web service dashboard
2. Click **"Shell"** tab
3. Run:
   ```bash
   python manage.py migrate
   ```

### 9. Create Superuser (Optional)

In the same shell:
```bash
python manage.py createsuperuser
```

## Alternative: Using render.yaml (Recommended)

For easier setup, you can use the included `render.yaml` file:

1. **Push your code** with the `render.yaml` file
2. **Create a Blueprint** on Render:
   - Go to **"New +"** → **"Blueprint"**
   - Connect your repository
   - Render will automatically detect and use `render.yaml`

## Verification

### Check Your Deployment

1. **Health Check**: Visit `https://your-app-name.onrender.com/health/`
2. **Admin Panel**: Visit `https://your-app-name.onrender.com/admin/`
3. **API Endpoints**: Test your API at `https://your-app-name.onrender.com/api/`

### View Logs

1. Go to your web service dashboard
2. Click **"Logs"** tab to view real-time logs

## Render-Specific Features

### 1. **Automatic Deployments**
- Deploys automatically on every Git push
- Can be disabled in settings if needed

### 2. **Health Checks**
- Render automatically monitors your `/health/` endpoint
- Service restarts if health checks fail

### 3. **SSL Certificates**
- Automatic HTTPS certificates
- Custom domains supported

### 4. **Environment Variables**
- Set via dashboard or `render.yaml`
- Secure storage of sensitive data

### 5. **Logging**
- Centralized logging in dashboard
- Log retention based on plan

## Free Tier Limitations

### Web Service
- **Sleep**: Services sleep after 15 minutes of inactivity
- **Cold Start**: ~30 seconds to wake up
- **Bandwidth**: 100GB/month
- **Build Time**: 90 minutes/month

### PostgreSQL
- **Storage**: 1GB
- **Connections**: 97 concurrent connections
- **Backups**: 7 days retention

## Scaling and Upgrades

### Upgrade to Paid Plans
- **Starter**: $7/month - No sleep, more resources
- **Standard**: $25/month - Better performance
- **Pro**: $85/month - High availability

### Custom Domains
1. Add your domain in **Settings** → **Custom Domains**
2. Update DNS records as instructed
3. Update `ALLOWED_HOSTS` environment variable

## Troubleshooting

### Common Issues

1. **Build Fails**:
   - Check build logs in dashboard
   - Ensure all dependencies are in `requirements.txt`

2. **Database Connection Issues**:
   - Verify `DATABASE_URL` is set correctly
   - Check database status in dashboard

3. **Static Files Not Loading**:
   - Ensure `collectstatic` runs during build
   - Check WhiteNoise configuration

4. **Service Sleeps**:
   - Free tier services sleep after inactivity
   - Consider upgrading to paid plan for always-on service

### Useful Commands

```bash
# Access shell (via Render dashboard)
python manage.py shell
python manage.py migrate
python manage.py collectstatic --noinput

# Check service status
# (via Render dashboard)
```

## Monitoring and Maintenance

### 1. **Health Monitoring**
- Render monitors your health endpoint
- Set up external monitoring for better coverage

### 2. **Database Backups**
- Automatic backups on paid plans
- Manual backups available via dashboard

### 3. **Performance Monitoring**
- Built-in metrics in dashboard
- Consider external APM tools for detailed monitoring

## Security Best Practices

1. **Environment Variables**: Never commit secrets to Git
2. **HTTPS**: Always use HTTPS in production
3. **Database**: Use strong passwords and limit access
4. **Updates**: Keep dependencies updated
5. **Monitoring**: Set up alerts for critical issues

## Cost Optimization

### Free Tier Tips
- Use efficient database queries
- Optimize static file serving
- Monitor bandwidth usage
- Consider caching strategies

### Paid Tier Benefits
- No sleep mode
- Better performance
- More resources
- Priority support

## Next Steps

1. **Set up monitoring**: Consider external monitoring tools
2. **Implement caching**: Redis or similar for better performance
3. **Set up CI/CD**: Automated testing and deployment
4. **Backup strategy**: Regular database backups
5. **Performance optimization**: Monitor and optimize as needed

## Support

- **Render Documentation**: [render.com/docs](https://render.com/docs)
- **Community**: [render.com/community](https://render.com/community)
- **Support**: Available via dashboard

Your Django application is now successfully deployed on Render! 🎉

## Quick Reference

- **Dashboard**: [dashboard.render.com](https://dashboard.render.com)
- **Documentation**: [render.com/docs](https://render.com/docs)
- **Status**: [status.render.com](https://status.render.com)
