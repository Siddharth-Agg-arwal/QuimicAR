# Chemistry AR API - Deployment Guide

This guide provides step-by-step instructions for deploying the Chemistry AR FastAPI application to various platforms.

## Prerequisites

- Git repository with your code
- Python 3.11+
- Basic knowledge of the deployment platform you choose

## Project Structure

```
chemistry-augmented-reality/
├── api/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   └── test_api.py      # API tests
├── chemistry_ar/        # Core application logic
├── requirements.txt     # Python dependencies
└── .gitignore
```

## Deployment Options

### Option 1: Docker Deployment (Recommended)

#### 1.1 Create Dockerfile

Create `Dockerfile` in the `chemistry-augmented-reality/` directory:

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY chemistry_ar chemistry_ar
COPY api api

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 1.2 Create .dockerignore

Create `.dockerignore` in the `chemistry-augmented-reality/` directory:

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
venv
.env
.git
.gitignore
*.md
user_database.json
```

#### 1.3 Build and Run

```bash
# Build the Docker image
docker build -t chemistry-ar-api .

# Run the container
docker run -p 8000:8000 chemistry-ar-api

# Test the API
curl http://localhost:8000/
```

### Option 2: Railway Deployment

Railway offers easy deployment with automatic HTTPS and domain.

#### 2.1 Prepare Files

Create `railway.toml` in `chemistry-augmented-reality/`:

```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "cd chemistry-augmented-reality && python -m uvicorn api.main:app --host 0.0.0.0 --port $PORT"
```

#### 2.2 Deploy Steps

1. Go to [Railway.app](https://railway.app/)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect Python and deploy
5. Your API will be live at `https://your-app.railway.app`

### Option 3: Render Deployment

Render provides free tier hosting with automatic SSL.

#### 3.1 Create render.yaml

Create `render.yaml` in the root directory:

```yaml
services:
  - type: web
    name: chemistry-ar-api
    env: python
    region: oregon
    buildCommand: "pip install -r requirements.txt"
    startCommand: "cd chemistry-augmented-reality && python -m uvicorn api.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

#### 3.2 Deploy Steps

1. Go to [Render.com](https://render.com/)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Render will auto-detect the `render.yaml` and deploy
5. Your API will be live with HTTPS

### Option 4: Google Cloud Run

Cloud Run offers serverless container deployment.

#### 4.1 Prerequisites

```bash
# Install Google Cloud SDK
# Login to Google Cloud
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

#### 4.2 Deploy

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/chemistry-ar-api

# Deploy to Cloud Run
gcloud run deploy chemistry-ar-api \
  --image gcr.io/YOUR_PROJECT_ID/chemistry-ar-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000
```

### Option 5: AWS Elastic Beanstalk

#### 5.1 Create Procfile

Create `Procfile` in `chemistry-augmented-reality/`:

```
web: cd chemistry-augmented-reality && uvicorn api.main:app --host 0.0.0.0 --port 8000
```

#### 5.2 Deploy

```bash
# Install EB CLI
pip install awsebcli

# Initialize EB application
eb init -p python-3.11 chemistry-ar-api

# Create environment and deploy
eb create chemistry-ar-env
eb open
```

### Option 6: Heroku

#### 6.1 Create Procfile

Create `Procfile` in the root directory:

```
web: cd chemistry-augmented-reality && uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

#### 6.2 Create runtime.txt

Create `runtime.txt`:

```
python-3.11.2
```

#### 6.3 Deploy

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Deploy
git push heroku main

# Open app
heroku open
```

## Environment Variables

If you need environment variables for production:

### For Docker:

```bash
docker run -p 8000:8000 \
  -e DEBUG=False \
  chemistry-ar-api
```

### For Cloud Platforms:

Add these via the platform's dashboard:
- `DEBUG=False` - Disable debug mode in production
- `ALLOWED_ORIGINS=https://your-frontend.com` - CORS settings

## Post-Deployment Testing

Test your deployed API:

```bash
# Health check
curl https://your-api-url.com/

# Get levels
curl https://your-api-url.com/levels

# Set level
curl -X POST https://your-api-url.com/set_level/1

# Process frame (with an image file)
curl -X POST https://your-api-url.com/process_frame \
  -F "file=@test_image.jpg" \
  --output result.jpg
```

## Monitoring and Logs

### Docker:
```bash
docker logs <container_id>
```

### Railway:
- View logs in Railway dashboard

### Render:
- View logs in Render dashboard

### Google Cloud Run:
```bash
gcloud logging read "resource.type=cloud_run_revision"
```

## Troubleshooting

### Common Issues:

1. **ModernGL requires display**: The API uses headless OpenGL context, ensure your deployment platform supports it
   - Solution: Use platforms with full Linux support (not Alpine-based containers)

2. **Port binding errors**: 
   - Ensure you're using `$PORT` environment variable in cloud platforms
   - Update start command to use the platform's port

3. **Import errors**:
   - Verify all dependencies are in `requirements.txt`
   - Check Python version compatibility

4. **Memory issues**:
   - Increase container memory allocation
   - Consider using background workers for heavy processing

## Scaling Considerations

- **Horizontal Scaling**: Most platforms support auto-scaling based on traffic
- **Load Balancing**: Automatically handled by cloud platforms
- **Caching**: Consider adding Redis for session/state management
- **CDN**: Use CDN for static assets if you add a frontend

## Security Best Practices

1. **Use HTTPS**: All cloud platforms provide free SSL
2. **API Keys**: Add authentication for production use
3. **Rate Limiting**: Implement rate limiting to prevent abuse
4. **CORS**: Configure allowed origins properly
5. **Keep Dependencies Updated**: Regularly update packages

## Cost Estimates

- **Railway**: Free tier available, then ~$5/month
- **Render**: Free tier available, then ~$7/month
- **Google Cloud Run**: Pay per use, ~$5-10/month for light traffic
- **AWS Elastic Beanstalk**: ~$12+/month
- **Heroku**: ~$7/month (Eco dyno)

## Next Steps

After deployment:
1. Set up custom domain
2. Configure monitoring (Sentry, DataDog, etc.)
3. Set up CI/CD pipeline
4. Add authentication layer
5. Implement caching strategy
6. Create frontend application to consume the API

## Support

For issues or questions:
- Check API logs for errors
- Verify all environment variables are set
- Test locally with Docker before deploying
- Review platform-specific documentation
