# 📘 COMPLETE DEVOPS PIPELINE EXPLANATION
## Candlestick Predictor - 3-VM Architecture

---

## 🎯 **OVERVIEW: How Everything Connects**

```
┌──────────────────────────────────────────────────────────────────┐
│                         YOUR MACHINE                              │
│  ┌────────┐   ┌────────┐   ┌────────┐                            │
│  │  Git   │   │ Vagrant│   │ Docker │                            │
│  │ Repo   │   │ (VBox) │   │Compose │                            │
│  └────────┘   └────────┘   └────────┘                            │
│       │            │            │                                 │
└───────┼────────────┼────────────┼─────────────────────────────────┘
        │            │            │
        │            ▼            │
        │    ┌──────────────────┐ │
        │    │   VM 1: JENKINS  │ │
        │    │  192.168.33.10   │ │
        │    │  Port: 8080      │ │
        │    └──────────────────┘ │
        │            │             │
        ▼            ▼             ▼
┌────────────┐  ┌────────────┐  ┌────────────┐
│   Git      │  │  Ansible   │  │ AppServer  │
│  (GitHub)  │──│  Deploys   │──│    VM 2    │
└────────────┘  └────────────┘  │192.168.33.11│
                                │Ports: 3000, │
                                │ 8000, 8001  │
                                └─────────────┘
                                      │
                                      ▼
                                ┌────────────┐
                                │ Docker     │
                                │ Containers │
                                │ (7 total)  │
                                └────────────┘
                                      │
                                      ▼
                                ┌────────────┐
                                │  Monitor   │
                                │    VM 3    │
                                │192.168.33.12│
                                │  Nagios    │
                                └────────────┘
```

---

## 🚀 **THE COMPLETE FLOW**

### **Step 1: Developer Pushes Code**
```
Developer → git add . → git commit → git push → GitHub
```
**What happens:** Code is versioned and stored in Git repository

---

### **Step 2: Vagrant Creates 3 VMs**
```
vagrant up
```

**What Vagrant does:**
1. **Creates VM 1 (Jenkins)**
   - Installs Java, Jenkins, Docker, Ansible
   - IP: 192.168.33.10
   - Purpose: CI/CD automation

2. **Creates VM 2 (AppServer)**
   - Installs Docker, Docker Compose
   - IP: 192.168.33.11
   - Purpose: Run application containers

3. **Creates VM 3 (Monitor)**
   - Installs Nagios, Apache
   - IP: 192.168.33.12
   - Purpose: Monitor VMs and containers

**Why 3 VMs?**
- **Isolation:** Jenkins failures don't affect the app
- **Security:** App server has no build tools
- **Production-like:** Mimics real infrastructure

---

### **Step 3: Jenkins Detects Code Change**

**Jenkins Pipeline (Jenkinsfile):**
```groovy
stage 1: Checkout
  ↓ Pull code from Git

stage 2: Build
  ↓ Build Docker images (frontend, backend, AI)

stage 3: Test
  ↓ Run unit tests

stage 4: Deploy
  ↓ Trigger Ansible playbook

stage 5: Notify
  ↓ Send status to team
```

---

### **Step 4: Ansible Deploys to AppServer**

**Ansible Playbook** (`deploy-app.yml`):
```yaml
1. SSH to AppServer VM (192.168.33.11)
2. Copy docker-compose.yml
3. Copy application code
4. Run: docker-compose build
5. Run: docker-compose up -d
6. Wait for services to start
7. Report success/failure
```

**Why Ansible?**
- **Idempotent:** Can run multiple times safely
- **Declarative:** Describes desired state
- **Agentless:** Just needs SSH

---

### **Step 5: Docker Compose Starts Containers**

**On AppServer VM:**
```bash
docker-compose up -d
```

**Creates 7 containers:**
1. **candlestick-frontend** (React) - Port 3000
2. **candlestick-backend** (FastAPI) - Port 8000
3. **candlestick-ai** (PyTorch) - Port 8001
4. **candlestick-redis** (Cache) - Port 6379
5. **candlestick-prometheus** (Metrics) - Port 9090
6. **candlestick-grafana** (Dashboards) - Port 3001
7. **candlestick-jenkins** (CI/CD) - Port 8080

**Container Network:**
```
candlestick-network (172.20.0.0/16)
  ├── frontend     (172.20.0.2)
  ├── backend      (172.20.0.3) ← talks to ai via hostname
  ├── ai           (172.20.0.4)
  ├── redis        (172.20.0.5)
  ├── prometheus   (172.20.0.6)
  └── grafana      (172.20.0.7)
```

**Service Discovery:**
Backend can call: `http://ai:8001/predict` (Docker DNS resolves hostname)

---

### **Step 6: Nagios Monitors Everything**

**Monitor VM watches:**
```
✓ VM 1 (Jenkins) - Is Jenkins running?
✓ VM 2 (AppServer) - Can we reach it?
✓ Container health - Are all 7 containers up?
✓ Application health - Does frontend respond?
✓ Disk space - Any VM running out of space?
```

**If something fails:**
```
Nagios → Email/Slack alert → DevOps team
```

---

## 🔧 **DETAILED COMPONENT BREAKDOWN**

### **1. GIT - Version Control**

**Files tracked:**
```
.git/
├── All code history
├── Branches (main, dev, feature/*)
└── Commits with messages
```

**Commands used in pipeline:**
```bash
git clone <repo>        # Jenkins pulls code
git pull origin main    # Get latest changes
git checkout <branch>   # Switch versions
```

**Integration:**
- Jenkins polls Git every 5 minutes
- OR Git webhook triggers Jenkins immediately

---

### **2. DOCKER - Containerization**

**Why containers?**
- ✅ Consistent environments (dev = staging = prod)
- ✅ Isolated dependencies (Python 3.11 for AI, Node 18 for frontend)
- ✅ Portable (works on Windows, Mac, Linux, cloud)

**Example: Backend Dockerfile**
```dockerfile
FROM python:3.11-slim       # Base image
WORKDIR /app                # Set directory
COPY requirements.txt .     # Copy dependencies
RUN pip install -r ...      # Install them
COPY . .                    # Copy code
CMD ["uvicorn", ...]        # Start server
```

**Build & Run:**
```bash
docker build -t backend ./backend
docker run -p 8000:8000 backend
```

---

### **3. DOCKER COMPOSE - Orchestration**

**Why Docker Compose?**
- Manage multiple containers as one application
- Define networks and volumes
- Start/stop everything with one command

**docker-compose.yml structure:**
```yaml
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    depends_on: [backend]    ← waits for backend

  backend:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: [ai]         ← waits for AI
    environment:
      AI_SERVICE_URL: http://ai:8001  ← hostname resolution

  ai:
    build: ./ai
    ports: ["8001:8001"]
    volumes:
      - ./model.pth:/app/models/model.pth  ← shared file

networks:
  candlestick-network:  ← private network for containers
```

**Commands:**
```bash
docker-compose up -d        # Start all
docker-compose down         # Stop all
docker-compose logs backend # View logs
docker-compose ps           # List containers
```

---

### **4. VAGRANT - VM Management**

**Vagrantfile** = Recipe for VMs

**Key concepts:**
```ruby
config.vm.define "jenkins" do |jenkins|
  jenkins.vm.box = "ubuntu/focal64"      # OS template
  jenkins.vm.network "private_network", ip: "192.168.33.10"
  jenkins.vm.provider "virtualbox" do |vb|
    vb.memory = "2048"                   # RAM allocation
    vb.cpus = 2                          # CPU cores
  end
end
```

**Networking:**
- **Private Network:** VMs talk to each other (192.168.33.x)
- **Port Forwarding:** Access VM services from host
  - Host:8080 → Jenkins VM:8080
  - Host:3000 → AppServer VM:3000

**Commands:**
```bash
vagrant up                # Create all VMs
vagrant ssh jenkins       # SSH into Jenkins VM
vagrant halt              # Stop VMs
vagrant destroy           # Delete VMs
vagrant reload            # Restart VMs
vagrant status            # Check VM states
```

---

### **5. ANSIBLE - Automation**

**Inventory** = List of servers
```ini
[appserver]
192.168.33.11 ansible_user=vagrant
```

**Playbook** = Instructions
```yaml
- name: Deploy app
  hosts: appserver
  tasks:
    - name: Copy files
      copy:
        src: docker-compose.yml
        dest: /home/vagrant/

    - name: Start containers
      command: docker-compose up -d
```

**Why Ansible?**
- **Idempotent:** Running twice = same result
- **Declarative:** Say what you want, not how
- **Agentless:** Just SSH required

**Run playbook:**
```bash
ansible-playbook -i inventories/vagrant deploy-app.yml
```

**Or from Jenkins:**
```groovy
stage('Deploy') {
    sh 'ansible-playbook -i inventories/vagrant deploy-app.yml'
}
```

---

### **6. JENKINS - CI/CD Pipeline**

**Jenkinsfile** defines pipeline:
```groovy
pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/user/repo.git'
            }
        }
        stage('Build') {
            steps {
                sh 'docker build -t frontend ./frontend'
                sh 'docker build -t backend ./backend'
                sh 'docker build -t ai ./ai'
            }
        }
        stage('Test') {
            steps {
                sh 'python -m pytest tests/'
            }
        }
        stage('Deploy') {
            steps {
                sh 'ansible-playbook deploy-app.yml'
            }
        }
    }
    post {
        success {
            echo 'Deployment successful!'
        }
        failure {
            echo 'Deployment failed!'
        }
    }
}
```

**Triggers:**
- **Git webhook:** Push → immediate build
- **Scheduled:** Daily at 2 AM
- **Manual:** Click "Build Now"

**Plugins used:**
- Git plugin
- Docker plugin
- Ansible plugin
- Slack notification

---

### **7. NAGIOS - Monitoring**

**What Nagios monitors:**

**1. Host checks:**
```
VM 1 (Jenkins)   → PING, SSH
VM 2 (AppServer) → PING, SSH, Docker daemon
VM 3 (Monitor)   → PING, SSH
```

**2. Service checks:**
```
Frontend → HTTP GET http://192.168.33.11:3000
Backend  → HTTP GET http://192.168.33.11:8000/health
AI       → HTTP GET http://192.168.33.11:8001/health
```

**3. Resource checks:**
```
CPU usage > 80%  → WARNING
Disk space < 10% → CRITICAL
Memory < 500MB   → WARNING
```

**Alert flow:**
```
Problem detected → Nagios evaluates severity → Send alert (email/Slack)
```

**Configuration:**
```cfg
define host {
    host_name           appserver
    address             192.168.33.11
    check_command       check-host-alive
}

define service {
    host_name           appserver
    service_description Frontend HTTP
    check_command       check_http!3000
}
```

---

## 🔄 **COMPLETE WORKFLOW EXAMPLE**

**Scenario:** You fix a bug in the backend

### **Step 1: Code Change**
```bash
# On your machine
cd backend
vim main.py          # Fix bug
git add main.py
git commit -m "Fix: Resolved image processing error"
git push origin main
```

### **Step 2: Jenkins Triggered**
```
GitHub webhook → Jenkins VM (192.168.33.10)
Jenkins pulls code
Jenkins runs pipeline
```

### **Step 3: Build Phase**
```
Jenkins VM:
  docker build -t backend:v1.2.3 ./backend
  docker build -t frontend:v1.2.3 ./frontend
  docker build -t ai:v1.2.3 ./ai
```

### **Step 4: Test Phase**
```
Jenkins runs:
  pytest tests/
  npm test
All tests pass ✓
```

### **Step 5: Deploy Phase**
```
Jenkins triggers Ansible:
  ansible-playbook -i inventories/vagrant deploy-app.yml

Ansible:
  1. SSH to AppServer (192.168.33.11)
  2. Copy new docker-compose.yml
  3. Run: docker-compose pull
  4. Run: docker-compose up -d
  5. Containers restart with new code
```

### **Step 6: Health Check**
```
Ansible waits for:
  ✓ Frontend responding on :3000
  ✓ Backend responding on :8000
  ✓ AI responding on :8001
```

### **Step 7: Monitoring**
```
Nagios on Monitor VM (192.168.33.12):
  ✓ All containers healthy
  ✓ HTTP endpoints responding
  ✓ No errors in logs
```

### **Step 8: Notification**
```
Jenkins → Slack:
  "✅ Deployment successful - Build #47"
```

---

## 📊 **VM RESOURCE ALLOCATION**

```
┌──────────────────────────────────────────────┐
│ VM 1: JENKINS                                │
│ RAM: 2 GB                                    │
│ CPU: 2 cores                                 │
│ Disk: ~10 GB                                 │
│ Purpose: CI/CD builds & orchestration        │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│ VM 2: APPSERVER                              │
│ RAM: 4 GB                                    │
│ CPU: 4 cores                                 │
│ Disk: ~20 GB                                 │
│ Purpose: Run 7 Docker containers             │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│ VM 3: MONITOR                                │
│ RAM: 1 GB                                    │
│ CPU: 1 core                                  │
│ Disk: ~5 GB                                  │
│ Purpose: Nagios monitoring                   │
└──────────────────────────────────────────────┘

Total: 7 GB RAM, 7 CPU cores
```

---

## 🎓 **FOR YOUR PRESENTATION**

### **Demonstrate:**

**1. Version Control (Git)**
```bash
git log --oneline --graph
git diff HEAD~1
```
Show commit history and changes

**2. Infrastructure Provisioning (Vagrant)**
```bash
vagrant status
vagrant ssh jenkins
vagrant ssh appserver
```
Show 3 running VMs

**3. Configuration Management (Ansible)**
```bash
ansible-playbook --check deploy-app.yml
ansible appserver -m ping
```
Show automation capabilities

**4. Containerization (Docker)**
```bash
docker ps
docker logs candlestick-backend
docker exec -it candlestick-ai bash
```
Show container isolation

**5. Orchestration (Docker Compose)**
```bash
docker-compose ps
docker-compose scale backend=3
```
Show multi-container management

**6. CI/CD (Jenkins)**
- Show Jenkins pipeline UI
- Trigger a build
- Show build logs
- Show deployment stages

**7. Monitoring (Nagios)**
- Show Nagios dashboard
- Demonstrate service checks
- Show alert configuration

---

## 🏆 **KEY BENEFITS OF THIS ARCHITECTURE**

### **1. Scalability**
```
Need more backend instances?
  docker-compose scale backend=5
```

### **2. Isolation**
```
Frontend crash → Backend unaffected
Jenkins update → App keeps running
```

### **3. Reproducibility**
```
New developer joins:
  1. git clone
  2. vagrant up
  3. Wait 15 minutes
  4. Environment ready
```

### **4. Testing**
```
Test in production-like environment:
  3 VMs = production setup
  Ansible = same deploy process
```

### **5. Automation**
```
Push code → Automatic deployment
No manual SSH
No "works on my machine"
```

---

## ✅ **VALIDATION CHECKLIST**

### **Before Presentation:**

- [ ] All 3 VMs running (`vagrant status`)
- [ ] Jenkins accessible (http://localhost:8080)
- [ ] Application working (http://localhost:3000)
- [ ] Nagios monitoring (http://localhost:8888/nagios)
- [ ] Git history clean (`git log`)
- [ ] Ansible playbook runs without errors
- [ ] Jenkins pipeline successful
- [ ] All containers healthy (`docker ps`)

---

## 🎯 **EXPECTED QUESTIONS & ANSWERS**

**Q: Why 3 VMs instead of 1?**
A: Separation of concerns - Jenkins for builds, AppServer for runtime, Monitor for observability. Mimics production.

**Q: Why Docker instead of installing directly?**
A: Consistency across environments, isolation, easy rollback, and portability.

**Q: What if Jenkins fails?**
A: Application keeps running. Jenkins only handles deployments, not runtime.

**Q: How do you ensure zero downtime?**
A: Blue-green deployment with Ansible, health checks before routing traffic.

**Q: Can this scale to production?**
A: Yes. Replace Vagrant with AWS/Azure, same Ansible playbooks work.

---

## 📚 **SUMMARY**

```
Git       → Version control & collaboration
Docker    → Container packaging
Docker    → Multi-container orchestration
Compose
Vagrant   → VM provisioning & management
Ansible   → Configuration & deployment automation
Jenkins   → CI/CD pipeline execution
Nagios    → Monitoring & alerting
```

**Together they create:**
- ✅ Automated infrastructure
- ✅ Consistent environments
- ✅ Fast deployments
- ✅ Easy rollbacks
- ✅ Continuous monitoring

---

**Good luck with your presentation! 🚀**
