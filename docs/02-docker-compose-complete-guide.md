# Docker Compose 완벽 가이드 - MING Stack

이 문서는 Docker를 전혀 모르는 분들을 위해 작성되었습니다. docker-compose.yml 파일의 모든 내용을 하나하나 상세히 설명합니다.

---

## 목차

1. [Docker란 무엇인가?](#1-docker란-무엇인가)
2. [Docker Compose란?](#2-docker-compose란)
3. [docker-compose.yml 파일 기본 구조](#3-docker-composeyml-파일-기본-구조)
4. [MING Stack 서비스 상세 설명](#4-ming-stack-서비스-상세-설명)
5. [네트워크 설정](#5-네트워크-설정)
6. [볼륨 설정](#6-볼륨-설정)
7. [자주 사용하는 명령어](#7-자주-사용하는-명령어)
8. [문제 해결 가이드](#8-문제-해결-가이드)

---

## 1. Docker란 무엇인가?

### 1.1 쉬운 비유로 이해하기

Docker를 이해하기 위해 **이사**를 예로 들어보겠습니다.

**기존 방식 (Docker 없이):**
```
새 집에 이사할 때:
1. 가구를 하나씩 옮긴다
2. 새 집에서 가구를 다시 배치한다
3. 전기, 수도 등을 새로 연결한다
4. 인터넷도 새로 설치한다
→ 매우 번거롭고 시간이 오래 걸림
```

**Docker 방식:**
```
집 전체를 컨테이너 박스에 담아서 이동:
1. 집 전체(가구, 전기, 수도, 인터넷 모두 포함)를 박스에 넣는다
2. 박스를 새 위치에 놓는다
3. 끝!
→ 어디서든 동일하게 작동
```

### 1.2 핵심 개념

| 용어 | 설명 | 비유 |
|------|------|------|
| **이미지(Image)** | 프로그램 실행에 필요한 모든 것을 담은 템플릿 | 요리 레시피 |
| **컨테이너(Container)** | 이미지를 실행한 상태 | 레시피로 만든 실제 요리 |
| **볼륨(Volume)** | 데이터를 영구적으로 저장하는 공간 | USB 메모리 |
| **네트워크(Network)** | 컨테이너들이 서로 통신하는 방법 | 전화선 |

### 1.3 왜 Docker를 사용하나요?

```
❌ Docker 없이:
"내 컴퓨터에서는 되는데, 왜 네 컴퓨터에서는 안 돼?"
→ 버전 차이, 설정 차이, 운영체제 차이 등 문제 발생

✅ Docker 사용:
"내 컴퓨터에서 되면, 모든 컴퓨터에서 된다!"
→ 동일한 환경이 보장됨
```

---

## 2. Docker Compose란?

### 2.1 Docker vs Docker Compose

| Docker | Docker Compose |
|--------|----------------|
| 컨테이너 1개를 다룸 | 여러 컨테이너를 한 번에 다룸 |
| 명령어가 길고 복잡함 | 설정 파일 하나로 간편하게 관리 |
| `docker run ...` | `docker compose up` |

### 2.2 예시로 이해하기

**Docker만 사용할 경우 (7개 서비스 각각 실행):**
```bash
docker run -d --name mosquitto -p 1883:1883 eclipse-mosquitto:2
docker run -d --name influxdb -p 8086:8086 influxdb:2.7
docker run -d --name nodered -p 1880:1880 nodered/node-red
docker run -d --name grafana -p 3000:3000 grafana/grafana
# ... 계속 반복 (총 7번)
```

**Docker Compose 사용 (한 번에 실행):**
```bash
docker compose up -d
```

→ docker-compose.yml 파일에 모든 설정이 저장되어 있어서 한 줄로 끝!

---

## 3. docker-compose.yml 파일 기본 구조

### 3.1 YAML 파일이란?

YAML은 설정 파일을 작성하는 형식입니다. 들여쓰기(스페이스)가 매우 중요합니다!

```yaml
# 이것은 주석입니다 (설명용, 실행에 영향 없음)

# 키: 값 형식
이름: 홍길동
나이: 25

# 목록 (배열)
취미:
  - 독서
  - 영화
  - 게임

# 중첩 구조
주소:
  도시: 서울
  구: 강남구
```

### 3.2 docker-compose.yml 최상위 구조

```yaml
# 주석: Docker Compose V2에서는 version 불필요

services:      # ← 실행할 프로그램들 정의
  서비스1:
    ...
  서비스2:
    ...

networks:      # ← 네트워크 설정
  네트워크이름:
    ...

volumes:       # ← 저장소 설정
  볼륨이름:
    ...
```

### 3.3 들여쓰기 규칙

```yaml
services:                    # 레벨 0 (맨 앞)
  mosquitto:                 # 레벨 1 (스페이스 2칸)
    image: eclipse-mosquitto # 레벨 2 (스페이스 4칸)
    ports:                   # 레벨 2
      - "1883:1883"          # 레벨 3 (스페이스 6칸)
```

> ⚠️ **주의**: 탭(Tab) 대신 반드시 스페이스를 사용해야 합니다!

---

## 4. MING Stack 서비스 상세 설명

MING Stack은 7개의 서비스(컨테이너)로 구성됩니다.

### 4.1 Mosquitto (MQTT 브로커)

```yaml
mosquitto:
  image: eclipse-mosquitto:2
  container_name: ming-mosquitto
  restart: unless-stopped
  ports:
    - "1883:1883"
    - "9001:9001"
  volumes:
    - ./mosquitto/config:/mosquitto/config:ro
    - ./mosquitto/data:/mosquitto/data
    - ./mosquitto/log:/mosquitto/log
  networks:
    - ming-network
  healthcheck:
    test: ["CMD", "mosquitto_sub", "-t", "$$SYS/#", "-C", "1", "-i", "healthcheck", "-W", "3"]
    interval: 30s
    timeout: 10s
    retries: 3
```

#### 각 줄 상세 설명:

| 설정 | 값 | 설명 |
|------|-----|------|
| `image` | `eclipse-mosquitto:2` | 사용할 Docker 이미지. Docker Hub에서 다운로드됨. `:2`는 버전 2.x를 의미 |
| `container_name` | `ming-mosquitto` | 컨테이너에 붙일 이름. `docker ps`에서 이 이름으로 표시됨 |
| `restart` | `unless-stopped` | 재시작 정책. 컴퓨터를 재부팅해도 자동 시작 (수동 중지 시 제외) |

#### ports 상세:

```yaml
ports:
  - "1883:1883"     # MQTT 프로토콜
  - "9001:9001"     # WebSocket
```

**포트 매핑 형식: `"호스트포트:컨테이너포트"`**

```
┌────────────────────────────────────────────┐
│         라즈베리파이 (호스트)                │
│                                             │
│   외부 요청 ──────► 포트 1883               │
│                        │                    │
│                        ▼                    │
│   ┌─────────────────────────────────────┐  │
│   │        Mosquitto 컨테이너           │  │
│   │                                     │  │
│   │   포트 1883에서 수신 대기 중         │  │
│   └─────────────────────────────────────┘  │
└────────────────────────────────────────────┘
```

| 포트 | 용도 |
|------|------|
| 1883 | 일반 MQTT 연결용 |
| 9001 | 웹 브라우저 WebSocket 연결용 |

#### volumes 상세:

```yaml
volumes:
  - ./mosquitto/config:/mosquitto/config:ro
  - ./mosquitto/data:/mosquitto/data
  - ./mosquitto/log:/mosquitto/log
```

**볼륨 매핑 형식: `호스트경로:컨테이너경로[:옵션]`**

```
┌─ 라즈베리파이 (호스트) ─┐    ┌─ 컨테이너 내부 ─┐
│                         │    │                 │
│ ./mosquitto/config ────────► /mosquitto/config │
│ ./mosquitto/data  ─────────► /mosquitto/data   │
│ ./mosquitto/log   ─────────► /mosquitto/log    │
│                         │    │                 │
└─────────────────────────┘    └─────────────────┘
```

| 옵션 | 설명 |
|------|------|
| `:ro` | Read-Only. 컨테이너가 이 폴더를 수정할 수 없음 (설정 파일 보호용) |
| (없음) | Read-Write. 컨테이너가 읽기/쓰기 가능 (데이터 저장용) |

> **왜 볼륨을 사용하나요?**
> 컨테이너를 삭제하면 내부 데이터도 사라집니다. 볼륨을 사용하면 데이터가 호스트(라즈베리파이)에 저장되어 컨테이너를 삭제해도 데이터가 유지됩니다.

#### healthcheck 상세:

```yaml
healthcheck:
  test: ["CMD", "mosquitto_sub", "-t", "$$SYS/#", "-C", "1", "-i", "healthcheck", "-W", "3"]
  interval: 30s
  timeout: 10s
  retries: 3
```

**상태 확인(Health Check)**: Docker가 주기적으로 컨테이너가 정상인지 확인

| 설정 | 값 | 설명 |
|------|-----|------|
| `test` | 명령어 | 이 명령이 성공하면 "건강함" |
| `interval` | `30s` | 30초마다 확인 |
| `timeout` | `10s` | 10초 내에 응답 없으면 실패 |
| `retries` | `3` | 3번 연속 실패하면 "비정상" 상태 |

---

### 4.2 InfluxDB (시계열 데이터베이스)

```yaml
influxdb:
  image: influxdb:2.7
  container_name: ming-influxdb
  restart: unless-stopped
  ports:
    - "8086:8086"
  environment:
    - DOCKER_INFLUXDB_INIT_MODE=setup
    - DOCKER_INFLUXDB_INIT_USERNAME=${INFLUXDB_USERNAME:-admin}
    - DOCKER_INFLUXDB_INIT_PASSWORD=${INFLUXDB_PASSWORD:-admin123456}
    - DOCKER_INFLUXDB_INIT_ORG=${INFLUXDB_ORG:-ming-org}
    - DOCKER_INFLUXDB_INIT_BUCKET=${INFLUXDB_BUCKET:-factory}
    - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=${INFLUXDB_TOKEN:-ming-super-secret-token}
    - DOCKER_INFLUXDB_INIT_RETENTION=${INFLUXDB_RETENTION:-7d}
  volumes:
    - ./influxdb/data:/var/lib/influxdb2
    - ./influxdb/config:/etc/influxdb2
  networks:
    - ming-network
  healthcheck:
    test: ["CMD", "influx", "ping"]
    interval: 30s
    timeout: 10s
    retries: 3
```

#### environment (환경 변수) 상세:

환경 변수는 컨테이너 내부에서 사용되는 설정값입니다.

```yaml
environment:
  - DOCKER_INFLUXDB_INIT_MODE=setup
  - DOCKER_INFLUXDB_INIT_USERNAME=${INFLUXDB_USERNAME:-admin}
```

**`${변수명:-기본값}` 형식 설명:**

```
${INFLUXDB_USERNAME:-admin}

해석:
1. .env 파일에서 INFLUXDB_USERNAME 값을 찾는다
2. 있으면 그 값을 사용
3. 없으면 "admin"을 기본값으로 사용
```

| 환경 변수 | 기본값 | 설명 |
|-----------|--------|------|
| `INIT_MODE` | `setup` | 첫 실행 시 자동 초기 설정 |
| `INIT_USERNAME` | `admin` | 관리자 계정 이름 |
| `INIT_PASSWORD` | `admin123456` | 관리자 비밀번호 |
| `INIT_ORG` | `ming-org` | 조직(Organization) 이름 |
| `INIT_BUCKET` | `factory` | 데이터 저장소(버킷) 이름 |
| `INIT_ADMIN_TOKEN` | `ming-super-secret-token` | API 접근용 토큰 |
| `INIT_RETENTION` | `7d` | 데이터 보관 기간 (7일) |

---

### 4.3 Node-RED (플로우 프로그래밍)

```yaml
nodered:
  build:
    context: ./nodered
    dockerfile: Dockerfile
  container_name: ming-nodered
  restart: unless-stopped
  ports:
    - "1880:1880"
  environment:
    - TZ=${TIMEZONE:-Asia/Seoul}
    - NODE_RED_CREDENTIAL_SECRET=${NODERED_CREDENTIAL_SECRET:-ming-secret-key}
  volumes:
    - ./nodered/data:/data
  networks:
    - ming-network
  depends_on:
    - mosquitto
    - influxdb
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:1880/"]
    interval: 30s
    timeout: 10s
    retries: 3
```

#### build vs image 차이:

```yaml
# 방법 1: 미리 만들어진 이미지 사용
image: eclipse-mosquitto:2

# 방법 2: 직접 이미지 빌드
build:
  context: ./nodered      # Dockerfile이 있는 폴더
  dockerfile: Dockerfile  # 사용할 Dockerfile 이름
```

| 항목 | image | build |
|------|-------|-------|
| 소스 | Docker Hub에서 다운로드 | 로컬 Dockerfile로 직접 생성 |
| 커스터마이징 | 어려움 | 자유롭게 수정 가능 |
| 속도 | 빠름 (다운로드만) | 느림 (빌드 필요) |

**Node-RED는 왜 build를 사용하나요?**

추가 노드(Modbus, OPC-UA 등)를 설치해야 하므로 Dockerfile로 커스텀 이미지를 만듭니다.

#### depends_on 상세:

```yaml
depends_on:
  - mosquitto
  - influxdb
```

**의존성 설정**: Node-RED가 시작되기 전에 Mosquitto와 InfluxDB가 먼저 시작됨

```
시작 순서:
1. mosquitto 시작
2. influxdb 시작
3. nodered 시작 (1, 2가 준비된 후)
```

> ⚠️ **주의**: `depends_on`은 컨테이너 "시작" 순서만 보장합니다. 서비스가 "완전히 준비"될 때까지 기다리지는 않습니다. (그래서 healthcheck도 함께 사용)

---

### 4.4 Grafana (시각화 대시보드)

```yaml
grafana:
  image: grafana/grafana:latest
  container_name: ming-grafana
  restart: unless-stopped
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_USER=${GRAFANA_USER:-admin}
    - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin123}
    - GF_USERS_ALLOW_SIGN_UP=false
    - GF_SERVER_ROOT_URL=${GRAFANA_ROOT_URL:-http://localhost:3000}
    - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource
  volumes:
    - ./grafana/data:/var/lib/grafana
    - ./grafana/provisioning:/etc/grafana/provisioning:ro
    - ./grafana/dashboards:/var/lib/grafana/dashboards:ro
  networks:
    - ming-network
  depends_on:
    - influxdb
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
    interval: 30s
    timeout: 10s
    retries: 3
```

#### :latest 태그:

```yaml
image: grafana/grafana:latest
```

| 태그 | 의미 | 사용 시기 |
|------|------|-----------|
| `:latest` | 가장 최신 버전 | 항상 최신 기능을 원할 때 |
| `:2.7` | 특정 버전 | 안정적인 환경을 원할 때 |
| `:2` | 2.x 중 최신 | 메이저 버전은 고정, 마이너는 최신 |

#### GF_ 환경 변수:

Grafana는 `GF_` 접두어로 시작하는 환경 변수로 설정을 변경할 수 있습니다.

| 환경 변수 | 설명 |
|-----------|------|
| `GF_SECURITY_ADMIN_USER` | 관리자 계정명 |
| `GF_SECURITY_ADMIN_PASSWORD` | 관리자 비밀번호 |
| `GF_USERS_ALLOW_SIGN_UP` | 회원가입 허용 여부 (false = 비허용) |
| `GF_INSTALL_PLUGINS` | 자동 설치할 플러그인 목록 |

---

### 4.5 산업용 프로토콜 시뮬레이터

#### Modbus TCP 시뮬레이터

```yaml
modbus-simulator:
  build:
    context: ./nodered/simulators/modbus
    dockerfile: Dockerfile
  container_name: ming-modbus-simulator
  restart: unless-stopped
  ports:
    - "5020:5020"
  networks:
    - ming-network
```

**Modbus란?** 산업 자동화에서 가장 널리 사용되는 통신 프로토콜. PLC, 센서 등과 통신할 때 사용.

#### OPC-UA 시뮬레이터

```yaml
opcua-simulator:
  build:
    context: ./nodered/simulators/opcua
    dockerfile: Dockerfile
  container_name: ming-opcua-simulator
  restart: unless-stopped
  ports:
    - "4840:4840"
  networks:
    - ming-network
```

**OPC-UA란?** 산업 자동화의 표준 통신 프로토콜. 보안과 확장성이 뛰어남.

#### S7 시뮬레이터 (Siemens PLC)

```yaml
s7-simulator:
  build:
    context: ./nodered/simulators/s7
    dockerfile: Dockerfile
  container_name: ming-s7-simulator
  restart: unless-stopped
  ports:
    - "102:102"
  networks:
    - ming-network
```

**S7 프로토콜이란?** Siemens PLC와 통신하기 위한 프로토콜.

---

## 5. 네트워크 설정

```yaml
networks:
  ming-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### 5.1 네트워크가 필요한 이유

```
┌─────────────────────────────────────────────────────────┐
│                    ming-network                          │
│                                                          │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐           │
│   │mosquitto │◄─►│ nodered  │◄─►│ influxdb │           │
│   │          │   │          │   │          │           │
│   └──────────┘   └──────────┘   └──────────┘           │
│         ▲                              ▲                │
│         │                              │                │
│         │        ┌──────────┐          │                │
│         │        │ grafana  │──────────┘                │
│         │        └──────────┘                           │
│         │                                               │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐               │
│   │ modbus   │ │ opcua    │ │ s7       │               │
│   │simulator │ │simulator │ │simulator │               │
│   └──────────┘ └──────────┘ └──────────┘               │
└─────────────────────────────────────────────────────────┘
```

같은 네트워크에 있는 컨테이너들은 **컨테이너 이름**으로 서로 통신할 수 있습니다.

```yaml
# Node-RED에서 InfluxDB 접속 시:
# IP 주소 대신 컨테이너 이름 사용 가능
url: http://influxdb:8086   # ✅ 컨테이너 이름 사용
url: http://172.20.0.5:8086 # ❌ IP는 변경될 수 있음
```

### 5.2 네트워크 설정 상세

| 설정 | 값 | 설명 |
|------|-----|------|
| `driver` | `bridge` | 가장 일반적인 네트워크 종류. 같은 호스트 내 컨테이너 연결 |
| `subnet` | `172.20.0.0/16` | 사용할 IP 대역. 다른 네트워크와 충돌 방지 |

### 5.3 Bridge 네트워크란?

```
┌────────────────────────────────────────────────────────┐
│                   라즈베리파이                          │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │            Docker Bridge (ming-network)          │   │
│  │                                                  │   │
│  │   172.20.0.2    172.20.0.3    172.20.0.4        │   │
│  │   mosquitto     influxdb      nodered           │   │
│  │       ↑             ↑            ↑              │   │
│  │       └─────────────┼────────────┘              │   │
│  │                     │                           │   │
│  └─────────────────────┼───────────────────────────┘   │
│                        │                                │
│                     브릿지                              │
│                        │                                │
│                   라즈베리파이 eth0                     │
│                   192.168.1.100                         │
└────────────────────────────────────────────────────────┘
                         │
                         ▼
                    외부 네트워크
```

---

## 6. 볼륨 설정

```yaml
volumes:
  influxdb-data:
  grafana-data:
  nodered-data:
  mosquitto-data:
```

### 6.1 두 가지 볼륨 방식

#### 방식 1: 바인드 마운트 (Bind Mount)

```yaml
volumes:
  - ./mosquitto/data:/mosquitto/data  # 호스트 경로:컨테이너 경로
```

- 호스트의 특정 폴더를 컨테이너에 연결
- 호스트에서 직접 파일 수정 가능
- 이 프로젝트에서 주로 사용하는 방식

#### 방식 2: 네임드 볼륨 (Named Volume)

```yaml
volumes:
  influxdb-data:  # 이름만 선언

# 서비스에서 사용:
services:
  influxdb:
    volumes:
      - influxdb-data:/var/lib/influxdb2
```

- Docker가 관리하는 볼륨
- 호스트에서 직접 접근하기 어려움
- 백업/복원에 Docker 명령어 필요

### 6.2 MING Stack의 볼륨 구조

```
프로젝트 폴더/
├── mosquitto/
│   ├── config/     → /mosquitto/config (읽기 전용)
│   ├── data/       → /mosquitto/data
│   └── log/        → /mosquitto/log
├── influxdb/
│   ├── data/       → /var/lib/influxdb2
│   └── config/     → /etc/influxdb2
├── nodered/
│   └── data/       → /data
└── grafana/
    ├── data/       → /var/lib/grafana
    ├── provisioning/ → /etc/grafana/provisioning (읽기 전용)
    └── dashboards/  → /var/lib/grafana/dashboards (읽기 전용)
```

---

## 7. 자주 사용하는 명령어

### 7.1 기본 명령어

| 명령어 | 설명 |
|--------|------|
| `docker compose up -d` | 모든 서비스 백그라운드 시작 |
| `docker compose down` | 모든 서비스 중지 및 제거 |
| `docker compose ps` | 실행 중인 서비스 목록 |
| `docker compose logs` | 모든 서비스 로그 보기 |
| `docker compose restart` | 모든 서비스 재시작 |

### 7.2 특정 서비스만 다루기

```bash
# 특정 서비스만 시작
docker compose up -d nodered

# 특정 서비스 로그 보기
docker compose logs nodered

# 특정 서비스 로그 실시간 보기 (-f = follow)
docker compose logs -f nodered

# 특정 서비스 재시작
docker compose restart nodered

# 특정 서비스 중지
docker compose stop nodered
```

### 7.3 이미지 빌드 관련

```bash
# 이미지 다시 빌드 (코드 변경 후)
docker compose build nodered

# 캐시 없이 처음부터 빌드
docker compose build --no-cache nodered

# 빌드 후 시작
docker compose up -d --build nodered
```

### 7.4 컨테이너 내부 접속

```bash
# bash 쉘로 접속
docker exec -it ming-nodered bash

# sh 쉘로 접속 (bash 없는 경우)
docker exec -it ming-mosquitto sh
```

### 7.5 정리 명령어

```bash
# 중지된 컨테이너, 사용하지 않는 이미지 등 정리
docker system prune

# 모든 것 정리 (주의!)
docker system prune -a
```

---

## 8. 문제 해결 가이드

### 8.1 컨테이너가 시작되지 않을 때

```bash
# 1. 상태 확인
docker compose ps

# 2. 로그 확인
docker compose logs [서비스명]

# 3. 재빌드 시도
docker compose build --no-cache [서비스명]
docker compose up -d [서비스명]
```

### 8.2 포트 충돌

```
Error: bind: address already in use
```

```bash
# 어떤 프로세스가 포트를 사용 중인지 확인 (Linux/Mac)
sudo lsof -i :1883

# Windows
netstat -ano | findstr :1883
```

**해결 방법:**
1. 해당 프로세스 종료
2. 또는 docker-compose.yml에서 포트 변경:
   ```yaml
   ports:
     - "1884:1883"  # 호스트 포트를 1884로 변경
   ```

### 8.3 권한 오류

```
Error: permission denied
```

```bash
# 폴더 권한 설정
sudo chown -R 1000:1000 nodered/data
sudo chown -R 1883:1883 mosquitto/data mosquitto/log
sudo chown -R 472:472 grafana/data
```

### 8.4 메모리 부족

라즈베리파이에서 메모리 부족 시:

```bash
# 메모리 사용량 확인
docker stats

# 스왑 메모리 추가 (임시)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 8.5 이미지 다운로드 실패

```bash
# 수동으로 이미지 다운로드
docker pull eclipse-mosquitto:2
docker pull influxdb:2.7
docker pull grafana/grafana:latest
```

### 8.6 네트워크 연결 문제

```bash
# 네트워크 상태 확인
docker network ls
docker network inspect ming-network

# 네트워크 재생성
docker compose down
docker network prune
docker compose up -d
```

---

## 용어 정리

| 용어 | 영문 | 설명 |
|------|------|------|
| 이미지 | Image | 컨테이너를 만들기 위한 템플릿 |
| 컨테이너 | Container | 이미지를 실행한 인스턴스 |
| 서비스 | Service | docker-compose.yml에서 정의한 컨테이너 단위 |
| 볼륨 | Volume | 데이터 영구 저장소 |
| 네트워크 | Network | 컨테이너 간 통신 경로 |
| 포트 | Port | 네트워크 연결 지점 |
| 헬스체크 | Health Check | 컨테이너 상태 확인 기능 |
| 바인드 마운트 | Bind Mount | 호스트 폴더를 컨테이너에 연결 |

---

## 추가 학습 자료

- [Docker 공식 문서 (한글)](https://docs.docker.com/get-started/)
- [Docker Compose 공식 문서](https://docs.docker.com/compose/)
- [Docker Hub](https://hub.docker.com/) - 이미지 저장소
