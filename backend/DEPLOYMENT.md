# Clarity in Care - Deployment Guide

## 📋 Deployment Overview

This guide covers deploying the Clarity in Care backend to AWS cloud infrastructure for production use.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Internet / Frontend                       │
└──────────┬──────────────────────────────────────────────────┘
           │ HTTPS
           ▼
┌──────────────────────────────────────────────────────────────┐
│              AWS Application Load Balancer (ALB)             │
│                  Port 443 (SSL/TLS)                          │
└──────────┬──────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│           ECS Cluster / EC2 Auto Scaling Group              │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  FastAPI Server (Docker Container)                    │ │
│  │  - Port 8000                                           │ │
│  │  - Model Inference                                    │ │
│  │  - Image Processing                                  │ │
│  │  - API Endpoints                                     │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────┬──────────────┬───────────────┬────────────────────┘
           │              │               │
     ┌─────▼──────┐  ┌────▼──────┐  ┌───▼──────────┐
     │   AWS RDS  │  │  AWS S3   │  │  CloudWatch  │
     │ (Database) │  │ (Images)  │  │  (Logs)      │
     └────────────┘  └───────────┘  └──────────────┘
```

---

## 🚀 Step-by-Step Deployment

### Phase 1: AWS Setup

#### Step 1: Create AWS Account
1. Go to https://aws.amazon.com
2. Click "Create an AWS Account"
3. Complete account setup
4. Add payment method

#### Step 2: Create IAM User (for deployment)
1. Go to IAM Dashboard
2. Create new user: `clarity-deploy`
3. Attach policies:
   - `AmazonEC2FullAccess`
   - `AmazonS3FullAccess`
   - `AWSRDSFullAccess`
   - `CloudWatchLogsFullAccess`

#### Step 3: Create S3 Bucket
1. Go to S3 Dashboard
2. Create bucket: `clarity-in-care-images`
3. Block public access (keep data private)
4. Enable versioning for safety

#### Step 4: Create RDS Database (Optional)
For production, use managed database instead of SQLite:

1. Go to RDS Dashboard
2. Create database:
   - Engine: PostgreSQL 14
   - Instance: db.t3.micro
   - Storage: 20GB
   - Database name: `clarity_in_care`
   - Username: `admin`
   - Generate password (save it!)

3. Note the **Endpoint** (e.g., `db.xxxx.us-east-1.rds.amazonaws.com`)

---

### Phase 2: Docker Setup

#### Step 1: Push Docker Image to ECR (Elastic Container Registry)

```bash
# Create ECR repository
aws ecr create-repository --repository-name clarity-in-care --region us-east-1

# Get login token
aws ecr get-login-password --region us-east-1 | docker login \
  --username AWS \
  --password-stdin <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

# Build and tag image
docker build -t clarity-in-care:latest .
docker tag clarity-in-care:latest \
  <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/clarity-in-care:latest

# Push to ECR
docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/clarity-in-care:latest
```

---

### Phase 3: EC2 Deployment (Simple Option)

#### Step 1: Launch EC2 Instance

```bash
# Via AWS CLI
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name my-key-pair \
  --security-groups clarity-security-group \
  --region us-east-1
```

Or via AWS Console:
1. Go to EC2 Dashboard
2. Launch Instance
   - AMI: Ubuntu 22.04 LTS
   - Type: t3.medium
   - Storage: 50GB
   - Security Group: Allow 80, 443, 8000

#### Step 2: SSH into Instance

```bash
ssh -i my-key-pair.pem ubuntu@<INSTANCE_IP>
```

#### Step 3: Install Docker and Dependencies

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Step 4: Deploy Application

```bash
# Clone repository
git clone <your-repo-url>
cd Clarity-In-Care/backend

# Create .env file
cat > .env << 'EOF'
DEBUG=False
HOST=0.0.0.0
PORT=8000
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
AWS_REGION=us-east-1
S3_BUCKET_NAME=clarity-in-care-images
DATABASE_URL=postgresql://admin:password@db.xxxx.us-east-1.rds.amazonaws.com/clarity_in_care
MODEL_PATH=./models/dr_detection_model.pth
EOF

# Download trained model (if available)
aws s3 cp s3://clarity-models/dr_detection_model.pth ./models/

# Start services
docker-compose up -d

# Check status
docker-compose logs -f api
```

#### Step 5: Setup Nginx Reverse Proxy

```bash
# Install Nginx
sudo apt-get install -y nginx

# Create config
sudo cat > /etc/nginx/sites-available/clarity << 'EOF'
server {
    listen 80;
    server_name clarity.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/clarity /etc/nginx/sites-enabled/clarity
sudo nginx -t
sudo systemctl restart nginx
```

#### Step 6: Setup SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d clarity.example.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

---

### Phase 4: ECS Deployment (Scalable Option)

For production with high traffic:

#### Step 1: Create ECS Cluster

```bash
aws ecs create-cluster --cluster-name clarity-cluster
```

#### Step 2: Create Task Definition

Create `task-definition.json`:

```json
{
  "family": "clarity-task",
  "networkMode": "awsvpc",
  "containerDefinitions": [
    {
      "name": "clarity-api",
      "image": "<ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/clarity-in-care:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "hostPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "DEBUG", "value": "False"},
        {"name": "AWS_REGION", "value": "us-east-1"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/clarity",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ],
  "executionRoleArn": "arn:aws:iam::<ACCOUNT_ID>:role/ecsTaskExecutionRole",
  "memory": "2048",
  "cpu": "1024"
}
```

#### Step 3: Register Task Definition

```bash
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

#### Step 4: Create Service

```bash
aws ecs create-service \
  --cluster clarity-cluster \
  --service-name clarity-service \
  --task-definition clarity-task \
  --desired-count 2 \
  --launch-type EC2
```

---

## 🔒 Security Checklist

- [ ] Enable HTTPS/SSL
- [ ] Use IAM roles instead of hardcoded credentials
- [ ] Enable S3 bucket encryption
- [ ] Use VPC security groups to restrict access
- [ ] Setup CloudWatch monitoring and alerts
- [ ] Enable AWS WAF for DDoS protection
- [ ] Rotate AWS access keys regularly
- [ ] Use secrets manager for sensitive data
- [ ] Enable VPC Flow Logs for troubleshooting
- [ ] Setup backup and disaster recovery

---

## 📊 Monitoring

### CloudWatch Setup

```bash
# Create alarm for high CPU
aws cloudwatch put-metric-alarm \
  --alarm-name clarity-high-cpu \
  --alarm-description "Alert if CPU > 70%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 70 \
  --comparison-operator GreaterThanThreshold
```

### Log Analysis

```bash
# View logs
docker-compose logs -f api

# Export logs to S3
aws logs create-export-task \
  --log-group-name /ecs/clarity \
  --from 1000000000000 \
  --to 9999999999999 \
  --destination clarity-logs
```

---

## 🔄 Update and Rollback

### Deploy New Version

```bash
# Build and push new image
docker build -t clarity-in-care:v1.1 .
docker tag clarity-in-care:v1.1 \
  <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/clarity-in-care:v1.1
docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/clarity-in-care:v1.1

# Update service
aws ecs update-service \
  --cluster clarity-cluster \
  --service clarity-service \
  --force-new-deployment
```

### Rollback if Issues

```bash
# Revert to previous image
aws ecs update-service \
  --cluster clarity-cluster \
  --service clarity-service \
  --task-definition clarity-task:1 \
  --force-new-deployment
```

---

## 💰 Cost Optimization

| Component | Estimated Cost (monthly) |
|-----------|--------------------------|
| EC2 t3.medium | $30 |
| RDS db.t3.micro | $25 |
| S3 storage (100GB) | $2 |
| Data transfer | $5 |
| **Total** | **~$62** |

**Tips to reduce costs:**
- Use spot instances for non-critical workloads (-70%)
- Use S3 lifecycle policies to archive old images
- Monitor data transfer (most expensive)
- Use CloudFront CDN for image delivery

---

## 🎯 Production Readiness Checklist

- [ ] Model trained and tested
- [ ] API endpoints documented and tested
- [ ] Database backups configured
- [ ] Monitoring and alerts setup
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Disaster recovery plan in place
- [ ] Team trained on operations
- [ ] Documentation complete
- [ ] SLA defined and agreed

---

## 📞 Troubleshooting Deployment

### Docker Container won't start
```bash
docker logs <container_id>
docker-compose logs api
```

### Connection refused
- Check security group rules
- Verify service is running: `docker-compose ps`
- Check port mappings

### Out of memory
- Increase EC2 instance size
- Reduce model batch size
- Enable swap

### Slow predictions
- Add GPU support (g3.4xlarge)
- Enable caching
- Use model quantization

---

**Deployment Version:** 1.0  
**Last Updated:** February 2026
