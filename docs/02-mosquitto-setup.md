# Mosquitto MQTT 브로커 설정 가이드

> Eclipse Mosquitto 상세 설정 및 보안 구성

---

## 1. Mosquitto 개요

### 1.1 Eclipse Mosquitto란?

Eclipse Mosquitto는 경량 오픈소스 MQTT 메시지 브로커로, IoT 환경에서 널리 사용됩니다.

### 1.2 주요 특징

| 특징 | 설명 |
|------|------|
| 경량화 | 라즈베리파이에서도 원활하게 동작 |
| MQTT 3.1.1/5.0 | 최신 MQTT 프로토콜 지원 |
| TLS/SSL | 암호화 통신 지원 |
| WebSocket | 웹 브라우저 연결 지원 |
| Bridge | 브로커 간 연결 지원 |

---

## 2. 설정 파일 구조

```
mosquitto/
├── config/
│   ├── mosquitto.conf    # 메인 설정 파일
│   ├── passwd            # 사용자 비밀번호
│   └── acl               # 접근 제어 목록
├── data/                 # 영구 데이터
└── log/                  # 로그 파일
```

---

## 3. 기본 설정

### 3.1 mosquitto.conf 주요 설정

```conf
# 기본 리스너
listener 1883
protocol mqtt

# WebSocket 리스너
listener 9001
protocol websockets

# 인증 설정
allow_anonymous false
password_file /mosquitto/config/passwd
acl_file /mosquitto/config/acl

# 영속성 설정
persistence true
persistence_location /mosquitto/data/

# 로깅
log_dest file /mosquitto/log/mosquitto.log
log_dest stdout
```

### 3.2 성능 최적화 설정

```conf
# 최대 연결 수 (라즈베리파이 기준)
max_connections 1000

# 메시지 크기 제한 (1MB)
message_size_limit 1048576

# 큐 설정
max_queued_messages 1000
max_queued_bytes 0

# Keep-alive
max_keepalive 120
```

---

## 4. 사용자 인증 설정

### 4.1 비밀번호 파일 생성

```bash
# 첫 사용자 생성 (-c: 새 파일 생성)
docker exec ming-mosquitto mosquitto_passwd -c /mosquitto/config/passwd mqtt_user

# 추가 사용자 생성
docker exec ming-mosquitto mosquitto_passwd -b /mosquitto/config/passwd nodered mqtt_pass
docker exec ming-mosquitto mosquitto_passwd -b /mosquitto/config/passwd sensor_device mqtt_pass
```

### 4.2 비밀번호 변경

```bash
docker exec ming-mosquitto mosquitto_passwd -b /mosquitto/config/passwd mqtt_user new_password
```

### 4.3 사용자 삭제

```bash
docker exec ming-mosquitto mosquitto_passwd -D /mosquitto/config/passwd old_user
```

---

## 5. ACL (접근 제어) 설정

### 5.1 ACL 파일 형식

```
# 사용자별 권한 설정
user <username>
topic [read|write|readwrite|deny] <topic_pattern>

# 패턴 사용
# %c - 클라이언트 ID
# %u - 사용자명
# + - 단일 레벨 와일드카드
# # - 다중 레벨 와일드카드
```

### 5.2 ACL 설정 예시

```
# 관리자 - 모든 권한
user admin
topic readwrite #

# Node-RED - 전체 읽기/쓰기
user nodered
topic readwrite #

# 센서 디바이스 - 제한된 권한
user sensor_device
topic write factory/+/+/data
topic write factory/+/+/status
topic read factory/+/+/control

# 모니터링 시스템 - 읽기만
user monitoring
topic read #

# 공통 패턴 (인증된 사용자)
pattern read $SYS/#
pattern readwrite factory/%u/#
```

---

## 6. TLS/SSL 설정 (선택사항)

### 6.1 인증서 생성

```bash
# CA 키 및 인증서 생성
openssl genrsa -out ca.key 2048
openssl req -new -x509 -days 365 -key ca.key -out ca.crt

# 서버 키 및 인증서 생성
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr
openssl x509 -req -days 365 -in server.csr -CA ca.crt -CAkey ca.key -set_serial 01 -out server.crt
```

### 6.2 TLS 설정

```conf
# mosquitto.conf에 추가
listener 8883
protocol mqtt
cafile /mosquitto/config/certs/ca.crt
certfile /mosquitto/config/certs/server.crt
keyfile /mosquitto/config/certs/server.key
require_certificate false
```

---

## 7. 테스트

### 7.1 연결 테스트

```bash
# 구독 테스트
mosquitto_sub -h localhost -p 1883 -u mqtt_user -P mqtt_pass -t "test/#" -v

# 발행 테스트 (다른 터미널)
mosquitto_pub -h localhost -p 1883 -u mqtt_user -P mqtt_pass -t "test/hello" -m "Hello MQTT!"
```

### 7.2 Docker 내부에서 테스트

```bash
docker exec ming-mosquitto mosquitto_sub -t "test/#" -u mqtt_user -P mqtt_pass -C 1
docker exec ming-mosquitto mosquitto_pub -t "test/hello" -u mqtt_user -P mqtt_pass -m "test"
```

---

## 8. 모니터링

### 8.1 시스템 토픽

```bash
# 브로커 상태 모니터링
mosquitto_sub -h localhost -u mqtt_user -P mqtt_pass -t '$SYS/#' -v
```

주요 시스템 토픽:
- `$SYS/broker/clients/connected` - 연결된 클라이언트 수
- `$SYS/broker/messages/received` - 수신 메시지 수
- `$SYS/broker/messages/sent` - 발신 메시지 수
- `$SYS/broker/uptime` - 가동 시간

### 8.2 로그 확인

```bash
# Docker 로그
docker logs -f ming-mosquitto

# 파일 로그
tail -f mosquitto/log/mosquitto.log
```

---

## 9. 문제 해결

### 9.1 연결 거부

```
Connection refused: not authorised
```

해결: passwd 파일 확인, 사용자명/비밀번호 확인

### 9.2 ACL 권한 오류

```
Client not authorized to publish
```

해결: acl 파일에서 해당 사용자의 권한 확인

### 9.3 컨테이너 시작 실패

```bash
# 설정 파일 검증
docker run --rm -v $(pwd)/mosquitto/config:/mosquitto/config \
    eclipse-mosquitto:2.0 mosquitto -c /mosquitto/config/mosquitto.conf -t
```

---

## 참고 자료

- [Mosquitto Documentation](https://mosquitto.org/documentation/)
- [MQTT 5.0 Specification](https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html)
