#!/bin/bash
# =============================================================================
# MING Stack 테스트 스크립트
# 라즈베리파이 4/5 산업용 IoT 플랫폼
# =============================================================================

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 테스트 결과 카운터
PASSED=0
FAILED=0
WARNINGS=0

# =============================================================================
# 유틸리티 함수
# =============================================================================

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

test_pass() {
    echo -e "  ${GREEN}✓ PASS${NC}: $1"
    ((PASSED++))
}

test_fail() {
    echo -e "  ${RED}✗ FAIL${NC}: $1"
    ((FAILED++))
}

test_warn() {
    echo -e "  ${YELLOW}⚠ WARN${NC}: $1"
    ((WARNINGS++))
}

test_info() {
    echo -e "  ${BLUE}ℹ INFO${NC}: $1"
}

# =============================================================================
# 환경 체크
# =============================================================================

check_environment() {
    print_header "환경 체크"

    # Docker 설치 확인
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | awk '{print $3}' | tr -d ',')
        test_pass "Docker 설치됨: $DOCKER_VERSION"
    else
        test_fail "Docker가 설치되지 않음"
        exit 1
    fi

    # Docker Compose 확인
    if docker compose version &> /dev/null; then
        COMPOSE_VERSION=$(docker compose version | awk '{print $4}')
        test_pass "Docker Compose 설치됨: $COMPOSE_VERSION"
    else
        test_fail "Docker Compose가 설치되지 않음"
        exit 1
    fi

    # .env 파일 확인
    if [ -f .env ]; then
        test_pass ".env 파일 존재"
    else
        test_warn ".env 파일 없음 (.env.example에서 복사 필요)"
    fi

    # 아키텍처 확인
    ARCH=$(uname -m)
    if [[ "$ARCH" == "aarch64" || "$ARCH" == "arm64" ]]; then
        test_pass "ARM64 아키텍처 감지: $ARCH"
    else
        test_info "현재 아키텍처: $ARCH (라즈베리파이가 아닐 수 있음)"
    fi
}

# =============================================================================
# 컨테이너 상태 체크
# =============================================================================

check_containers() {
    print_header "컨테이너 상태 체크"

    # Mosquitto
    if docker ps --format '{{.Names}}' | grep -q "ming-mosquitto"; then
        STATUS=$(docker inspect --format='{{.State.Health.Status}}' ming-mosquitto 2>/dev/null || echo "unknown")
        if [[ "$STATUS" == "healthy" ]]; then
            test_pass "Mosquitto: healthy"
        else
            test_warn "Mosquitto: $STATUS"
        fi
    else
        test_fail "Mosquitto 컨테이너 실행 중 아님"
    fi

    # InfluxDB
    if docker ps --format '{{.Names}}' | grep -q "ming-influxdb"; then
        STATUS=$(docker inspect --format='{{.State.Health.Status}}' ming-influxdb 2>/dev/null || echo "unknown")
        if [[ "$STATUS" == "healthy" ]]; then
            test_pass "InfluxDB: healthy"
        else
            test_warn "InfluxDB: $STATUS"
        fi
    else
        test_fail "InfluxDB 컨테이너 실행 중 아님"
    fi

    # Node-RED
    if docker ps --format '{{.Names}}' | grep -q "ming-nodered"; then
        STATUS=$(docker inspect --format='{{.State.Health.Status}}' ming-nodered 2>/dev/null || echo "unknown")
        if [[ "$STATUS" == "healthy" ]]; then
            test_pass "Node-RED: healthy"
        else
            test_warn "Node-RED: $STATUS"
        fi
    else
        test_fail "Node-RED 컨테이너 실행 중 아님"
    fi

    # Grafana
    if docker ps --format '{{.Names}}' | grep -q "ming-grafana"; then
        STATUS=$(docker inspect --format='{{.State.Health.Status}}' ming-grafana 2>/dev/null || echo "unknown")
        if [[ "$STATUS" == "healthy" ]]; then
            test_pass "Grafana: healthy"
        else
            test_warn "Grafana: $STATUS"
        fi
    else
        test_fail "Grafana 컨테이너 실행 중 아님"
    fi
}

# =============================================================================
# 포트 체크
# =============================================================================

check_ports() {
    print_header "포트 체크"

    # 환경변수 로드
    source .env 2>/dev/null || true

    MQTT_PORT=${MQTT_PORT:-1883}
    INFLUXDB_PORT=${INFLUXDB_PORT:-8086}
    NODERED_PORT=${NODERED_PORT:-1880}
    GRAFANA_PORT=${GRAFANA_PORT:-3000}

    # Mosquitto MQTT
    if nc -z localhost $MQTT_PORT 2>/dev/null; then
        test_pass "MQTT 포트 $MQTT_PORT 열림"
    else
        test_fail "MQTT 포트 $MQTT_PORT 닫힘"
    fi

    # InfluxDB
    if nc -z localhost $INFLUXDB_PORT 2>/dev/null; then
        test_pass "InfluxDB 포트 $INFLUXDB_PORT 열림"
    else
        test_fail "InfluxDB 포트 $INFLUXDB_PORT 닫힘"
    fi

    # Node-RED
    if nc -z localhost $NODERED_PORT 2>/dev/null; then
        test_pass "Node-RED 포트 $NODERED_PORT 열림"
    else
        test_fail "Node-RED 포트 $NODERED_PORT 닫힘"
    fi

    # Grafana
    if nc -z localhost $GRAFANA_PORT 2>/dev/null; then
        test_pass "Grafana 포트 $GRAFANA_PORT 열림"
    else
        test_fail "Grafana 포트 $GRAFANA_PORT 닫힘"
    fi
}

# =============================================================================
# MQTT 연결 테스트
# =============================================================================

check_mqtt() {
    print_header "MQTT 연결 테스트"

    # 환경변수 로드
    source .env 2>/dev/null || true

    MQTT_USER=${MQTT_USER:-mqtt_user}
    MQTT_PASSWORD=${MQTT_PASSWORD:-mqtt_pass}
    MQTT_PORT=${MQTT_PORT:-1883}

    # mosquitto_pub/sub 설치 확인
    if ! command -v mosquitto_pub &> /dev/null; then
        test_warn "mosquitto-clients 미설치 (MQTT 테스트 건너뜀)"
        return
    fi

    # MQTT 발행 테스트
    TEST_MSG="test_$(date +%s)"
    if timeout 5 mosquitto_pub -h localhost -p $MQTT_PORT -u "$MQTT_USER" -P "$MQTT_PASSWORD" -t "ming/test" -m "$TEST_MSG" 2>/dev/null; then
        test_pass "MQTT 발행 성공"
    else
        test_fail "MQTT 발행 실패 (인증 정보 확인 필요)"
    fi
}

# =============================================================================
# InfluxDB API 테스트
# =============================================================================

check_influxdb() {
    print_header "InfluxDB API 테스트"

    # 환경변수 로드
    source .env 2>/dev/null || true

    INFLUXDB_PORT=${INFLUXDB_PORT:-8086}
    INFLUXDB_TOKEN=${INFLUXDB_TOKEN:-ming-super-secret-token}
    INFLUXDB_ORG=${INFLUXDB_ORG:-ming-org}
    INFLUXDB_BUCKET=${INFLUXDB_BUCKET:-factory}

    # 헬스 체크
    HEALTH=$(curl -sf "http://localhost:$INFLUXDB_PORT/health" 2>/dev/null)
    if echo "$HEALTH" | grep -q '"status":"pass"'; then
        test_pass "InfluxDB 헬스 체크 통과"
    else
        test_fail "InfluxDB 헬스 체크 실패"
        return
    fi

    # 버킷 확인
    BUCKETS=$(curl -sf "http://localhost:$INFLUXDB_PORT/api/v2/buckets" \
        -H "Authorization: Token $INFLUXDB_TOKEN" 2>/dev/null)
    if echo "$BUCKETS" | grep -q "$INFLUXDB_BUCKET"; then
        test_pass "InfluxDB 버킷 '$INFLUXDB_BUCKET' 존재"
    else
        test_warn "InfluxDB 버킷 '$INFLUXDB_BUCKET' 없음 (자동 생성됨)"
    fi
}

# =============================================================================
# Node-RED API 테스트
# =============================================================================

check_nodered() {
    print_header "Node-RED API 테스트"

    # 환경변수 로드
    source .env 2>/dev/null || true

    NODERED_PORT=${NODERED_PORT:-1880}

    # 헬스 체크
    HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" "http://localhost:$NODERED_PORT" 2>/dev/null)
    if [[ "$HTTP_CODE" == "200" ]]; then
        test_pass "Node-RED 웹 UI 접근 가능"
    else
        test_fail "Node-RED 웹 UI 접근 실패 (HTTP $HTTP_CODE)"
    fi

    # 플로우 API 체크
    FLOWS=$(curl -sf "http://localhost:$NODERED_PORT/flows" 2>/dev/null)
    if [ -n "$FLOWS" ]; then
        test_pass "Node-RED 플로우 API 접근 가능"
    else
        test_warn "Node-RED 플로우 API 접근 실패"
    fi
}

# =============================================================================
# Grafana API 테스트
# =============================================================================

check_grafana() {
    print_header "Grafana API 테스트"

    # 환경변수 로드
    source .env 2>/dev/null || true

    GRAFANA_PORT=${GRAFANA_PORT:-3000}
    GRAFANA_USER=${GRAFANA_USER:-admin}
    GRAFANA_PASSWORD=${GRAFANA_PASSWORD:-admin123}

    # 헬스 체크
    HEALTH=$(curl -sf "http://localhost:$GRAFANA_PORT/api/health" 2>/dev/null)
    if echo "$HEALTH" | grep -q '"database":"ok"'; then
        test_pass "Grafana 헬스 체크 통과"
    else
        test_fail "Grafana 헬스 체크 실패"
        return
    fi

    # 데이터소스 확인
    DATASOURCES=$(curl -sf "http://$GRAFANA_USER:$GRAFANA_PASSWORD@localhost:$GRAFANA_PORT/api/datasources" 2>/dev/null)
    if echo "$DATASOURCES" | grep -q "InfluxDB"; then
        test_pass "Grafana InfluxDB 데이터소스 설정됨"
    else
        test_warn "Grafana InfluxDB 데이터소스 미설정"
    fi
}

# =============================================================================
# 시뮬레이터 체크
# =============================================================================

check_simulators() {
    print_header "시뮬레이터 체크"

    # 환경변수 로드
    source .env 2>/dev/null || true

    MODBUS_PORT=${MODBUS_PORT:-5020}
    OPCUA_PORT=${OPCUA_PORT:-4840}
    S7_PORT=${S7_PORT:-1102}
    MELSEC_PORT=${MELSEC_PORT:-5000}

    # Modbus 시뮬레이터
    if docker ps --format '{{.Names}}' | grep -q "ming-modbus-simulator"; then
        if nc -z localhost $MODBUS_PORT 2>/dev/null; then
            test_pass "Modbus 시뮬레이터 포트 $MODBUS_PORT 열림"
        else
            test_warn "Modbus 시뮬레이터 포트 $MODBUS_PORT 닫힘"
        fi
    else
        test_info "Modbus 시뮬레이터 실행 중 아님 (--profile simulators 필요)"
    fi

    # OPC-UA 시뮬레이터
    if docker ps --format '{{.Names}}' | grep -q "ming-opcua-simulator"; then
        if nc -z localhost $OPCUA_PORT 2>/dev/null; then
            test_pass "OPC-UA 시뮬레이터 포트 $OPCUA_PORT 열림"
        else
            test_warn "OPC-UA 시뮬레이터 포트 $OPCUA_PORT 닫힘"
        fi
    else
        test_info "OPC-UA 시뮬레이터 실행 중 아님 (--profile simulators 필요)"
    fi

    # S7 시뮬레이터
    if docker ps --format '{{.Names}}' | grep -q "ming-s7-simulator"; then
        if nc -z localhost $S7_PORT 2>/dev/null; then
            test_pass "S7 시뮬레이터 포트 $S7_PORT 열림"
        else
            test_warn "S7 시뮬레이터 포트 $S7_PORT 닫힘"
        fi
    else
        test_info "S7 시뮬레이터 실행 중 아님 (--profile simulators 필요)"
    fi

    # MELSEC MC 시뮬레이터
    if docker ps --format '{{.Names}}' | grep -q "ming-melsec-simulator"; then
        if nc -z localhost $MELSEC_PORT 2>/dev/null; then
            test_pass "MELSEC 시뮬레이터 포트 $MELSEC_PORT 열림"
        else
            test_warn "MELSEC 시뮬레이터 포트 $MELSEC_PORT 닫힘"
        fi
    else
        test_info "MELSEC 시뮬레이터 실행 중 아님 (--profile simulators 필요)"
    fi
}

# =============================================================================
# 시스템 리소스 체크
# =============================================================================

check_resources() {
    print_header "시스템 리소스"

    # 메모리 사용량
    MEM_TOTAL=$(free -m | awk '/^Mem:/ {print $2}')
    MEM_USED=$(free -m | awk '/^Mem:/ {print $3}')
    MEM_PERCENT=$((MEM_USED * 100 / MEM_TOTAL))

    if [ $MEM_PERCENT -lt 80 ]; then
        test_pass "메모리 사용량: ${MEM_USED}MB / ${MEM_TOTAL}MB (${MEM_PERCENT}%)"
    else
        test_warn "메모리 사용량 높음: ${MEM_USED}MB / ${MEM_TOTAL}MB (${MEM_PERCENT}%)"
    fi

    # 디스크 사용량
    DISK_PERCENT=$(df / | awk 'NR==2 {print $5}' | tr -d '%')
    DISK_USED=$(df -h / | awk 'NR==2 {print $3}')
    DISK_TOTAL=$(df -h / | awk 'NR==2 {print $2}')

    if [ $DISK_PERCENT -lt 80 ]; then
        test_pass "디스크 사용량: ${DISK_USED} / ${DISK_TOTAL} (${DISK_PERCENT}%)"
    else
        test_warn "디스크 사용량 높음: ${DISK_USED} / ${DISK_TOTAL} (${DISK_PERCENT}%)"
    fi

    # CPU 온도 (라즈베리파이)
    if command -v vcgencmd &> /dev/null; then
        TEMP=$(vcgencmd measure_temp | cut -d= -f2 | cut -d\' -f1)
        if (( $(echo "$TEMP < 70" | bc -l) )); then
            test_pass "CPU 온도: ${TEMP}°C"
        elif (( $(echo "$TEMP < 80" | bc -l) )); then
            test_warn "CPU 온도 높음: ${TEMP}°C"
        else
            test_fail "CPU 온도 위험: ${TEMP}°C (쿨링 필요)"
        fi
    fi
}

# =============================================================================
# 테스트 요약
# =============================================================================

print_summary() {
    print_header "테스트 요약"

    TOTAL=$((PASSED + FAILED + WARNINGS))

    echo ""
    echo -e "  ${GREEN}통과${NC}: $PASSED"
    echo -e "  ${RED}실패${NC}: $FAILED"
    echo -e "  ${YELLOW}경고${NC}: $WARNINGS"
    echo -e "  ────────────"
    echo -e "  총계: $TOTAL"
    echo ""

    if [ $FAILED -eq 0 ]; then
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}  모든 테스트 통과! MING Stack이 정상 작동 중입니다.${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        exit 0
    else
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${RED}  $FAILED 개의 테스트가 실패했습니다. 로그를 확인하세요.${NC}"
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        exit 1
    fi
}

# =============================================================================
# 메인 실행
# =============================================================================

main() {
    echo ""
    echo "============================================================"
    echo "  MING Stack 테스트"
    echo "  $(date)"
    echo "============================================================"

    # 프로젝트 디렉토리로 이동
    cd "$(dirname "$0")/.."

    check_environment
    check_containers
    check_ports
    check_mqtt
    check_influxdb
    check_nodered
    check_grafana
    check_simulators
    check_resources
    print_summary
}

main "$@"
