# GCP Cloud Run Deployment Guide

[한국어 버전 (Korean Version)](GCP_DEPLOY.md)

## Overview

This guide explains how to deploy the Discord MCP Notifier to Google Cloud Platform (GCP) Cloud Run.

## Why Cloud Run?

- **Serverless**: No server management required
- **Auto-scaling**: Automatically scales up/down based on traffic
- **Cost-effective**: Pay only for what you use (free tier available)
- **HTTPS auto-configuration**: Automatic SSL certificate management
- **Container-based**: Standardized deployment using Docker

## 📋 Prerequisites

1. **GCP Account**
   - https://cloud.google.com/
   - $300 free credit for new users

2. **GCP Project**
   - Create a new project in GCP Console
   - Remember your project ID (e.g., `discord-mcp-notifier`)

3. **gcloud CLI Installation**
   ```bash
   # macOS
   brew install google-cloud-sdk

   # Ubuntu/Debian
   curl https://sdk.cloud.google.com | bash

   # Windows
   # See https://cloud.google.com/sdk/docs/install
   ```

4. **Docker Installation**
   ```bash
   # macOS
   brew install docker

   # Ubuntu/Debian
   sudo apt-get install docker.io

   # Windows
   # https://docs.docker.com/desktop/install/windows-install/
   ```

## 🚀 Deployment Steps

### 1. Authenticate gcloud CLI

```bash
# Login with Google account
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Example:
# gcloud config set project discord-mcp-notifier
```

### 2. Enable APIs

```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Container Registry API
gcloud services enable containerregistry.googleapis.com

# Enable Artifact Registry API (recommended)
gcloud services enable artifactregistry.googleapis.com
```

### 3. Build Docker Image

```bash
# Navigate to project directory
cd /path/to/016_discord_mcp

# Build Docker image
docker build -t discord-mcp-notifier .

# Verify build
docker images | grep discord-mcp-notifier
```

### 4. Push Docker Image to GCP

#### Method 1: Using Artifact Registry (Recommended)

```bash
# Create Artifact Registry repository
gcloud artifacts repositories create discord-mcp \
  --repository-format=docker \
  --location=us-central1 \
  --description="Discord MCP Notifier"

# Configure Docker authentication
gcloud auth configure-docker us-central1-docker.pkg.dev

# Tag image
docker tag discord-mcp-notifier \
  us-central1-docker.pkg.dev/YOUR_PROJECT_ID/discord-mcp/notifier:latest

# Push image
docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/discord-mcp/notifier:latest
```

#### Method 2: Using Container Registry (Legacy)

```bash
# Configure Docker authentication
gcloud auth configure-docker

# Tag image
docker tag discord-mcp-notifier gcr.io/YOUR_PROJECT_ID/discord-mcp-notifier:latest

# Push image
docker push gcr.io/YOUR_PROJECT_ID/discord-mcp-notifier:latest
```

### 5. Store Webhook URL in Secret Manager

```bash
# Enable Secret Manager API
gcloud services enable secretmanager.googleapis.com

# Create secret
echo -n "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL" | \
  gcloud secrets create discord-webhook-url \
    --data-file=-

# Verify secret
gcloud secrets describe discord-webhook-url
```

### 6. Deploy Cloud Run Service

#### Using Artifact Registry:

```bash
gcloud run deploy discord-mcp-notifier \
  --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/discord-mcp/notifier:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-secrets DISCORD_WEBHOOK_URL=discord-webhook-url:latest \
  --memory 256Mi \
  --cpu 1 \
  --max-instances 10 \
  --min-instances 0 \
  --timeout 60
```

#### Using Container Registry:

```bash
gcloud run deploy discord-mcp-notifier \
  --image gcr.io/YOUR_PROJECT_ID/discord-mcp-notifier:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-secrets DISCORD_WEBHOOK_URL=discord-webhook-url:latest \
  --memory 256Mi \
  --cpu 1 \
  --max-instances 10 \
  --min-instances 0 \
  --timeout 60
```

**Option Explanations:**
- `--platform managed`: Use fully managed Cloud Run
- `--region us-central1`: US Central region (or use `asia-northeast3` for Seoul)
- `--allow-unauthenticated`: Allow access without authentication (public API)
- `--set-secrets`: Inject environment variables from Secret Manager
- `--memory 256Mi`: Allocate 256MB memory
- `--cpu 1`: Allocate 1 CPU
- `--max-instances 10`: Maximum 10 instances
- `--min-instances 0`: Minimum 0 instances (cost savings)
- `--timeout 60`: Request timeout 60 seconds

### 7. Verify Deployment

After deployment, Cloud Run provides a service URL:

```
Service [discord-mcp-notifier] revision [discord-mcp-notifier-00001-abc] has been deployed and is serving 100 percent of traffic.
Service URL: https://discord-mcp-notifier-XXXX-uc.a.run.app
```

#### Health Check Test:

```bash
curl https://discord-mcp-notifier-XXXX-uc.a.run.app/

# Response:
# {"status":"healthy","service":"discord-mcp-notifier"}
```

#### Notification Test:

```bash
curl -X POST https://discord-mcp-notifier-XXXX-uc.a.run.app/notify \
  -H "Content-Type: application/json" \
  -d '{
    "message_type": "task_complete",
    "project_name": "GCP Deployment Test",
    "details": "Cloud Run deployment successful!",
    "metadata": {
      "Region": "us-central1",
      "Memory": "256Mi"
    }
  }'

# Response:
# {"status":"success"}
```

## 🔄 Update and Redeploy

To redeploy after code changes:

```bash
# 1. Rebuild Docker image
docker build -t discord-mcp-notifier .

# 2. Tag image (change version number)
docker tag discord-mcp-notifier \
  us-central1-docker.pkg.dev/YOUR_PROJECT_ID/discord-mcp/notifier:v1.1

# 3. Push image
docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/discord-mcp/notifier:v1.1

# 4. Update Cloud Run service
gcloud run deploy discord-mcp-notifier \
  --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/discord-mcp/notifier:v1.1 \
  --platform managed \
  --region us-central1
```

## 📊 Monitoring and Logs

### View Logs

```bash
# Stream logs in real-time
gcloud run services logs tail discord-mcp-notifier \
  --region us-central1 \
  --follow

# Read recent logs
gcloud run services logs read discord-mcp-notifier \
  --region us-central1 \
  --limit 50
```

### Monitoring in GCP Console

1. GCP Console → Cloud Run
2. Click `discord-mcp-notifier` service
3. **Metrics** tab: View request count, response time, error rate, etc.
4. **Logs** tab: View detailed logs
5. **Revisions** tab: Deployment history and version management

## 💰 Cost Optimization

### Free Tier

Cloud Run provides the following free monthly usage:

- **CPU**: 180,000 vCPU-seconds
- **Memory**: 360,000 GiB-seconds
- **Requests**: 2 million
- **Network Egress**: 1 GB (North America region)

### Cost Saving Tips

1. **Set min instances to 0**: No charges when not in use
2. **Optimize memory**: Allocate only what's needed (256Mi is sufficient)
3. **Set timeout**: Prevent unnecessarily long timeouts
4. **Choose region**: Select nearest region

### Cost Estimation

**Scenario**: 100 notifications per day (3,000 per month)

- **Requests**: 3,000 → Free (within 2 million)
- **CPU/Memory**: ~1 second per request → Free (within 180,000 seconds)
- **Network**: Negligible → Free

**Conclusion**: Most personal/small projects can operate within the free tier!

## 🔒 Security Configuration

### 1. Add Authentication (Optional)

To allow only authenticated requests:

```bash
# Require authentication
gcloud run services update discord-mcp-notifier \
  --region us-central1 \
  --no-allow-unauthenticated

# Grant permissions to service account
gcloud run services add-iam-policy-binding discord-mcp-notifier \
  --region us-central1 \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.invoker"
```

### 2. Add API Key (Optional)

To add simple API key authentication, modify the code:

```python
# Add to app.py
import os

API_KEY = os.getenv("API_KEY", "your-secret-api-key")

@app.before_request
def check_api_key():
    if request.endpoint != 'health_check':
        api_key = request.headers.get("X-API-Key")
        if api_key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
```

Add API Key to Secret Manager:

```bash
echo -n "your-secret-api-key" | \
  gcloud secrets create api-key \
    --data-file=-

# Update service
gcloud run deploy discord-mcp-notifier \
  --set-secrets API_KEY=api-key:latest \
  --update-secrets DISCORD_WEBHOOK_URL=discord-webhook-url:latest
```

## 🧪 CI/CD Pipeline (Optional)

Automated deployment using GitHub Actions:

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches:
      - main

env:
  PROJECT_ID: YOUR_PROJECT_ID
  SERVICE_NAME: discord-mcp-notifier
  REGION: us-central1

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v1
      with:
        service_account_key: ${{ secrets.GCP_SA_KEY }}
        project_id: ${{ env.PROJECT_ID }}

    - name: Configure Docker
      run: gcloud auth configure-docker us-central1-docker.pkg.dev

    - name: Build Docker image
      run: docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/discord-mcp/notifier:$GITHUB_SHA .

    - name: Push Docker image
      run: docker push us-central1-docker.pkg.dev/$PROJECT_ID/discord-mcp/notifier:$GITHUB_SHA

    - name: Deploy to Cloud Run
      run: |
        gcloud run deploy $SERVICE_NAME \
          --image us-central1-docker.pkg.dev/$PROJECT_ID/discord-mcp/notifier:$GITHUB_SHA \
          --platform managed \
          --region $REGION \
          --allow-unauthenticated
```

## 🔍 Troubleshooting

### Issue 1: "Permission denied" error

```bash
# Grant necessary permissions to service account
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"
```

### Issue 2: Docker image push fails

```bash
# Reconfigure Docker authentication
gcloud auth configure-docker us-central1-docker.pkg.dev

# Verify login
gcloud auth list
```

### Issue 3: Cannot access secrets

```bash
# Grant secret access permission to service account
gcloud secrets add-iam-policy-binding discord-webhook-url \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## 📞 Support

- **GCP Documentation**: https://cloud.google.com/run/docs
- **GitHub Issues**: https://github.com/davidlikescat/016_discord_mcp/issues
- **Discord Community**: (Coming soon)

---

**Created by**: Discord MCP Notifier Project
**Date**: 2025-10-27
