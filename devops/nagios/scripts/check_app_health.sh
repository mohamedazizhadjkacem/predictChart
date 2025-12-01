#!/bin/bash

# Application Health Check Script for Nagios
# This script performs comprehensive health checks on the Candlestick Predictor application

# Nagios return codes
OK=0
WARNING=1
CRITICAL=2
UNKNOWN=3

# Configuration
FRONTEND_URL="http://localhost:3000"
BACKEND_URL="http://localhost:8000"
AI_URL="http://localhost:8001"
TIMEOUT=10

# Function to check HTTP endpoint
check_endpoint() {
    local url=$1
    local service_name=$2
    local expected_status=${3:-200}
    
    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$url" 2>/dev/null)
    
    if [ "$response" = "$expected_status" ]; then
        return 0
    else
        echo "$service_name endpoint failed (HTTP $response)"
        return 1
    fi
}

# Function to check service health endpoint
check_health_endpoint() {
    local url=$1
    local service_name=$2
    
    response=$(curl -s --max-time $TIMEOUT "$url/health" 2>/dev/null)
    
    if echo "$response" | grep -q '"status".*"healthy"'; then
        return 0
    else
        echo "$service_name health check failed"
        return 1
    fi
}

# Initialize status tracking
failed_checks=()
warning_checks=()

# Check frontend
if ! check_endpoint "$FRONTEND_URL" "Frontend"; then
    failed_checks+=("Frontend")
fi

# Check backend health
if ! check_health_endpoint "$BACKEND_URL" "Backend"; then
    failed_checks+=("Backend")
fi

# Check AI service health
if ! check_health_endpoint "$AI_URL" "AI Service"; then
    failed_checks+=("AI Service")
fi

# Check disk space
disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$disk_usage" -gt 90 ]; then
    failed_checks+=("Disk space critical ($disk_usage%)")
elif [ "$disk_usage" -gt 80 ]; then
    warning_checks+=("Disk space high ($disk_usage%)")
fi

# Check memory usage
memory_usage=$(free | awk 'NR==2{printf "%.1f", $3*100/$2}')
if [ "$(echo "$memory_usage > 90" | bc)" -eq 1 ]; then
    failed_checks+=("Memory usage critical ($memory_usage%)")
elif [ "$(echo "$memory_usage > 80" | bc)" -eq 1 ]; then
    warning_checks+=("Memory usage high ($memory_usage%)")
fi

# Check Docker containers
container_check=$(docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(candlestick-frontend|candlestick-backend|candlestick-ai)" | wc -l)
if [ "$container_check" -lt 3 ]; then
    failed_checks+=("Some containers not running")
fi

# Determine exit status and message
if [ ${#failed_checks[@]} -gt 0 ]; then
    echo "CRITICAL - ${failed_checks[*]}"
    exit $CRITICAL
elif [ ${#warning_checks[@]} -gt 0 ]; then
    echo "WARNING - ${warning_checks[*]}"
    exit $WARNING
else
    echo "OK - All application components healthy"
    exit $OK
fi