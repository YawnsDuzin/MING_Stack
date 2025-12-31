#!/bin/bash
# MING Stack 시작 스크립트

set -e

echo "=========================================="
echo "  MING Stack - Starting Services"
echo "=========================================="

cd "$(dirname "$0")/.."

# 환경 변수 파일 확인
if [ ! -f .env ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Please edit .env file with your settings"
fi

# 디렉토리 권한 설정
echo "Setting up directory permissions..."
mkdir -p mosquitto/data mosquitto/log
mkdir -p influxdb/data influxdb/config
mkdir -p nodered/data
mkdir -p grafana/data

# Docker Compose 실행
echo "Starting Docker Compose..."
docker compose up -d

# 서비스 상태 확인
echo ""
echo "Waiting for services to start..."
sleep 10

echo ""
echo "=========================================="
echo "  Service Status"
echo "=========================================="
docker compose ps

echo ""
echo "=========================================="
echo "  Access URLs"
echo "=========================================="
echo "  Node-RED:  http://localhost:1880"
echo "  Grafana:   http://localhost:3000"
echo "  InfluxDB:  http://localhost:8086"
echo "  MQTT:      localhost:1883"
echo "=========================================="
echo ""
echo "Use 'docker compose logs -f' to view logs"
