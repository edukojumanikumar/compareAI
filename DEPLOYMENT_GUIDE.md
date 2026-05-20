# Deployment Guide - Room Inspection Platform

## Local Deployment

### Option 1: Direct Python Execution

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run server
python app.py

# 3. Access API
# http://localhost:8000/docs
```

**Pros**: Simple, fast development
**Cons**: Requires Python installed, no isolation

---

## Docker Deployment

### Option 2: Docker Container

```bash
# 1. Build image
docker build -t room-inspection:latest .

# 2. Run container
docker run -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  room-inspection:latest

# 3. Access API
# http://localhost:8000/docs
```

**Pros**: Isolated environment, consistent across systems
**Cons**: Requires Docker installed

---

### Option 3: Docker Compose (Recommended)

```bash
# 1. Run services
docker-compose up -d

# 2. Check status
docker-compose ps

# 3. View logs
docker-compose logs -f

# 4. Stop services
docker-compose down
```

**Pros**: One-command setup, health checks, volume management
**Cons**: Requires Docker and Docker Compose

---

## Cloud Deployment

### AWS Deployment

#### Option A: Elastic Container Service (ECS)

```bash
# 1. Create ECR repository
aws ecr create-repository --repository-name room-inspection

# 2. Push image
docker tag room-inspection:latest <AWS_ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/room-inspection:latest
docker push <AWS_ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/room-inspection:latest

# 3. Create ECS cluster, task definition, service
# (Use AWS Console or CloudFormation)

# 4. Configure load balancer, auto-scaling
```

#### Option B: Elastic Beanstalk

```bash
# 1. Install EB CLI
pip install awsebcli

# 2. Initialize
eb init -p docker room-inspection

# 3. Create environment
eb create room-inspection-env

# 4. Deploy
eb deploy
```

#### Option C: App Runner (Simplest)

```bash
# 1. Push to ECR (same as above)

# 2. Use AWS App Runner console:
#    - Select ECR image
#    - Configure port 8000
#    - Deploy
```

---

### Azure Deployment

#### Option A: Container Instances (ACI)

```bash
# 1. Create resource group
az group create --name room-inspection --location eastus

# 2. Create container
az container create \
  --resource-group room-inspection \
  --name room-inspection-api \
  --image room-inspection:latest \
  --ports 8000 \
  --cpu 2 --memory 4
```

#### Option B: App Service with Docker

```bash
# 1. Create App Service plan
az appservice plan create \
  --name room-inspection-plan \
  --resource-group room-inspection \
  --sku B2 --is-linux

# 2. Create web app
az webapp create \
  --resource-group room-inspection \
  --plan room-inspection-plan \
  --name room-inspection-api \
  --deployment-container-image-name-user room-inspection:latest
```

#### Option C: Azure Container Apps

```bash
# 1. Create environment
az containerapp env create \
  --name room-inspection-env \
  --resource-group room-inspection

# 2. Create container app
az containerapp create \
  --name room-inspection-api \
  --resource-group room-inspection \
  --environment room-inspection-env \
  --image room-inspection:latest \
  --target-port 8000
```

---

### Google Cloud Deployment

#### Cloud Run (Easiest)

```bash
# 1. Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/room-inspection

# 2. Deploy to Cloud Run
gcloud run deploy room-inspection \
  --image gcr.io/PROJECT_ID/room-inspection \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --cpu 2
```

---

## Environment Setup

### Environment Variables

Create `.env` file:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO

# Image Settings
MAX_FILE_SIZE_MB=50
UPLOAD_DIR=/app/uploads

# Processing
BLUR_THRESHOLD=100
BRIGHTNESS_MIN=30
BRIGHTNESS_MAX=225

# Status Thresholds
PASS_THRESHOLD=90
MINOR_ISSUES_THRESHOLD=75
REVIEW_THRESHOLD=60
```

### Using Environment Variables

```python
# In app.py or config.py
import os
from dotenv import load_dotenv

load_dotenv()

API_PORT = int(os.getenv("API_PORT", 8000))
BLUR_THRESHOLD = int(os.getenv("BLUR_THRESHOLD", 100))
```

---

## Monitoring

### Health Checks

```bash
# Health endpoint
curl http://localhost:8000/health

# Swagger docs available
curl http://localhost:8000/docs
```

### Logging

```bash
# Docker logs
docker logs <container_id>

# Docker Compose logs
docker-compose logs -f room-inspection-api

# Follow specific service
docker-compose logs -f --tail=100
```

### Performance Monitoring

```bash
# Docker stats
docker stats <container_id>

# Check memory/CPU usage
```

---

## Storage Configuration

### Local Storage (Current)

Default location: `./uploads/`

Files are temporary, cleaned up after comparison.

### Future: AWS S3

```python
import boto3

s3 = boto3.client('s3')
s3.upload_file('local_file', 'bucket', 'object_key')
```

### Future: Azure Blob Storage

```python
from azure.storage.blob import BlobServiceClient

client = BlobServiceClient.from_connection_string(connection_string)
```

---

## Scaling

### Horizontal Scaling

**Multiple Containers with Load Balancer:**

```yaml
# docker-compose.yml example
version: '3.8'
services:
  api-1:
    build: .
    ports: ["8001:8000"]
  api-2:
    build: .
    ports: ["8002:8000"]
  api-3:
    build: .
    ports: ["8003:8000"]
  
  nginx:
    image: nginx:latest
    ports: ["80:80"]
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### Vertical Scaling

Adjust container resources:

```dockerfile
# In Dockerfile
# Increase base resources
# Use more efficient algorithms
# Cache computations
```

---

## Database Integration (Phase 2)

### PostgreSQL Setup

```bash
# Docker Compose with PostgreSQL
docker-compose up -d

# Connect to database
psql -h localhost -U postgres -d room_inspection
```

### Environment Variables for DB

```env
DATABASE_URL=postgresql://user:password@localhost/room_inspection
DATABASE_POOL_SIZE=5
DATABASE_ECHO=false
```

---

## SSL/HTTPS

### Using Caddy Reverse Proxy

```bash
# Caddy automatically manages SSL certificates

docker run -p 443:443 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  caddy caddy reverse-proxy --from api.example.com --to room-inspection-api:8000
```

### Using Let's Encrypt + Nginx

```nginx
server {
    listen 443 ssl http2;
    server_name api.example.com;
    
    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;
    
    location / {
        proxy_pass http://room-inspection-api:8000;
    }
}
```

---

## Backup & Recovery

### Backup Uploads

```bash
# Backup local uploads
tar -czf uploads_backup.tar.gz uploads/

# Backup Docker volumes
docker run --rm \
  -v room_inspection_uploads:/data \
  -v $(pwd):/backup \
  ubuntu tar czf /backup/uploads_backup.tar.gz /data
```

### Backup Database (Phase 2)

```bash
# PostgreSQL backup
pg_dump -U postgres room_inspection > backup.sql

# Restore
psql -U postgres room_inspection < backup.sql
```

---

## Maintenance

### Container Updates

```bash
# Pull latest code
git pull origin main

# Rebuild image
docker-compose build

# Restart services
docker-compose up -d --force-recreate
```

### Log Rotation

```bash
# Docker daemon.json configuration
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs <container_id>

# Verify image
docker images

# Check configuration
docker inspect <container_id>
```

### Port Already in Use

```bash
# Find process on port 8000
lsof -i :8000

# Use different port
docker run -p 9000:8000 room-inspection:latest
```

### Out of Memory

```bash
# Increase container memory
docker run -m 2g room-inspection:latest

# Or in docker-compose.yml
services:
  api:
    mem_limit: 2g
```

### Slow Processing

```bash
# Check CPU usage
docker stats

# Increase CPU allocation
docker run --cpus="2" room-inspection:latest
```

---

## Production Checklist

- [ ] Use environment variables for secrets
- [ ] Set up health checks
- [ ] Configure logging
- [ ] Enable HTTPS/SSL
- [ ] Set up monitoring/alerts
- [ ] Configure auto-scaling
- [ ] Implement rate limiting
- [ ] Add authentication
- [ ] Enable audit logging
- [ ] Set up backup strategy
- [ ] Document deployment process
- [ ] Test disaster recovery
- [ ] Load test the system
- [ ] Set up alerting
- [ ] Configure CDN (if needed)
- [ ] Enable CORS properly
- [ ] Use secrets management
- [ ] Set resource limits

---

## Deployment Flowchart

```
┌─────────────────┐
│  Code Update    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  Build Docker Image     │
│  (docker build)         │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Push to Registry       │
│  (ECR/Docker Hub/etc)   │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Deploy Container       │
│  (ECS/App Service/etc)  │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Health Checks          │
│  (Verify running)       │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Smoke Tests            │
│  (Quick validation)     │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Monitor & Alert        │
│  (Watch for issues)     │
└─────────────────────────┘
```

---

**Version**: 0.1.0  
**Type**: Deployment Guide  
**Last Updated**: May 20, 2026
