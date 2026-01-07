#!/bin/bash
# =============================================================================
# MING Stack 시작 스크립트
# 라즈베리파이 4/5 최적화
# =============================================================================

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 스크립트 디렉토리로 이동
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo -e "${BLUE}"
echo "=========================================="
echo "  MING Stack - Industrial IoT Platform"
echo "  Starting Services..."
echo "=========================================="
echo -e "${NC}"

# -----------------------------------------------------------------------------
# 1. 시스템 요구사항 확인
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[1/6] Checking system requirements...${NC}"

# Docker 확인
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Install Docker: curl -fsSL https://get.docker.com | sh"
    exit 1
fi

# Docker Compose 확인
if ! docker compose version &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    echo "Install: sudo apt install docker-compose-plugin"
    exit 1
fi

# Docker 데몬 확인
if ! docker info &> /dev/null; then
    echo -e "${RED}Error: Docker daemon is not running${NC}"
    echo "Start Docker: sudo systemctl start docker"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose are available${NC}"

# -----------------------------------------------------------------------------
# 2. 환경 변수 파일 확인
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[2/6] Checking environment configuration...${NC}"

if [ ! -f .env ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo -e "${YELLOW}⚠ Please review and edit .env file if needed${NC}"
fi

# 환경 변수 로드
source .env 2>/dev/null || true

echo -e "${GREEN}✓ Environment configuration ready${NC}"

# -----------------------------------------------------------------------------
# 3. 디렉토리 생성 및 권한 설정
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[3/6] Setting up directories and permissions...${NC}"

# 데이터 디렉토리 생성
mkdir -p mosquitto/data mosquitto/log
mkdir -p influxdb/data influxdb/config
mkdir -p nodered/data
mkdir -p grafana/data

# 권한 설정 (컨테이너 내부 사용자 UID에 맞춤)
# Mosquitto: 1883:1883
# Node-RED: 1000:1000
# Grafana: 472:472

# 권한 설정 시도 (실패해도 계속 진행)
if [ "$(id -u)" = "0" ] || sudo -n true 2>/dev/null; then
    sudo chown -R 1883:1883 mosquitto/data mosquitto/log 2>/dev/null || true
    sudo chown -R 1000:1000 nodered/data 2>/dev/null || true
    sudo chown -R 472:472 grafana/data 2>/dev/null || true
else
    # sudo 없이 chmod로 대체
    chmod -R 777 mosquitto/data mosquitto/log 2>/dev/null || true
    chmod -R 777 nodered/data 2>/dev/null || true
    chmod -R 777 grafana/data 2>/dev/null || true
fi

echo -e "${GREEN}✓ Directories created${NC}"

# -----------------------------------------------------------------------------
# 4. Mosquitto 비밀번호 초기화
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[4/6] Checking Mosquitto authentication...${NC}"

PASSWD_FILE="mosquitto/config/passwd"
MQTT_USER="${MQTT_USER:-mqtt_user}"
MQTT_PASS="${MQTT_PASSWORD:-mqtt_pass}"

# passwd 파일이 비어있거나 주석만 있는지 확인
if [ ! -f "$PASSWD_FILE" ] || ! grep -v "^#" "$PASSWD_FILE" | grep -q "[^[:space:]]"; then
    echo "Initializing Mosquitto passwords..."

    # 임시 컨테이너로 비밀번호 생성
    docker run --rm -v "$(pwd)/mosquitto/config:/mosquitto/config" \
        eclipse-mosquitto:2.0 \
        mosquitto_passwd -b -c /mosquitto/config/passwd "$MQTT_USER" "$MQTT_PASS"

    # Node-RED 계정 추가
    docker run --rm -v "$(pwd)/mosquitto/config:/mosquitto/config" \
        eclipse-mosquitto:2.0 \
        mosquitto_passwd -b /mosquitto/config/passwd nodered "$MQTT_PASS"

    # 센서 디바이스 계정 추가
    docker run --rm -v "$(pwd)/mosquitto/config:/mosquitto/config" \
        eclipse-mosquitto:2.0 \
        mosquitto_passwd -b /mosquitto/config/passwd sensor_device "$MQTT_PASS"

    echo -e "${GREEN}✓ Mosquitto passwords initialized${NC}"
    echo -e "${YELLOW}  Users: $MQTT_USER, nodered, sensor_device${NC}"
    echo -e "${YELLOW}  Password: $MQTT_PASS${NC}"
else
    echo -e "${GREEN}✓ Mosquitto passwords already configured${NC}"
fi

# -----------------------------------------------------------------------------
# 5. Docker Compose 빌드 및 시작
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[5/6] Starting Docker containers...${NC}"

# 이전 컨테이너 정리
docker compose down --remove-orphans 2>/dev/null || true

# 이미지 빌드 (필요시)
echo "Building custom images..."
docker compose build --quiet

# 서비스 시작
echo "Starting services..."
docker compose up -d

# -----------------------------------------------------------------------------
# 6. 서비스 상태 확인
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[6/6] Verifying services...${NC}"

echo "Waiting for services to initialize..."
sleep 15

# 상태 확인
echo ""
docker compose ps

# -----------------------------------------------------------------------------
# 접속 정보 출력
# -----------------------------------------------------------------------------
# 라즈베리파이 IP 주소 가져오기
HOST_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
if [ -z "$HOST_IP" ]; then
    HOST_IP="localhost"
fi

echo ""
echo -e "${GREEN}=========================================="
echo "  MING Stack Started Successfully!"
echo "==========================================${NC}"
echo ""
echo -e "${BLUE}Access URLs:${NC}"
echo "  Node-RED:    http://${HOST_IP}:1880"
echo "  Grafana:     http://${HOST_IP}:3000"
echo "  InfluxDB:    http://${HOST_IP}:8086"
echo ""
echo -e "${BLUE}MQTT Broker:${NC}"
echo "  Host:        ${HOST_IP}"
echo "  Port:        1883 (MQTT), 9001 (WebSocket)"
echo "  User:        ${MQTT_USER}"
echo ""
echo -e "${BLUE}Default Credentials:${NC}"
echo "  Grafana:     admin / ${GRAFANA_PASSWORD:-admin123}"
echo "  Node-RED:    admin / admin123"
echo "  InfluxDB:    admin / ${INFLUXDB_PASSWORD:-admin123456}"
echo ""
echo -e "${BLUE}Simulators:${NC}"
echo "  Modbus TCP:  ${HOST_IP}:5020"
echo "  OPC-UA:      opc.tcp://${HOST_IP}:4840"
echo "  S7 PLC:      ${HOST_IP}:1102"
echo ""
echo -e "${YELLOW}Commands:${NC}"
echo "  View logs:   docker compose logs -f"
echo "  Stop:        ./scripts/stop.sh"
echo "  Status:      docker compose ps"
echo "=========================================="
