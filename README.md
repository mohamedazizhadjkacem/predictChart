# 🔮 Candlestick Chart Predictor

A full-stack AI-powered web application that analyzes candlestick chart images and predicts future price movements using LSTM neural networks.

## 🏗️ Architecture

This application consists of three containerized microservices:

### 🟦 Frontend (React)
- **Technology**: React.js + Styled Components
- **Port**: 3000
- **Features**:
  - Drag & drop image upload
  - Real-time processing status
  - Interactive result visualization
  - Responsive design

### 🟩 Backend (FastAPI)
- **Technology**: Python + FastAPI
- **Port**: 8000
- **Features**:
  - Image → Numeric conversion
  - AI service communication
  - Image reconstruction
  - Full pipeline processing

### 🟥 AI Service (PyTorch)
- **Technology**: Python + PyTorch
- **Port**: 8001
- **Features**:
  - LSTM sequence-to-sequence model
  - Real-time inference
  - Fallback prediction algorithms

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for development)
- Python 3.11+ (for development)

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/candlestick-predictor.git
cd candlestick-predictor
```

### 2. Start with Docker Compose
```bash
# Production deployment
docker-compose up -d

# Development with hot reload
docker-compose -f docker-compose.dev.yml up -d
```

### 3. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **AI Service**: http://localhost:8001
- **Monitoring**: http://localhost:9090 (Prometheus) / http://localhost:3001 (Grafana)

## 📊 How It Works

1. **Upload**: User uploads a candlestick chart image (recommended: 1025×817px)
2. **Extract**: Backend converts image to 50 OHLC (Open, High, Low, Close) data points
3. **Predict**: AI service uses LSTM model to predict 25 future candlesticks
4. **Reconstruct**: Backend converts predictions back to image format (342×817px)
5. **Combine**: Original and predicted images are concatenated horizontally
6. **Display**: Frontend shows the complete result with analysis data

## 🔧 Development Setup

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm install
npm start
```

### AI Service Development
```bash
cd ai
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

## 📋 API Documentation

### Backend Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health check |
| `/convert-image-to-numeric` | POST | Convert image to OHLC data |
| `/predict` | POST | Get prediction from AI service |
| `/reconstruct-image` | POST | Convert numeric to image |
| `/full-process` | POST | Complete pipeline processing |

### AI Service Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health check |
| `/predict` | POST | LSTM model prediction |
| `/predict-demo` | POST | Demo prediction (no model required) |
| `/model-info` | GET | Model information |

## 🎯 Model Information

### LSTM Architecture
- **Input Size**: 4 (OHLC values)
- **Hidden Size**: 64
- **Layers**: 2
- **Sequence Length**: 50 candlesticks
- **Prediction Length**: 25 future candlesticks
- **Output Format**: Normalized OHLC values (0-1 range)

### Model Training (Not included in this repository)
```python
# Example training configuration
model = CandlestickLSTM(
    input_size=4,
    hidden_size=64,
    num_layers=2,
    output_size=4,
    sequence_length=50,
    prediction_length=25
)
```

## 🔒 Security Features

- Input validation and sanitization
- File type and size restrictions
- Docker container isolation
- CORS configuration
- SSL/TLS support
- Rate limiting (configurable)

## 📈 Monitoring & DevOps

### Jenkins Pipeline
- Automated testing
- Security scanning
- Docker image building
- Multi-environment deployment

### Ansible Deployment
```bash
# Deploy to staging
ansible-playbook -i devops/ansible/inventories/staging devops/ansible/playbooks/deploy.yml

# Deploy to production
ansible-playbook -i devops/ansible/inventories/production devops/ansible/playbooks/deploy.yml
```

### Nagios Monitoring
- Application health checks
- Resource utilization monitoring
- SSL certificate monitoring
- Container status monitoring

## 🐳 Docker Commands

```bash
# Build all images
docker-compose build

# View logs
docker-compose logs -f [service-name]

# Scale services
docker-compose up -d --scale backend=3

# Health check
docker-compose ps

# Update services
docker-compose pull && docker-compose up -d
```

## 🛠️ Configuration

### Environment Variables

#### Backend (.env)
```
AI_SERVICE_URL=http://ai:8001
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

#### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_MAX_FILE_SIZE=10485760
```

#### AI Service (.env)
```
MODEL_PATH=/app/models/candlestick_predictor_model.pth
PREDICTION_LENGTH=25
```

## 📊 Performance Tuning

### Production Optimizations
- **Frontend**: Nginx with gzip compression
- **Backend**: Gunicorn with multiple workers
- **AI Service**: Model optimization and caching
- **Database**: Redis for session storage
- **CDN**: Static asset delivery

### Scaling Recommendations
- **Horizontal**: Multiple container instances
- **Vertical**: Increased CPU/memory allocation
- **Load Balancing**: Nginx or HAProxy
- **Caching**: Redis for frequent predictions

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test

# Integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 🚀 Deployment

### Production Checklist
- [ ] SSL certificates configured
- [ ] Environment variables set
- [ ] Database backups enabled
- [ ] Monitoring configured
- [ ] Log rotation enabled
- [ ] Security headers configured
- [ ] Rate limiting enabled

### Blue-Green Deployment
```bash
# Deploy new version
ansible-playbook devops/ansible/playbooks/deploy-blue-green.yml

# Switch traffic
ansible-playbook devops/ansible/playbooks/switch-traffic.yml

# Rollback if needed
ansible-playbook devops/ansible/playbooks/rollback.yml
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint for JavaScript code
- Add tests for new features
- Update documentation
- Use conventional commits

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Documentation**: [Wiki](https://github.com/yourusername/candlestick-predictor/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/candlestick-predictor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/candlestick-predictor/discussions)

## 🙏 Acknowledgments

- PyTorch team for the deep learning framework
- FastAPI community for the excellent web framework
- React team for the frontend framework
- Docker for containerization technology
- All open-source contributors

---

**Built with ❤️ for the trading and AI community**

*Last updated: December 2025*