# MING Stack - 산업용 IoT 플랫폼 튜토리얼

> **Mosquitto(MQTT) + InfluxDB + Node-RED + Grafana**
> 라즈베리파이 4/5 기반 산업현장 IoT 데이터 수집 및 모니터링 플랫폼

---

## 목차

1. [MING Stack 개요](#1-ming-stack-개요)
2. [기술스택 상세 설명](#2-기술스택-상세-설명)
3. [시스템 요구사항](#3-시스템-요구사항)
4. [빠른 시작](#4-빠른-시작)
5. [상세 설정 가이드](#5-상세-설정-가이드)
6. [산업용 프로토콜 시뮬레이션](#6-산업용-프로토콜-시뮬레이션)
7. [MQTT 토픽 구조 설계](#7-mqtt-토픽-구조-설계)
8. [실제 산업현장 구성 예제](#8-실제-산업현장-구성-예제)
9. [문제 해결](#9-문제-해결)

---

## 1. MING Stack 개요

### 1.1 MING Stack이란?

MING Stack은 산업용 IoT(IIoT) 환경에서 데이터 수집, 처리, 저장, 시각화를 위한 오픈소스 기반 통합 솔루션입니다.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MING Stack Architecture                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│   │  Mosquitto  │    │  InfluxDB   │    │  Node-RED   │    │   Grafana   │  │
│   │   (MQTT     │───▶│  (Time-     │◀───│  (Flow      │───▶│  (Dashboard │  │
│   │   Broker)   │    │   Series)   │    │   Engine)   │    │   & Alert)  │  │
│   └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│         ▲                                      │                            │
│         │                                      │                            │
│   ┌─────┴───────────────────────────────────────┴─────┐                     │
│   │              산업용 디바이스/센서                    │                     │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌───────┐  │                     │
│   │  │ Modbus  │  │ OPC-UA  │  │ Siemens │  │ MQTT  │  │                     │
│   │  │   TCP   │  │ Server  │  │   PLC   │  │Devices│  │                     │
│   │  └─────────┘  └─────────┘  └─────────┘  └───────┘  │                     │
│   └─────────────────────────────────────────────────────┘                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 왜 MING Stack인가?

| 특징 | 설명 |
|------|------|
| **오픈소스** | 라이선스 비용 없이 상용 수준의 IoT 플랫폼 구축 |
| **경량화** | 라즈베리파이에서도 원활하게 동작 |
| **확장성** | 수천 개의 센서 데이터 처리 가능 |
| **유연성** | 다양한 산업용 프로토콜 지원 |
| **실시간** | 밀리초 단위의 실시간 데이터 처리 |

### 1.3 산업현장 적용 분야

- **스마트 팩토리**: 생산라인 모니터링, 설비 예지보전
- **에너지 관리**: 전력/가스/수도 사용량 모니터링
- **빌딩 자동화**: HVAC, 조명, 보안 시스템 통합
- **농업**: 스마트팜 환경 모니터링
- **물류**: 창고 환경 및 재고 관리

---

## 2. 기술스택 상세 설명

### 2.1 Mosquitto (MQTT Broker)

#### 개요
Eclipse Mosquitto는 MQTT 프로토콜을 구현한 경량 메시지 브로커입니다.

#### MQTT 프로토콜 특징

```
┌─────────────────────────────────────────────────────────────┐
│                    MQTT 통신 구조                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│    Publisher                  Broker               Subscriber│
│   ┌─────────┐              ┌─────────┐              ┌───────┐│
│   │ Sensor  │──PUBLISH────▶│Mosquitto│──SUBSCRIBE──▶│Node-RED││
│   │  Data   │              │         │              │       ││
│   └─────────┘              └─────────┘              └───────┘│
│                                                             │
│   Topic: factory/line1/temperature                          │
│   Payload: {"value": 25.5, "unit": "celsius"}              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### QoS (Quality of Service) 레벨

| QoS | 이름 | 설명 | 사용 사례 |
|-----|------|------|----------|
| 0 | At most once | 최대 1회 전송 (Fire & Forget) | 주기적 센서 데이터 |
| 1 | At least once | 최소 1회 전송 보장 | 일반적인 IoT 데이터 |
| 2 | Exactly once | 정확히 1회 전송 | 결제, 알람 등 중요 데이터 |

#### 산업현장 활용

- **센서 데이터 수집**: 수천 개의 센서에서 실시간 데이터 수집
- **제어 명령 전달**: PLC/HMI로 제어 명령 전송
- **이벤트 알림**: 알람 및 경고 메시지 배포

---

### 2.2 InfluxDB (Time-Series Database)

#### 개요
InfluxDB는 시계열 데이터에 최적화된 데이터베이스로, IoT 센서 데이터 저장에 적합합니다.

#### 핵심 개념

```
┌─────────────────────────────────────────────────────────────┐
│                   InfluxDB 데이터 구조                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Measurement (테이블): temperature                           │
│  ├── Tags (인덱스): location=line1, sensor_id=temp_001      │
│  ├── Fields (값): value=25.5, humidity=60.2                 │
│  └── Timestamp: 2024-01-15T10:30:00Z                        │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ SELECT mean("value") FROM "temperature"                 │ │
│  │ WHERE "location" = 'line1'                              │ │
│  │ AND time > now() - 1h                                   │ │
│  │ GROUP BY time(5m)                                       │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 데이터 보존 정책 (Retention Policy)

```
Raw Data (1초 간격)     → 7일 보존
Downsampled (1분 평균)  → 30일 보존
Downsampled (1시간 평균) → 1년 보존
Aggregated (1일 평균)   → 영구 보존
```

#### 산업현장 활용

- **트렌드 분석**: 장기간 데이터 추세 분석
- **이상 탐지**: 정상 범위 이탈 감지
- **예지보전**: 설비 상태 예측

---

### 2.3 Node-RED (Flow-based Programming)

#### 개요
Node-RED는 IBM이 개발한 플로우 기반 프로그래밍 도구로, 하드웨어 장치, API, 온라인 서비스를 연결합니다.

#### 핵심 기능

```
┌─────────────────────────────────────────────────────────────┐
│                    Node-RED 플로우 예시                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐ │
│  │  Modbus  │──▶│ Function │──▶│   MQTT   │──▶│ InfluxDB │ │
│  │   Read   │   │  (변환)   │   │  Publish │   │  Write   │ │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘ │
│       │                                                     │
│       ▼                                                     │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐                │
│  │  Switch  │──▶│  Alarm   │──▶│   Email  │                │
│  │ (조건분기) │   │ Trigger  │   │  Alert   │                │
│  └──────────┘   └──────────┘   └──────────┘                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 지원 프로토콜

| 프로토콜 | 노드 패키지 | 용도 |
|---------|------------|------|
| Modbus TCP/RTU | node-red-contrib-modbus | PLC, 센서 통신 |
| OPC-UA | node-red-contrib-opcua | 산업용 표준 통신 |
| S7 (Siemens) | node-red-contrib-s7 | Siemens PLC |
| BACnet | node-red-contrib-bacnet | 빌딩 자동화 |
| MQTT | 내장 | IoT 디바이스 |

#### 산업현장 활용

- **프로토콜 변환**: 다양한 프로토콜을 MQTT로 통합
- **데이터 전처리**: 필터링, 변환, 집계
- **비즈니스 로직**: 알람, 제어 로직 구현

---

### 2.4 Grafana (Visualization & Alerting)

#### 개요
Grafana는 메트릭 데이터 시각화 및 모니터링을 위한 오픈소스 플랫폼입니다.

#### 핵심 기능

```
┌─────────────────────────────────────────────────────────────┐
│                   Grafana 대시보드 구조                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  📊 Production Line Dashboard                           ││
│  ├─────────────────────────────────────────────────────────┤│
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ││
│  │  │ Temperature  │  │  Humidity    │  │   Pressure   │  ││
│  │  │    25.5°C    │  │    60.2%     │  │   1.2 bar    │  ││
│  │  │   ▲ 0.5°C    │  │   ▼ 2.1%     │  │   → 0.0      │  ││
│  │  └──────────────┘  └──────────────┘  └──────────────┘  ││
│  │                                                         ││
│  │  ┌─────────────────────────────────────────────────────┐││
│  │  │ 📈 Temperature Trend (Last 24 Hours)                │││
│  │  │    ╭───╮     ╭────╮                                 │││
│  │  │ ───╯   ╰─────╯    ╰───────────────                  │││
│  │  └─────────────────────────────────────────────────────┘││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 알람 기능

- **조건 기반 알람**: 임계값 초과 시 알림
- **다중 채널**: Email, Slack, Telegram 등
- **에스컬레이션**: 단계별 알람 전파

#### 산업현장 활용

- **실시간 모니터링**: 생산라인 상태 시각화
- **성과 지표 (KPI)**: OEE, 가동률 등
- **보고서**: 일간/주간/월간 리포트 생성

---

## 3. 시스템 요구사항

### 3.1 하드웨어 (라즈베리파이 4/5)

| 구성요소 | 최소 사양 | 권장 사양 |
|---------|----------|----------|
| 모델 | Raspberry Pi 4 (2GB) | Raspberry Pi 5 (8GB) |
| 저장장치 | 16GB SD Card | 64GB+ SSD (USB 3.0) |
| 네트워크 | 이더넷 또는 WiFi | 이더넷 (고정 IP) |
| 전원 | 5V 3A | 5V 5A (Pi 5) |

### 3.2 소프트웨어

```bash
# OS 권장 버전
Raspberry Pi OS (64-bit) Bookworm

# 필수 소프트웨어
Docker: 24.0+
Docker Compose: 2.20+
Git: 2.30+
```

---

## 4. 빠른 시작

### 4.1 라즈베리파이 초기 설정

```bash
# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 현재 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER

# Docker Compose 설치 (최신 버전)
sudo apt install -y docker-compose-plugin

# 재부팅 후 적용
sudo reboot
```

### 4.2 MING Stack 배포

```bash
# 프로젝트 클론
git clone https://github.com/your-repo/MING_Stack.git
cd MING_Stack

# 환경 변수 설정
cp .env.example .env
nano .env  # 필요시 수정

# 스택 시작
docker compose up -d

# 상태 확인
docker compose ps
```

### 4.3 서비스 접속 정보

| 서비스 | URL | 기본 계정 |
|--------|-----|----------|
| Node-RED | http://raspberrypi:1880 | admin / admin123 |
| Grafana | http://raspberrypi:3000 | admin / admin123 |
| InfluxDB | http://raspberrypi:8086 | admin / admin123456 |
| Mosquitto | raspberrypi:1883 | mqtt_user / mqtt_pass |

---

## 5. 상세 설정 가이드

상세한 설정 가이드는 다음 문서를 참조하세요:

- [Docker Compose 설정](docs/01-docker-compose-setup.md)
- [Mosquitto MQTT 설정](docs/02-mosquitto-setup.md)
- [InfluxDB 설정](docs/03-influxdb-setup.md)
- [Node-RED 설정](docs/04-nodered-setup.md)
- [Grafana 설정](docs/05-grafana-setup.md)

---

## 6. 산업용 프로토콜 시뮬레이션

상세한 시뮬레이션 가이드는 다음 문서를 참조하세요:

- [Modbus TCP 시뮬레이션](docs/06-modbus-simulation.md)
- [OPC-UA 시뮬레이션](docs/07-opcua-simulation.md)
- [Siemens S7 시뮬레이션](docs/08-siemens-simulation.md)

---

## 7. MQTT 토픽 구조 설계

상세한 토픽 설계 가이드는 다음 문서를 참조하세요:

- [MQTT 토픽 구조 가이드](docs/09-mqtt-topic-structure.md)

---

## 8. 실제 산업현장 구성 예제

상세한 산업현장 구성 예제는 다음 문서를 참조하세요:

- [스마트 팩토리 구성](docs/10-smart-factory-example.md)

---

## 9. 문제 해결

### 일반적인 문제

#### Docker 컨테이너 시작 실패
```bash
# 로그 확인
docker compose logs -f [service_name]

# 컨테이너 재시작
docker compose restart [service_name]
```

#### 메모리 부족
```bash
# 스왑 메모리 확장 (2GB)
sudo dphys-swapfile swapoff
sudo sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=2048/' /etc/dphys-swapfile
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

#### 디스크 공간 부족
```bash
# Docker 정리
docker system prune -a

# InfluxDB 오래된 데이터 정리
# InfluxDB UI에서 Data > Buckets에서 보존 정책 설정
```

---

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 기여

이슈 및 풀 리퀘스트를 환영합니다!
