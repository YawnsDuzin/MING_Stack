# 라즈베리파이 5 최적화 가이드

> Raspberry Pi 5 환경에서 MING Stack 성능 최적화

---

## 1. 라즈베리파이 5 사양

### 1.1 하드웨어 스펙

| 항목 | Raspberry Pi 5 | Raspberry Pi 4 |
|------|----------------|----------------|
| CPU | Cortex-A76 2.4GHz (4코어) | Cortex-A72 1.8GHz (4코어) |
| RAM | 4GB / 8GB LPDDR4X | 2GB / 4GB / 8GB LPDDR4 |
| GPIO | 40핀 | 40핀 |
| USB | 2x USB 3.0, 2x USB 2.0 | 2x USB 3.0, 2x USB 2.0 |
| 네트워크 | Gigabit Ethernet | Gigabit Ethernet |
| PCIe | PCIe 2.0 x1 (M.2 확장 가능) | 없음 |
| 전원 | USB-C 5V/5A (27W) | USB-C 5V/3A (15W) |

### 1.2 MING Stack 권장 사양

| 구성 | 최소 | 권장 |
|------|------|------|
| RAM | 4GB | 8GB |
| 저장공간 | 32GB SD | 64GB+ NVMe SSD |
| 전원 | 5V/3A | 5V/5A 공식 어댑터 |

---

## 2. 초기 시스템 설정

### 2.1 OS 설치

```bash
# Raspberry Pi Imager 사용
# OS: Raspberry Pi OS Lite (64-bit) 권장
# Bookworm 이상 버전 사용
```

### 2.2 시스템 업데이트

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl wget htop iotop
```

### 2.3 Docker 설치

```bash
# Docker 설치 스크립트
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER

# 재로그인 후 확인
docker --version
docker compose version
```

---

## 3. 메모리 최적화

### 3.1 GPU 메모리 할당

GUI를 사용하지 않으므로 GPU 메모리를 최소화:

```bash
sudo raspi-config
# Performance Options → GPU Memory → 16MB
```

또는 직접 설정:
```bash
echo "gpu_mem=16" | sudo tee -a /boot/firmware/config.txt
sudo reboot
```

### 3.2 Swap 설정

```bash
# 기본 Swap 비활성화
sudo dphys-swapfile swapoff
sudo systemctl disable dphys-swapfile

# Zram 사용 (더 효율적인 압축 스왑)
sudo apt install -y zram-tools
echo "ALGO=zstd" | sudo tee -a /etc/default/zramswap
echo "PERCENT=50" | sudo tee -a /etc/default/zramswap
sudo systemctl restart zramswap
```

### 3.3 MING Stack 메모리 설정

`.env` 파일에서 Pi 5 8GB 기준:

```bash
# Pi 5 8GB 권장 설정
INFLUXDB_MEMORY_LIMIT=1G
NODERED_MEMORY_LIMIT=512M
GRAFANA_MEMORY_LIMIT=256M

# Pi 4 4GB 또는 Pi 5 4GB 설정
# INFLUXDB_MEMORY_LIMIT=512M
# NODERED_MEMORY_LIMIT=384M
# GRAFANA_MEMORY_LIMIT=192M
```

---

## 4. 저장공간 최적화

### 4.1 NVMe SSD 사용 (권장)

Pi 5는 PCIe를 통해 NVMe SSD를 지원합니다:

```bash
# NVMe HAT 또는 어댑터 설치 후
lsblk  # NVMe 장치 확인 (nvme0n1)

# 파티션 및 포맷
sudo fdisk /dev/nvme0n1
sudo mkfs.ext4 /dev/nvme0n1p1

# 마운트
sudo mkdir /mnt/nvme
sudo mount /dev/nvme0n1p1 /mnt/nvme

# fstab에 추가
echo "/dev/nvme0n1p1 /mnt/nvme ext4 defaults,noatime 0 2" | sudo tee -a /etc/fstab
```

### 4.2 Docker 데이터 이동 (NVMe로)

```bash
# Docker 중지
sudo systemctl stop docker

# Docker 데이터 이동
sudo mv /var/lib/docker /mnt/nvme/docker
sudo ln -s /mnt/nvme/docker /var/lib/docker

# Docker 재시작
sudo systemctl start docker
```

### 4.3 MING Stack 볼륨 위치

```bash
# docker-compose.yml에서 볼륨을 NVMe로 변경
# 또는 프로젝트를 NVMe에 클론
cd /mnt/nvme
git clone <your-repo> MING_Stack
```

### 4.4 SD 카드 수명 연장

SD 카드 사용 시:

```bash
# noatime 옵션으로 마운트 (fstab 수정)
# /dev/mmcblk0p2 / ext4 defaults,noatime 0 1

# 로그 최소화
sudo nano /etc/systemd/journald.conf
# Storage=volatile
# RuntimeMaxUse=50M

sudo systemctl restart systemd-journald
```

---

## 5. CPU 및 전력 최적화

### 5.1 CPU 거버너 설정

```bash
# 현재 거버너 확인
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

# performance 모드 (최고 성능)
echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# 부팅 시 자동 적용
echo 'GOVERNOR="performance"' | sudo tee /etc/default/cpufrequtils
sudo apt install -y cpufrequtils
```

### 5.2 전원 관리

공식 27W 어댑터 사용 권장. USB 장치 연결 시 전력 부족 주의.

```bash
# USB 전력 제한 해제 (주의: 과열 위험)
# /boot/firmware/config.txt
usb_max_current_enable=1
```

### 5.3 온도 모니터링

```bash
# CPU 온도 확인
vcgencmd measure_temp

# 모니터링 스크립트
watch -n 1 vcgencmd measure_temp

# 쿨링 필수 (액티브 쿨러 권장)
# 85°C 이상 시 스로틀링 발생
```

---

## 6. 네트워크 최적화

### 6.1 고정 IP 설정

```bash
sudo nano /etc/dhcpcd.conf
```

```
interface eth0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=8.8.8.8 1.1.1.1
```

### 6.2 TCP 튜닝

```bash
sudo nano /etc/sysctl.conf
```

```bash
# TCP 버퍼 크기 증가
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216

# 연결 수 증가
net.core.somaxconn = 65535
net.core.netdev_max_backlog = 65535
```

```bash
sudo sysctl -p
```

### 6.3 MQTT 브로커 연결 최적화

Mosquitto 설정에서:

```conf
# 최대 연결 수 (Pi 5 기준)
max_connections 1000

# Keep-alive 설정
max_keepalive 120

# QoS 메시지 최적화
max_inflight_messages 20
```

---

## 7. Docker 최적화

### 7.1 Docker 로깅 제한

```bash
sudo nano /etc/docker/daemon.json
```

```json
{
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "10m",
        "max-file": "3"
    },
    "storage-driver": "overlay2"
}
```

```bash
sudo systemctl restart docker
```

### 7.2 컨테이너 리소스 제한

docker-compose.yml에서 이미 설정됨:

```yaml
deploy:
  resources:
    limits:
      memory: 1G
    reservations:
      memory: 256M
```

### 7.3 이미지 정리

```bash
# 사용하지 않는 이미지 정리
docker image prune -a

# 볼륨 정리 (주의: 데이터 삭제됨)
docker volume prune

# 전체 정리
docker system prune -a
```

---

## 8. 서비스별 최적화

### 8.1 InfluxDB

```bash
# Pi 5 8GB 기준 .env 설정
INFLUXDB_MEMORY_LIMIT=1G
INFLUXDB_RETENTION=7d  # 데이터 보존 기간
```

쿼리 최적화:
- 집계 쿼리에 `aggregateWindow()` 사용
- 시간 범위 최소화
- 불필요한 필드 제외

### 8.2 Node-RED

```bash
NODERED_MEMORY_LIMIT=512M
```

플로우 최적화:
- 디버그 노드 비활성화 (프로덕션)
- 불필요한 context 저장 최소화
- 배치 처리 활용

### 8.3 Grafana

```bash
GRAFANA_MEMORY_LIMIT=256M
```

대시보드 최적화:
- 자동 새로고침 간격: 5초 이상
- 패널 수: 화면당 10개 이하 권장
- 쿼리 캐싱 활용

### 8.4 Mosquitto

메모리 제한은 Docker에서 별도 설정 없음 (경량).
연결 수 및 메시지 크기로 제한:

```conf
max_connections 1000
message_size_limit 1048576
```

---

## 9. 모니터링 설정

### 9.1 시스템 모니터링 스크립트

```bash
#!/bin/bash
# /usr/local/bin/system-monitor.sh

while true; do
    echo "=== $(date) ==="
    echo "CPU Temp: $(vcgencmd measure_temp)"
    echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')%"
    echo "Memory: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
    echo "Disk: $(df -h / | awk 'NR==2 {print $3 "/" $2}')"
    echo ""
    sleep 60
done
```

### 9.2 Docker 상태 확인

```bash
# 컨테이너 리소스 사용량
docker stats --no-stream

# 특정 컨테이너 로그
docker logs -f ming-nodered
```

---

## 10. 자동 시작 설정

### 10.1 systemd 서비스

```bash
sudo nano /etc/systemd/system/ming-stack.service
```

```ini
[Unit]
Description=MING Stack IoT Platform
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/pi/MING_Stack
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
User=pi

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable ming-stack
sudo systemctl start ming-stack
```

---

## 11. 문제 해결

### 11.1 메모리 부족

```bash
# 메모리 사용량 확인
free -h
docker stats

# 해결: 메모리 제한 축소
INFLUXDB_MEMORY_LIMIT=512M
NODERED_MEMORY_LIMIT=384M
GRAFANA_MEMORY_LIMIT=192M
```

### 11.2 CPU 과열

```bash
# 온도 확인
vcgencmd measure_temp

# 해결:
# 1. 액티브 쿨러 설치
# 2. CPU 거버너를 powersave로 변경
# 3. 케이스 환기 개선
```

### 11.3 SD 카드 오류

```bash
# 파일시스템 체크
sudo fsck -y /dev/mmcblk0p2

# 해결: NVMe SSD 사용 권장
```

### 11.4 Docker 시작 실패

```bash
# Docker 상태 확인
sudo systemctl status docker

# 로그 확인
sudo journalctl -u docker

# Docker 재시작
sudo systemctl restart docker
```

---

## 12. 성능 벤치마크

### 12.1 Pi 5 8GB 예상 성능

| 항목 | 수치 |
|------|------|
| MQTT 메시지 처리 | ~10,000 msg/s |
| InfluxDB 쓰기 | ~5,000 points/s |
| 동시 센서 연결 | 100+ |
| 대시보드 응답 | <1초 |

### 12.2 부하 테스트

```bash
# MQTT 부하 테스트
mosquitto_pub -h localhost -t test -m "test" -u mqtt_user -P mqtt_pass -r -q 0 -c 1000

# InfluxDB 쓰기 테스트
# Node-RED에서 inject 노드로 대량 데이터 생성
```

---

## 참고 자료

- [Raspberry Pi 5 Documentation](https://www.raspberrypi.com/documentation/)
- [Docker on Raspberry Pi](https://docs.docker.com/engine/install/debian/)
- [InfluxDB Performance](https://docs.influxdata.com/influxdb/v2/reference/internals/)
