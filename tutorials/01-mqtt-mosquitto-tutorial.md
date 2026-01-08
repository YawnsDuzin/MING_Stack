# MQTT와 Mosquitto 완전 정복 튜토리얼

> 처음 시작하는 분들을 위한 MQTT 기초부터 실전까지

---

## 📚 목차

1. [MQTT란 무엇인가?](#1-mqtt란-무엇인가)
2. [MQTT 기본 개념](#2-mqtt-기본-개념)
3. [Mosquitto 시작하기](#3-mosquitto-시작하기)
4. [실습: 첫 번째 메시지 보내기](#4-실습-첫-번째-메시지-보내기)
5. [토픽 설계하기](#5-토픽-설계하기)
6. [QoS 이해하기](#6-qos-이해하기)
7. [보안 설정](#7-보안-설정)
8. [실전 예제](#8-실전-예제)
9. [문제 해결](#9-문제-해결)

---

## 1. MQTT란 무엇인가?

### 1.1 쉬운 설명

**MQTT**는 기기들이 서로 대화하는 방법입니다.

```
일상 비유:
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   📱 카카오톡 그룹채팅 = MQTT 통신                        │
│                                                         │
│   - 그룹방 이름 = 토픽(Topic)                            │
│   - 메시지 보내기 = 발행(Publish)                        │
│   - 그룹방 들어가기 = 구독(Subscribe)                    │
│   - 카카오 서버 = 브로커(Mosquitto)                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 1.2 왜 MQTT를 사용할까?

| 특징 | HTTP | MQTT |
|------|------|------|
| 통신 방식 | 요청-응답 | 발행-구독 |
| 연결 | 매번 새로 | 한 번 연결 유지 |
| 데이터 크기 | 큼 | 매우 작음 (2바이트~) |
| 적합한 용도 | 웹사이트 | IoT, 센서 |

### 1.3 MQTT가 사용되는 곳

- 🏭 공장 센서 데이터 수집
- 🏠 스마트홈 (조명, 온도 조절)
- 🚗 차량 위치 추적
- 📊 실시간 모니터링

---

## 2. MQTT 기본 개념

### 2.1 발행/구독 모델

```
    발행자(Publisher)              구독자(Subscriber)
         │                              │
         │  "온도: 25도"                │
         ▼                              │
    ┌─────────────────────────────────────────┐
    │           Mosquitto 브로커              │
    │                                         │
    │   토픽: factory/sensor/temperature      │
    │   메시지: 25                            │
    │                                         │
    └─────────────────────────────────────────┘
                        │
                        │  "온도: 25도"
                        ▼
                   구독자에게 전달
```

### 2.2 핵심 용어

| 용어 | 영어 | 설명 | 예시 |
|------|------|------|------|
| 브로커 | Broker | 메시지를 전달하는 서버 | Mosquitto |
| 토픽 | Topic | 메시지의 주제/경로 | `factory/line1/temp` |
| 발행 | Publish | 메시지 보내기 | 센서가 온도 전송 |
| 구독 | Subscribe | 메시지 받기 신청 | 모니터가 온도 수신 |
| 페이로드 | Payload | 실제 데이터 내용 | `{"temp": 25}` |

### 2.3 토픽의 구조

토픽은 `/`로 계층을 구분합니다:

```
factory/line1/machine1/temperature
   │      │      │         │
   │      │      │         └── 데이터 종류
   │      │      └──────────── 장비
   │      └─────────────────── 라인
   └────────────────────────── 공장
```

### 2.4 와일드카드

| 기호 | 이름 | 의미 | 예시 |
|------|------|------|------|
| `+` | 단일 레벨 | 한 단계만 대체 | `factory/+/temperature` |
| `#` | 다중 레벨 | 모든 하위 대체 | `factory/#` |

```
예시:
- factory/+/temperature
  → factory/line1/temperature ✓
  → factory/line2/temperature ✓
  → factory/line1/machine1/temperature ✗

- factory/#
  → factory/line1 ✓
  → factory/line1/temperature ✓
  → factory/line1/machine1/temperature ✓
```

---

## 3. Mosquitto 시작하기

### 3.1 MING Stack에서 Mosquitto 확인

```bash
# 컨테이너 상태 확인
docker ps | grep mosquitto

# 로그 확인
docker logs ming-mosquitto

# 예상 출력:
# mosquitto version 2.0.x
# Config loaded from /mosquitto/config/mosquitto.conf
# Starting in local only mode.
```

### 3.2 Mosquitto 기본 정보

| 항목 | 값 |
|------|-----|
| 호스트 | `localhost` 또는 라즈베리파이 IP |
| MQTT 포트 | `1883` |
| WebSocket 포트 | `9001` |
| 사용자 | `mqtt_user` (기본) |
| 비밀번호 | `mqtt_pass` (기본) |

### 3.3 mosquitto-clients 설치

테스트를 위해 클라이언트 도구를 설치합니다:

```bash
# 라즈베리파이/우분투
sudo apt update
sudo apt install -y mosquitto-clients

# 설치 확인
mosquitto_pub --help
mosquitto_sub --help
```

---

## 4. 실습: 첫 번째 메시지 보내기

### 4.1 터미널 2개 열기

**터미널 1: 구독자 (메시지 받기)**
```bash
# test/hello 토픽 구독
mosquitto_sub -h localhost -p 1883 \
  -u mqtt_user -P mqtt_pass \
  -t "test/hello" -v

# -h: 호스트
# -p: 포트
# -u: 사용자
# -P: 비밀번호
# -t: 토픽
# -v: 토픽 이름도 함께 출력
```

**터미널 2: 발행자 (메시지 보내기)**
```bash
# test/hello 토픽에 메시지 발행
mosquitto_pub -h localhost -p 1883 \
  -u mqtt_user -P mqtt_pass \
  -t "test/hello" -m "안녕하세요!"
```

### 4.2 결과 확인

터미널 1에서 다음이 표시됩니다:
```
test/hello 안녕하세요!
```

🎉 **축하합니다!** 첫 MQTT 메시지를 보냈습니다!

### 4.3 JSON 메시지 보내기

실제로는 JSON 형식을 많이 사용합니다:

```bash
# JSON 메시지 발행
mosquitto_pub -h localhost -p 1883 \
  -u mqtt_user -P mqtt_pass \
  -t "factory/sensor/data" \
  -m '{"temperature": 25.5, "humidity": 60}'
```

### 4.4 와일드카드 구독 실습

```bash
# 터미널 1: 모든 factory 토픽 구독
mosquitto_sub -h localhost -p 1883 \
  -u mqtt_user -P mqtt_pass \
  -t "factory/#" -v

# 터미널 2: 여러 토픽에 발행
mosquitto_pub -h localhost -p 1883 \
  -u mqtt_user -P mqtt_pass \
  -t "factory/line1/temperature" -m "25"

mosquitto_pub -h localhost -p 1883 \
  -u mqtt_user -P mqtt_pass \
  -t "factory/line2/humidity" -m "60"

mosquitto_pub -h localhost -p 1883 \
  -u mqtt_user -P mqtt_pass \
  -t "factory/line1/machine1/status" -m "running"
```

---

## 5. 토픽 설계하기

### 5.1 좋은 토픽 구조

```
권장 구조:
{회사}/{사이트}/{영역}/{장비}/{데이터타입}

예시:
mycompany/seoul/factory1/line1/temperature
mycompany/seoul/factory1/line1/humidity
mycompany/seoul/factory1/line1/status
```

### 5.2 산업용 토픽 예시

```
┌─────────────────────────────────────────────────────────┐
│ 데이터 수집 (센서 → 서버)                                │
├─────────────────────────────────────────────────────────┤
│ factory/line1/sensor/temperature                        │
│ factory/line1/sensor/humidity                           │
│ factory/line1/sensor/pressure                           │
│ factory/line1/plc/production_count                      │
│ factory/line1/plc/status                                │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 제어 명령 (서버 → 장비)                                  │
├─────────────────────────────────────────────────────────┤
│ factory/line1/control/motor/start                       │
│ factory/line1/control/motor/stop                        │
│ factory/line1/control/conveyor/speed                    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 알람/이벤트                                              │
├─────────────────────────────────────────────────────────┤
│ factory/line1/alarm/temperature_high                    │
│ factory/line1/alarm/motor_fault                         │
│ factory/line1/event/production_complete                 │
└─────────────────────────────────────────────────────────┘
```

### 5.3 피해야 할 토픽 구조

```
❌ 나쁜 예:
- Sensor1Data          (구조가 없음)
- factory line1 temp   (공백 사용)
- /factory/line1/      (앞뒤 슬래시)
- FACTORY/LINE1/TEMP   (대문자 일관성 없음)

✓ 좋은 예:
- factory/line1/sensor/temperature
- factory/line1/sensor/humidity
```

---

## 6. QoS 이해하기

### 6.1 QoS란?

**QoS (Quality of Service)** = 메시지 전달 보장 수준

### 6.2 QoS 레벨 비교

| QoS | 이름 | 설명 | 속도 | 사용 사례 |
|-----|------|------|------|-----------|
| 0 | At most once | 최대 1번 (안 갈 수도) | 가장 빠름 | 센서 데이터 |
| 1 | At least once | 최소 1번 (중복 가능) | 보통 | 일반적인 용도 |
| 2 | Exactly once | 정확히 1번 | 가장 느림 | 결제, 중요 명령 |

### 6.3 QoS 시각적 이해

```
QoS 0: 발행자 ──메시지──> 브로커 (확인 없음)
       "보냈으니 끝!"

QoS 1: 발행자 ──메시지──> 브로커
       발행자 <──확인─── 브로커
       "받았다고 확인!"

QoS 2: 발행자 ──메시지──> 브로커
       발행자 <──받음─── 브로커
       발행자 ──해제──> 브로커
       발행자 <──완료─── 브로커
       "4단계 확인!"
```

### 6.4 QoS 사용 예시

```bash
# QoS 0 (기본값)
mosquitto_pub -h localhost -p 1883 \
  -u mqtt_user -P mqtt_pass \
  -t "sensor/temp" -m "25" -q 0

# QoS 1
mosquitto_pub -h localhost -p 1883 \
  -u mqtt_user -P mqtt_pass \
  -t "control/motor" -m "start" -q 1

# QoS 2
mosquitto_pub -h localhost -p 1883 \
  -u mqtt_user -P mqtt_pass \
  -t "payment/confirm" -m "approved" -q 2
```

---

## 7. 보안 설정

### 7.1 사용자 추가

```bash
# 컨테이너 내부에서 사용자 추가
docker exec ming-mosquitto \
  mosquitto_passwd -b /mosquitto/config/passwd newuser newpassword

# Mosquitto 재시작
docker restart ming-mosquitto
```

### 7.2 ACL (접근 제어 목록)

`mosquitto/config/acl.conf` 파일 생성:

```conf
# mqtt_user는 모든 토픽 접근 가능
user mqtt_user
topic readwrite #

# sensor_device는 센서 토픽만 발행 가능
user sensor_device
topic write factory/+/sensor/#
topic read factory/+/control/#

# monitor는 읽기만 가능
user monitor
topic read #
```

### 7.3 mosquitto.conf에 ACL 적용

```conf
# ACL 파일 경로
acl_file /mosquitto/config/acl.conf

# 익명 접속 불가
allow_anonymous false

# 비밀번호 파일
password_file /mosquitto/config/passwd
```

---

## 8. 실전 예제

### 8.1 Python으로 MQTT 사용

```python
# pip install paho-mqtt

import paho.mqtt.client as mqtt
import json
import time

# 콜백 함수
def on_connect(client, userdata, flags, rc):
    print(f"연결됨! 결과 코드: {rc}")
    # 연결 시 토픽 구독
    client.subscribe("factory/#")

def on_message(client, userdata, msg):
    print(f"토픽: {msg.topic}")
    print(f"메시지: {msg.payload.decode()}")

# 클라이언트 생성
client = mqtt.Client()
client.username_pw_set("mqtt_user", "mqtt_pass")
client.on_connect = on_connect
client.on_message = on_message

# 브로커 연결
client.connect("localhost", 1883, 60)

# 백그라운드에서 메시지 수신
client.loop_start()

# 메시지 발행
while True:
    data = {
        "temperature": 25.5,
        "humidity": 60,
        "timestamp": time.time()
    }
    client.publish("factory/line1/sensor/data", json.dumps(data))
    print(f"발행: {data}")
    time.sleep(5)
```

### 8.2 Node.js로 MQTT 사용

```javascript
// npm install mqtt

const mqtt = require('mqtt');

// 브로커 연결
const client = mqtt.connect('mqtt://localhost:1883', {
    username: 'mqtt_user',
    password: 'mqtt_pass'
});

// 연결 이벤트
client.on('connect', () => {
    console.log('연결됨!');
    client.subscribe('factory/#');
});

// 메시지 수신 이벤트
client.on('message', (topic, message) => {
    console.log(`토픽: ${topic}`);
    console.log(`메시지: ${message.toString()}`);
});

// 메시지 발행
setInterval(() => {
    const data = {
        temperature: 25.5 + Math.random(),
        humidity: 60 + Math.random() * 10
    };
    client.publish('factory/line1/sensor/data', JSON.stringify(data));
    console.log('발행:', data);
}, 5000);
```

### 8.3 Retained 메시지

마지막 메시지를 저장해서 새 구독자에게 즉시 전달:

```bash
# Retained 메시지 발행 (-r 옵션)
mosquitto_pub -h localhost -p 1883 \
  -u mqtt_user -P mqtt_pass \
  -t "factory/line1/status" \
  -m "running" -r

# 나중에 구독해도 마지막 메시지를 즉시 받음
mosquitto_sub -h localhost -p 1883 \
  -u mqtt_user -P mqtt_pass \
  -t "factory/line1/status"
# 출력: running (즉시!)
```

---

## 9. 문제 해결

### 9.1 연결 안 됨

```bash
# 1. Mosquitto 컨테이너 상태 확인
docker ps | grep mosquitto

# 2. 포트 열려 있는지 확인
netstat -tlnp | grep 1883

# 3. 로그 확인
docker logs ming-mosquitto

# 4. 방화벽 확인
sudo ufw status
sudo ufw allow 1883/tcp
```

### 9.2 인증 실패

```bash
# 에러: Connection refused: not authorised

# 해결:
# 1. 사용자/비밀번호 확인
# 2. passwd 파일 확인
docker exec ming-mosquitto cat /mosquitto/config/passwd

# 3. mosquitto.conf 확인
docker exec ming-mosquitto cat /mosquitto/config/mosquitto.conf
```

### 9.3 메시지가 안 옴

```bash
# 1. 토픽 이름 정확히 확인 (대소문자 구분!)
# factory/Line1/temp ≠ factory/line1/temp

# 2. 와일드카드로 모든 메시지 확인
mosquitto_sub -h localhost -p 1883 \
  -u mqtt_user -P mqtt_pass \
  -t "#" -v

# 3. QoS 레벨 확인
```

### 9.4 유용한 디버깅 명령

```bash
# 모든 시스템 토픽 보기 (브로커 상태)
mosquitto_sub -h localhost -p 1883 \
  -u mqtt_user -P mqtt_pass \
  -t "\$SYS/#" -v

# 연결된 클라이언트 수
mosquitto_sub -h localhost -p 1883 \
  -u mqtt_user -P mqtt_pass \
  -t "\$SYS/broker/clients/connected"
```

---

## 📝 핵심 요약

| 개념 | 설명 |
|------|------|
| MQTT | IoT 기기 간 메시지 전달 프로토콜 |
| Mosquitto | MQTT 브로커 (서버) |
| 토픽 | 메시지의 주소 (예: factory/line1/temp) |
| 발행 | 메시지 보내기 (Publish) |
| 구독 | 메시지 받기 신청 (Subscribe) |
| QoS | 전달 보장 수준 (0, 1, 2) |
| Retained | 마지막 메시지 저장 |

---

## 다음 단계

- [InfluxDB 튜토리얼](./02-influxdb-tutorial.md) - 데이터 저장
- [Node-RED 튜토리얼](./03-nodered-tutorial.md) - 데이터 처리
- [Grafana 튜토리얼](./04-grafana-tutorial.md) - 시각화
