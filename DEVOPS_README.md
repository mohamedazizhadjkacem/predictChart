# 🚀 Candlestick Predictor - Complete DevOps Pipeline

## 📋 Project Overview

Academic DevOps project demonstrating a complete containerized microservices architecture with CI/CD pipeline, infrastructure automation, and monitoring.

### Architecture: 3-Tier Application

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Frontend   │ ───► │   Backend   │ ───► │ AI Service  │
│  (React)    │      │  (FastAPI)  │      │  (PyTorch)  │
│  Port 3000  │      │  Port 8000  │      │  Port 8001  │
└─────────────┘      └─────────────┘      └─────────────┘
```

---

## 🎯 DevOps Components

### ✅ 1. **Docker** - Containerization
- 3 application containers (frontend, backend, AI)
- Supporting services (Redis, Prometheus, Grafana, Jenkins)
- Multi-stage builds for optimization

### ✅ 2. **Docker Compose** - Orchestration
- Multi-container application management
- Service discovery via internal network
- Volume management for data persistence

### ✅ 3. **Vagrant** - VM Provisioning
- Automated Ubuntu VM setup
- Pre-configured with Docker & Ansible
- Reproducible development environment

### ✅ 4. **Ansible** - Configuration Management
- Automated deployment playbooks
- Environment-specific inventories (staging/production)
- Idempotent infrastructure provisioning

### ✅ 5. **Jenkins** - CI/CD Pipeline
- Automated build & test
- Docker image creation
- Deployment automation

### ✅ 6. **Nagios** - Monitoring
- Container health checks
- Service availability monitoring
- Alert configuration

### ✅ 7. **Git** - Version Control
- Complete project versioning
- Collaboration workflow

---

## 🚀 Quick Start

### Option 1: Local Docker (Windows/Mac/Linux)

```bash
# Start all services
docker-compose up -d

# Check running containers
docker ps

# View logs
docker logs candlestick-frontend
docker logs candlestick-backend
docker logs candlestick-ai

# Stop all services
docker-compose down
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs
- AI Service: http://localhost:8001/docs
- Jenkins: http://localhost:8080
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin123)

---

### Option 2: Vagrant VM (Full DevOps Pipeline)

```bash
# Prerequisites: Install VirtualBox and Vagrant

# Start VM (first time takes ~10 minutes)
vagrant up

# SSH into VM
vagrant ssh

# Inside VM, start containers
cd /vagrant
docker-compose up -d

# Exit VM
exit

# Stop VM
vagrant halt

# Destroy VM
vagrant destroy
```

---

## 📦 Project Structure

```
predictChart/
├── frontend/              # React application
│   ├── src/
│   ├── Dockerfile
│   └── package.json
├── backend/               # FastAPI service
│   ├── main.py
│   ├── image_to_numeric.py
│   ├── numeric_to_image.py
│   ├── ai_client.py
│   ├── Dockerfile
│   └── requirements.txt
├── ai/                    # PyTorch AI service
│   ├── main.py
│   ├── model.py
│   ├── inference.py
│   ├── Dockerfile
│   └── requirements.txt
├── devops/
│   ├── ansible/           # Automation playbooks
│   │   ├── inventories/
│   │   │   ├── production
│   │   │   └── staging
│   │   └── playbooks/
│   │       └── deploy.yml
│   ├── jenkins/           # CI/CD configuration
│   ├── monitoring/        # Prometheus config
│   │   └── prometheus.yml
│   └── nagios/            # Monitoring config
│       ├── candlestick-predictor.cfg
│       └── scripts/
├── docker-compose.yml     # Multi-container orchestration
├── Vagrantfile            # VM provisioning
├── Jenkinsfile            # CI/CD pipeline
└── README.md              # This file
```

---

## 🔧 Jenkins Pipeline

The `Jenkinsfile` defines a complete CI/CD pipeline:

1. **Checkout** - Pull code from Git
2. **Build** - Create Docker images
3. **Test** - Run unit tests
4. **Push** - Upload to Docker registry
5. **Deploy** - Deploy to staging/production

### Setup Jenkins:

1. Access Jenkins at http://localhost:8080
2. Initial admin password:
   ```bash
   docker exec candlestick-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
   ```
3. Install suggested plugins
4. Create new Pipeline job pointing to `Jenkinsfile`

---

## 📊 Monitoring with Prometheus & Grafana

### Prometheus
- Metrics collection from all services
- Access: http://localhost:9090
- Queries:
  - Container CPU: `rate(container_cpu_usage_seconds_total[1m])`
  - Memory: `container_memory_usage_bytes`

### Grafana
- Visual dashboards
- Access: http://localhost:3001
- Login: `admin` / `admin123`
- Add Prometheus datasource: `http://prometheus:9090`

---

## 🔍 Nagios Monitoring

Configuration in `devops/nagios/`:
- Health check scripts
- Service availability monitoring
- Alert thresholds

---

## 🎓 Academic Demonstration Points

### For Your Presentation:

1. **Containerization**
   - Show `docker ps` with all 7 containers running
   - Explain isolation and portability

2. **Orchestration**
   - Demonstrate `docker-compose up/down`
   - Show service discovery (backend calling AI via hostname)

3. **Infrastructure as Code**
   - Walk through `Vagrantfile`
   - Show Ansible playbooks

4. **CI/CD**
   - Trigger Jenkins pipeline
   - Show automated build → test → deploy

5. **Monitoring**
   - Display Grafana dashboards
   - Show Prometheus metrics

6. **Scalability**
   ```bash
   # Scale backend to 3 instances
   docker-compose up -d --scale backend=3
   ```

---

## 🧪 Testing the Application

### Upload a Candlestick Image:

1. Open http://localhost:3000
2. Click "Upload Image"
3. Select a candlestick chart (PNG/JPG)
4. Watch the processing pipeline:
   - Image → Numeric conversion
   - AI prediction
   - Image reconstruction
   - Final concatenated output

---

## 🛠️ Troubleshooting

### Check Container Health
```bash
docker ps
docker logs <container-name>
```

### Restart Services
```bash
docker-compose restart
```

### Clean Rebuild
```bash
docker-compose down -v
docker-compose up --build -d
```

### Free Disk Space
```bash
docker system prune -a
```

---

## 📝 Environment Variables

Key configurations in `docker-compose.yml`:
- `AI_SERVICE_URL=http://ai:8001`
- `NODE_ENV=production`
- `PYTHONPATH=/app`

---

## 🎯 Learning Outcomes

This project demonstrates:
- ✅ Microservices architecture
- ✅ Containerization with Docker
- ✅ Container orchestration
- ✅ Infrastructure automation
- ✅ CI/CD pipelines
- ✅ Monitoring & observability
- ✅ Version control
- ✅ DevOps best practices

---

## 📚 Technologies Used

**Frontend:** React, Axios, CSS
**Backend:** Python, FastAPI, OpenCV, Pillow
**AI:** PyTorch, LSTM
**DevOps:** Docker, Docker Compose, Vagrant, Ansible, Jenkins, Nagios
**Monitoring:** Prometheus, Grafana
**Infrastructure:** VirtualBox, Ubuntu

---

## 👥 Contributors

Academic Project - DevOps Engineering

---

## 📄 License

Educational Use Only

---

## 🎉 Success Criteria

Your project is successful when:
- ✅ All 7 containers run without errors
- ✅ Frontend displays and accepts image uploads
- ✅ Backend processes and returns predictions
- ✅ Jenkins pipeline executes successfully
- ✅ Prometheus collects metrics
- ✅ Grafana displays dashboards
- ✅ Vagrant VM provisions automatically

**Good luck with your presentation! 🚀**
