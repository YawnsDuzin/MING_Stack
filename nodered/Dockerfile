# =============================================================================
# Node-RED Docker Image for MING Stack
# 라즈베리파이 4/5 ARM64 최적화
# =============================================================================

FROM nodered/node-red:latest-minimal

# 작업 디렉토리 설정
USER root

# 필수 시스템 패키지 설치
RUN apk add --no-cache \
    python3 \
    py3-pip \
    make \
    g++ \
    linux-headers

# Node-RED 사용자로 전환
USER node-red

# 산업용 프로토콜 노드 설치
RUN npm install --save \
    # MQTT (내장이지만 추가 기능)
    node-red-contrib-mqtt-broker \
    # Modbus TCP/RTU
    node-red-contrib-modbus \
    # OPC-UA
    node-red-contrib-opcua \
    # Siemens S7 PLC
    node-red-contrib-s7 \
    # InfluxDB
    node-red-contrib-influxdb \
    # 대시보드
    node-red-dashboard \
    # 유틸리티
    node-red-contrib-cron-plus \
    node-red-contrib-msg-speed \
    node-red-node-random

# 설정 파일 복사
COPY --chown=node-red:node-red settings.js /data/settings.js

# 초기 플로우 파일 복사
COPY --chown=node-red:node-red flows.json /data/flows.json
COPY --chown=node-red:node-red flows_cred.json /data/flows_cred.json

# 포트 노출
EXPOSE 1880

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:1880/ || exit 1
