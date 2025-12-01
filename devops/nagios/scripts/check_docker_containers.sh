#!/bin/bash

# Docker Containers Health Check Script for Nagios
# This script checks if all required Docker containers are running

# Define expected containers
EXPECTED_CONTAINERS=(
    "candlestick-frontend"
    "candlestick-backend" 
    "candlestick-ai"
)

# Nagios return codes
OK=0
WARNING=1
CRITICAL=2
UNKNOWN=3

# Initialize counters
total_containers=${#EXPECTED_CONTAINERS[@]}
running_containers=0
stopped_containers=()

# Check each container
for container in "${EXPECTED_CONTAINERS[@]}"; do
    status=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null)
    
    if [ "$status" = "running" ]; then
        ((running_containers++))
    else
        stopped_containers+=("$container:$status")
    fi
done

# Generate output and return appropriate code
if [ $running_containers -eq $total_containers ]; then
    echo "OK - All $total_containers containers are running"
    exit $OK
elif [ $running_containers -gt 0 ]; then
    echo "WARNING - $running_containers/$total_containers containers running. Stopped: ${stopped_containers[*]}"
    exit $WARNING
else
    echo "CRITICAL - No containers are running. Stopped: ${stopped_containers[*]}"
    exit $CRITICAL
fi