pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = credentials('docker-registry-url')
        DOCKER_CREDENTIALS = credentials('docker-registry-credentials')
        GITHUB_CREDENTIALS = credentials('github-credentials')
        PROJECT_NAME = 'candlestick-predictor'
        BUILD_VERSION = "${BUILD_NUMBER}-${GIT_COMMIT.take(7)}"
        SLACK_CHANNEL = '#deployments'
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
                script {
                    env.GIT_COMMIT = sh(
                        script: 'git rev-parse HEAD',
                        returnStdout: true
                    ).trim()
                    env.GIT_BRANCH = sh(
                        script: 'git rev-parse --abbrev-ref HEAD',
                        returnStdout: true
                    ).trim()
                }
            }
        }
        
        stage('Environment Validation') {
            steps {
                echo 'Validating environment...'
                sh '''
                    docker --version
                    docker-compose --version
                    node --version || echo "Node.js not found"
                    python3 --version || echo "Python3 not found"
                '''
            }
        }
        
        stage('Code Quality & Security') {
            parallel {
                stage('Backend Linting') {
                    steps {
                        dir('backend') {
                            sh '''
                                python3 -m venv venv
                                source venv/bin/activate
                                pip install -r requirements.txt
                                pip install flake8 bandit
                                flake8 . --max-line-length=120 --exclude=venv
                                bandit -r . -f json -o bandit-report.json || true
                            '''
                        }
                        archiveArtifacts artifacts: 'backend/bandit-report.json', allowEmptyArchive: true
                    }
                }
                
                stage('Frontend Linting') {
                    steps {
                        dir('frontend') {
                            sh '''
                                npm ci
                                npm run test -- --coverage --watchAll=false
                                npm audit --audit-level moderate || true
                            '''
                        }
                        publishHTML([
                            allowMissing: false,
                            alwaysLinkToLastBuild: true,
                            keepAll: true,
                            reportDir: 'frontend/coverage/lcov-report',
                            reportFiles: 'index.html',
                            reportName: 'Frontend Coverage Report'
                        ])
                    }
                }
                
                stage('AI Service Validation') {
                    steps {
                        dir('ai') {
                            sh '''
                                python3 -m venv venv
                                source venv/bin/activate
                                pip install -r requirements.txt
                                python -c "import torch; print(f'PyTorch version: {torch.__version__}')"
                                python -c "import model; print('Model imports successful')"
                            '''
                        }
                    }
                }
            }
        }
        
        stage('Build Docker Images') {
            parallel {
                stage('Build Frontend') {
                    steps {
                        script {
                            env.FRONTEND_IMAGE = "${DOCKER_REGISTRY}/${PROJECT_NAME}-frontend:${BUILD_VERSION}"
                            sh "docker build -t ${FRONTEND_IMAGE} ./frontend"
                            sh "docker tag ${FRONTEND_IMAGE} ${DOCKER_REGISTRY}/${PROJECT_NAME}-frontend:latest"
                        }
                    }
                }
                
                stage('Build Backend') {
                    steps {
                        script {
                            env.BACKEND_IMAGE = "${DOCKER_REGISTRY}/${PROJECT_NAME}-backend:${BUILD_VERSION}"
                            sh "docker build -t ${BACKEND_IMAGE} ./backend"
                            sh "docker tag ${BACKEND_IMAGE} ${DOCKER_REGISTRY}/${PROJECT_NAME}-backend:latest"
                        }
                    }
                }
                
                stage('Build AI Service') {
                    steps {
                        script {
                            env.AI_IMAGE = "${DOCKER_REGISTRY}/${PROJECT_NAME}-ai:${BUILD_VERSION}"
                            sh "docker build -t ${AI_IMAGE} ./ai"
                            sh "docker tag ${AI_IMAGE} ${DOCKER_REGISTRY}/${PROJECT_NAME}-ai:latest"
                        }
                    }
                }
            }
        }
        
        stage('Security Scanning') {
            parallel {
                stage('Container Vulnerability Scan') {
                    steps {
                        script {
                            sh '''
                                # Install trivy if not available
                                which trivy || (
                                    wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
                                    echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
                                    sudo apt-get update
                                    sudo apt-get install trivy
                                )
                                
                                # Scan images
                                trivy image --format json --output frontend-scan.json ${FRONTEND_IMAGE} || true
                                trivy image --format json --output backend-scan.json ${BACKEND_IMAGE} || true
                                trivy image --format json --output ai-scan.json ${AI_IMAGE} || true
                            '''
                        }
                        archiveArtifacts artifacts: '*-scan.json', allowEmptyArchive: true
                    }
                }
                
                stage('Dependency Check') {
                    steps {
                        sh '''
                            # Check for known vulnerabilities in dependencies
                            docker run --rm -v "$(pwd)":/src owasp/dependency-check:latest \
                                --scan /src --format JSON --out /src/dependency-check-report.json || true
                        '''
                        archiveArtifacts artifacts: 'dependency-check-report.json', allowEmptyArchive: true
                    }
                }
            }
        }
        
        stage('Integration Testing') {
            steps {
                echo 'Starting integration tests...'
                sh '''
                    # Start services for testing
                    docker-compose -f docker-compose.test.yml up -d
                    sleep 30
                    
                    # Health checks
                    curl -f http://localhost:8000/health || exit 1
                    curl -f http://localhost:8001/health || exit 1
                    curl -f http://localhost:3000 || exit 1
                    
                    # API tests
                    cd backend
                    python3 -m venv test-venv
                    source test-venv/bin/activate
                    pip install -r requirements.txt pytest requests
                    pytest tests/ -v --junitxml=../test-results.xml || true
                    
                    # Cleanup
                    cd ..
                    docker-compose -f docker-compose.test.yml down
                '''
                publishTestResults testResultsPattern: 'test-results.xml'
            }
        }
        
        stage('Push to Registry') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                    buildingTag()
                }
            }
            steps {
                script {
                    docker.withRegistry("https://${DOCKER_REGISTRY}", DOCKER_CREDENTIALS) {
                        sh "docker push ${FRONTEND_IMAGE}"
                        sh "docker push ${BACKEND_IMAGE}"
                        sh "docker push ${AI_IMAGE}"
                        sh "docker push ${DOCKER_REGISTRY}/${PROJECT_NAME}-frontend:latest"
                        sh "docker push ${DOCKER_REGISTRY}/${PROJECT_NAME}-backend:latest"
                        sh "docker push ${DOCKER_REGISTRY}/${PROJECT_NAME}-ai:latest"
                    }
                }
            }
        }
        
        stage('Deploy to Staging') {
            when {
                branch 'develop'
            }
            steps {
                echo 'Deploying to staging environment...'
                script {
                    // Update docker-compose with new image tags
                    sh '''
                        envsubst < docker-compose.staging.yml.template > docker-compose.staging.yml
                        scp docker-compose.staging.yml deploy@staging-server:/opt/candlestick-predictor/
                        ssh deploy@staging-server "cd /opt/candlestick-predictor && docker-compose -f docker-compose.staging.yml up -d"
                    '''
                }
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            input {
                message "Deploy to production?"
                ok "Deploy"
                parameters {
                    choice(name: 'DEPLOYMENT_TYPE', choices: ['rolling', 'blue-green'], description: 'Deployment strategy')
                }
            }
            steps {
                echo "Deploying to production with ${params.DEPLOYMENT_TYPE} strategy..."
                script {
                    if (params.DEPLOYMENT_TYPE == 'blue-green') {
                        // Blue-green deployment
                        sh '''
                            ansible-playbook -i devops/ansible/inventories/production \
                                devops/ansible/playbooks/deploy-blue-green.yml \
                                -e "build_version=${BUILD_VERSION}"
                        '''
                    } else {
                        // Rolling deployment
                        sh '''
                            ansible-playbook -i devops/ansible/inventories/production \
                                devops/ansible/playbooks/deploy-rolling.yml \
                                -e "build_version=${BUILD_VERSION}"
                        '''
                    }
                }
            }
        }
    }
    
    post {
        always {
            // Cleanup
            sh '''
                docker system prune -f
                docker volume prune -f
            '''
            
            // Archive logs
            archiveArtifacts artifacts: '**/*.log', allowEmptyArchive: true
            
            // Clean workspace
            cleanWs()
        }
        
        success {
            slackSend(
                channel: SLACK_CHANNEL,
                color: 'good',
                message: "✅ Build #${BUILD_NUMBER} succeeded for ${PROJECT_NAME} on branch ${GIT_BRANCH}"
            )
            
            // Update GitHub status
            githubNotify(
                status: 'SUCCESS',
                description: 'Build and tests passed',
                context: 'continuous-integration/jenkins'
            )
        }
        
        failure {
            slackSend(
                channel: SLACK_CHANNEL,
                color: 'danger',
                message: "❌ Build #${BUILD_NUMBER} failed for ${PROJECT_NAME} on branch ${GIT_BRANCH}"
            )
            
            githubNotify(
                status: 'FAILURE',
                description: 'Build or tests failed',
                context: 'continuous-integration/jenkins'
            )
        }
        
        unstable {
            slackSend(
                channel: SLACK_CHANNEL,
                color: 'warning',
                message: "⚠️ Build #${BUILD_NUMBER} unstable for ${PROJECT_NAME} on branch ${GIT_BRANCH}"
            )
        }
    }
}