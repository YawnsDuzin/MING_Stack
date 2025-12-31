# Docker Compose 설정 가이드

> 라즈베리파이 4/5를 위한 MING Stack Docker 구성

---

## 1. 사전 준비

### 1.1 라즈베리파이 OS 설치

```bash
# Raspberry Pi Imager를 사용하여 64비트 OS 설치
# 권장: Raspberry Pi OS (64-bit) Bookworm

# 설치 후 시스템 업데이트
sudo apt update && sudo apt upgrade -y
```

### 1.2 Docker 설치

```bash
# Docker 공식 설치 스크립트
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 현재 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER

# 로그아웃 후 다시 로그인 또는
newgrp docker

# Docker 버전 확인
docker --version
```

### 1.3 Docker Compose 설치

```bash
# Docker Compose V2 (docker compose)
sudo apt install -y docker-compose-plugin

# 버전 확인
docker compose version
```

---

## 2. 프로젝트 구조

```
MING_Stack/
├── docker-compose.yml          # 메인 컴포즈 파일
├── .env                        # 환경 변수
├── mosquitto/
│   ├── config/
│   │   ├── mosquitto.conf     # Mosquitto 설정
│   │   ├── passwd             # 사용자 비밀번호
│   │   └── acl                # 접근 제어
│   ├── data/                  # 영구 데이터
│   └── log/                   # 로그 파일
├── influxdb/
│   ├── config/                # InfluxDB 설정
│   └── data/                  # 데이터 저장소
├── nodered/
│   ├── Dockerfile             # 커스텀 이미지
│   ├── settings.js            # Node-RED 설정
│   ├── flows.json             # 플로우 정의
│   └── data/                  # 사용자 데이터
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/       # 데이터소스 자동 설정
│   │   └── dashboards/        # 대시보드 자동 로드
│   ├── dashboards/            # 대시보드 JSON
│   └── data/                  # Grafana 데이터
└── scripts/                   # 유틸리티 스크립트
```

---

## 3. 환경 변수 설정

### 3.1 .env 파일 생성

```bash
# .env.example을 복사
cp .env.example .env

# 편집
nano .env
```

### 3.2 주요 환경 변수

```bash
# 타임존
TIMEZONE=Asia/Seoul

# InfluxDB 설정
INFLUXDB_USERNAME=admin
INFLUXDB_PASSWORD=your_secure_password_here
INFLUXDB_ORG=ming-org
INFLUXDB_BUCKET=factory
INFLUXDB_TOKEN=your_influx_token_here
INFLUXDB_RETENTION=7d

# Grafana 설정
GRAFANA_USER=admin
GRAFANA_PASSWORD=your_grafana_password

# MQTT 설정
MQTT_USER=mqtt_user
MQTT_PASSWORD=mqtt_password
```

---

## 4. 서비스별 설정

### 4.1 Mosquitto 설정

```conf
# mosquitto/config/mosquitto.conf

persistence true
persistence_location /mosquitto/data/
log_dest file /mosquitto/log/mosquitto.log
log_dest stdout

listener 1883
protocol mqtt

listener 9001
protocol websockets

allow_anonymous false
password_file /mosquitto/config/passwd
acl_file /mosquitto/config/acl

max_connections 500
message_size_limit 1048576
```

### 4.2 비밀번호 생성

```bash
# 컨테이너 시작 후 비밀번호 생성
docker exec ming-mosquitto mosquitto_passwd -c /mosquitto/config/passwd mqtt_user

# 추가 사용자
docker exec ming-mosquitto mosquitto_passwd -b /mosquitto/config/passwd nodered mqtt_pass
```

---

## 5. 라즈베리파이 최적화

### 5.1 메모리 제한 설정

Docker Compose에서 각 서비스의 메모리 제한 설정:

```yaml
deploy:
  resources:
    limits:
      memory: 512M
    reservations:
      memory: 256M
```

### 5.2 스왑 메모리 확장

```bash
# 스왑 파일 크기 확인
free -h

# 스왑 확장 (2GB)
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# CONF_SWAPSIZE=2048

sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### 5.3 SSD 사용 권장

SD 카드 대신 USB SSD 사용 시 성능 및 수명 향상:

```bash
# USB 부팅 설정
sudo raspi-config
# Advanced Options > Boot Order > USB Boot
```

---

## 6. 스택 시작 및 관리

### 6.1 스택 시작

```bash
# 백그라운드에서 시작
docker compose up -d

# 로그 확인
docker compose logs -f

# 특정 서비스 로그
docker compose logs -f nodered
```

### 6.2 스택 중지

```bash
# 중지 (컨테이너 유지)
docker compose stop

# 중지 및 제거
docker compose down

# 볼륨까지 제거 (주의!)
docker compose down -v
```

### 6.3 상태 확인

```bash
# 컨테이너 상태
docker compose ps

# 리소스 사용량
docker stats

# 디스크 사용량
docker system df
```

### 6.4 업데이트

```bash
# 이미지 업데이트
docker compose pull

# 재시작
docker compose up -d

# 사용하지 않는 이미지 정리
docker image prune -a
```

---

## 7. 문제 해결

### 7.1 컨테이너 시작 실패

```bash
# 로그 확인
docker compose logs [service_name]

# 컨테이너 상세 정보
docker inspect ming-[service_name]

# 네트워크 확인
docker network ls
docker network inspect ming_ming-network
```

### 7.2 포트 충돌

```bash
# 사용 중인 포트 확인
sudo netstat -tlnp | grep -E "1883|8086|1880|3000"

# docker-compose.yml에서 포트 변경
ports:
  - "18830:1880"  # 호스트포트:컨테이너포트
```

### 7.3 권한 문제

```bash
# 데이터 디렉토리 권한 설정
sudo chown -R 1000:1000 ./nodered/data
sudo chown -R 472:472 ./grafana/data
sudo chown -R 1883:1883 ./mosquitto/data ./mosquitto/log
```

---

## 8. 백업 및 복원

### 8.1 백업 스크립트

```bash
#!/bin/bash
# scripts/backup.sh

BACKUP_DIR="/home/pi/backups/ming-stack"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 스택 중지
docker compose stop

# 데이터 백업
tar -czvf $BACKUP_DIR/ming-backup-$DATE.tar.gz \
    ./mosquitto/data \
    ./influxdb/data \
    ./nodered/data \
    ./grafana/data

# 스택 시작
docker compose start

echo "Backup completed: $BACKUP_DIR/ming-backup-$DATE.tar.gz"
```

### 8.2 복원

```bash
#!/bin/bash
# scripts/restore.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: ./restore.sh <backup_file>"
    exit 1
fi

# 스택 중지
docker compose down

# 복원
tar -xzvf $BACKUP_FILE

# 스택 시작
docker compose up -d

echo "Restore completed"
```

---

## 9. 모니터링

### 9.1 시스템 리소스 모니터링

```bash
# htop 설치
sudo apt install -y htop

# 실시간 모니터링
htop
```

### 9.2 Docker 리소스 모니터링

```bash
# 실시간 리소스 사용량
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# 컨테이너별 로그 크기
docker system df -v
```

---

## 참고 자료

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)
