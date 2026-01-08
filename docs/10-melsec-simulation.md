# Mitsubishi MELSEC MC 프로토콜 가이드

> MELSEC PLC MC 프로토콜 시뮬레이터 구성 및 Node-RED 연동

---

## 1. MC 프로토콜 개요

### 1.1 MC 프로토콜이란?

MC 프로토콜(MELSEC Communication Protocol)은 미쓰비시 전기(Mitsubishi Electric)의 MELSEC PLC 시리즈와 통신하기 위한 표준 프로토콜입니다.

| 특징 | 설명 |
|------|------|
| 제조사 | Mitsubishi Electric |
| 지원 PLC | MELSEC-Q, iQ-R, iQ-F, L 시리즈 등 |
| 통신 방식 | TCP/IP (이더넷) |
| 프레임 타입 | 3E (바이너리), 4E (ASCII) |

### 1.2 지원 PLC 시리즈

| 시리즈 | 설명 |
|--------|------|
| MELSEC-Q | 고성능 범용 PLC |
| MELSEC iQ-R | 차세대 고성능 PLC |
| MELSEC iQ-F | 소형 고성능 PLC |
| MELSEC-L | 컴팩트 PLC |
| MELSEC-F | 마이크로 PLC |

### 1.3 프레임 타입

| 프레임 | 형식 | 특징 |
|--------|------|------|
| 3E | Binary | 고속, 효율적, 실시간 처리에 적합 |
| 4E | ASCII | 디버깅 용이, 가독성 좋음 |
| 1E | Binary (구형) | 구형 장비 호환 |

---

## 2. 디바이스 메모리 영역

### 2.1 주요 디바이스

| 디바이스 | 코드 | 설명 | 주소 범위 |
|----------|------|------|-----------|
| D | 0xA8 | 데이터 레지스터 | D0 ~ D8191 |
| M | 0x90 | 내부 릴레이 | M0 ~ M8191 |
| X | 0x9C | 입력 (Input) | X0 ~ X1FF |
| Y | 0x9D | 출력 (Output) | Y0 ~ Y1FF |
| W | 0xB4 | 링크 레지스터 | W0 ~ W1FF |
| R | 0xAF | 파일 레지스터 | R0 ~ R32767 |
| L | 0x92 | 래치 릴레이 | L0 ~ L8191 |
| B | 0xA0 | 링크 릴레이 | B0 ~ B7FF |
| TN | 0xC2 | 타이머 현재값 | T0 ~ T2047 |
| CN | 0xC5 | 카운터 현재값 | C0 ~ C1023 |

### 2.2 데이터 타입

| 타입 | 크기 | 설명 |
|------|------|------|
| BIT | 1 bit | 비트 디바이스 (M, X, Y, L, B) |
| WORD | 16 bit | 워드 디바이스 (D, W, R) |
| DWORD | 32 bit | 더블워드 (D0-D1 조합) |

---

## 3. 시뮬레이터 구성

### 3.1 시뮬레이터 시작

```bash
# 시뮬레이터 프로파일로 시작
docker compose --profile simulators up -d

# MELSEC 시뮬레이터만 시작
docker compose up -d melsec-simulator
```

### 3.2 접속 정보

```
Host: raspberrypi (또는 IP 주소)
Port: 5000
Protocol: MC Protocol 3E Frame (Binary)
```

### 3.3 시뮬레이션 데이터 맵

```
디바이스          설명                  스케일
─────────────────────────────────────────────────
D0              온도                  x10 (250 = 25.0°C)
D1              습도                  x10 (600 = 60.0%)
D2              압력                  x100 (100 = 1.00 bar)
D10             모터 속도             RPM (0~3000)
D20-D21         생산 카운트           32비트 (D20:하위, D21:상위)
D100            상태 워드             비트별 상태

M0              운전 중 (R/W)         1=운전, 0=정지
M1              알람 (R)              1=알람 발생
M2              안전 상태 (R)         1=정상, 0=이상
M10             모터 시작 명령 (W)    1=시작 트리거
M11             모터 정지 명령 (W)    1=정지 트리거

X0              시작 버튼             1=ON
X1              정지 버튼             1=ON
X2              비상정지 (NC)         1=정상, 0=비상정지

Y0              운전 램프             1=점등
Y1              정지 램프             1=점등
Y2              알람 램프             1=점등
```

### 3.4 상태 워드 (D100) 비트 구성

| 비트 | 이름 | 설명 |
|------|------|------|
| Bit 0 | Running | 운전 중 |
| Bit 1 | Alarm | 알람 발생 |
| Bit 2 | Safety OK | 안전 상태 정상 |

---

## 4. Node-RED 연동

### 4.1 필요 노드 설치

Node-RED 팔레트에서 설치:
- `node-red-contrib-mcprotocol`

```bash
# 또는 명령줄에서
cd ~/.node-red
npm install node-red-contrib-mcprotocol
```

### 4.2 MC Protocol 노드 설정

**Connection 설정:**
```
Name: MELSEC-Simulator
Host: melsec-simulator (Docker 내부) 또는 IP
Port: 5000
Frame: 3E (Binary)
ASCII/Binary: Binary
PLC Mode: QnA compatible 3E
```

### 4.3 데이터 읽기 플로우

```json
[
    {
        "id": "mc-read",
        "type": "MC Read",
        "name": "Read D0-D10",
        "topic": "",
        "address": "D0",
        "quantity": "11",
        "connection": "melsec-config"
    },
    {
        "id": "inject-trigger",
        "type": "inject",
        "repeat": "1",
        "payload": ""
    }
]
```

### 4.4 데이터 쓰기 플로우

```json
[
    {
        "id": "mc-write",
        "type": "MC Write",
        "name": "Write M10",
        "address": "M10",
        "connection": "melsec-config"
    },
    {
        "id": "function-prepare",
        "type": "function",
        "func": "msg.payload = [1]; // M10 = ON\nreturn msg;"
    }
]
```

---

## 5. 데이터 읽기 상세

### 5.1 단일 워드 읽기

```javascript
// Function 노드에서 읽기 요청 설정
msg.topic = "D0";      // 시작 주소
msg.quantity = 1;      // 읽을 개수
return msg;
```

### 5.2 연속 워드 읽기

```javascript
// D0부터 D10까지 11개 워드 읽기
msg.topic = "D0";
msg.quantity = 11;
return msg;
```

### 5.3 비트 디바이스 읽기

```javascript
// M0부터 M9까지 10개 비트 읽기
msg.topic = "M0";
msg.quantity = 10;
return msg;
```

### 5.4 읽은 데이터 처리

```javascript
// MC Read 노드 출력 처리
var data = msg.payload;

// D0-D10 데이터 파싱
var sensorData = {
    temperature: data[0] / 10,    // D0: 온도 (스케일 /10)
    humidity: data[1] / 10,       // D1: 습도 (스케일 /10)
    pressure: data[2] / 100,      // D2: 압력 (스케일 /100)
    motorSpeed: data[10]          // D10: 모터 속도
};

// 32비트 카운터 조합 (D20-D21)
// var count = (data[21] << 16) + data[20];

msg.payload = sensorData;
return msg;
```

---

## 6. 데이터 쓰기 상세

### 6.1 단일 워드 쓰기

```javascript
// D10에 값 쓰기 (모터 속도 설정)
msg.topic = "D10";
msg.payload = [1500];  // 배열 형태로 전달
return msg;
```

### 6.2 연속 워드 쓰기

```javascript
// D100부터 3개 워드 쓰기
msg.topic = "D100";
msg.payload = [100, 200, 300];
return msg;
```

### 6.3 비트 디바이스 쓰기

```javascript
// M10 ON (모터 시작)
msg.topic = "M10";
msg.payload = [1];
return msg;

// M11 ON (모터 정지)
msg.topic = "M11";
msg.payload = [1];
return msg;
```

### 6.4 MQTT 연동 제어

```javascript
// MQTT 메시지를 MC 명령으로 변환
// factory/line1/control/motor 토픽 수신

var command = JSON.parse(msg.payload);

if (command.action === "start") {
    msg.topic = "M10";
    msg.payload = [1];
} else if (command.action === "stop") {
    msg.topic = "M11";
    msg.payload = [1];
} else if (command.action === "setSpeed") {
    msg.topic = "D10";
    msg.payload = [command.speed];
}

return msg;
```

---

## 7. InfluxDB 저장

### 7.1 완전한 데이터 수집 플로우

```
[Inject 1초] → [MC Read D0-D10] → [Function 변환] → [InfluxDB Out]
```

### 7.2 데이터 변환 함수

```javascript
// MC 프로토콜 데이터를 InfluxDB 형식으로 변환
var data = msg.payload;

msg.payload = [{
    measurement: "plc_data",
    tags: {
        source: "melsec",
        plc: "MELSEC-Simulator",
        line: "ProductionLine1"
    },
    fields: {
        temperature: data[0] / 10,
        humidity: data[1] / 10,
        pressure: data[2] / 100,
        motor_speed: data[10]
    },
    timestamp: new Date()
}];

return msg;
```

### 7.3 상태 데이터 수집

```javascript
// M0-M2 비트 상태를 InfluxDB에 저장
var bits = msg.payload;

msg.payload = [{
    measurement: "plc_status",
    tags: {
        source: "melsec",
        plc: "MELSEC-Simulator"
    },
    fields: {
        running: bits[0] === 1,
        alarm: bits[1] === 1,
        safety_ok: bits[2] === 1
    },
    timestamp: new Date()
}];

return msg;
```

---

## 8. 알람 처리

### 8.1 알람 조건 감지

```javascript
// D100 상태 워드에서 알람 비트 확인
var status = msg.payload[0];  // D100
var alarmBit = (status >> 1) & 0x01;

// 이전 상태와 비교
var prevAlarm = context.get('prevAlarm') || 0;
context.set('prevAlarm', alarmBit);

if (alarmBit === 1 && prevAlarm === 0) {
    // 새 알람 발생
    msg.alarm = {
        type: "MELSEC_ALARM",
        device: "D100",
        bit: 1,
        timestamp: new Date().toISOString(),
        severity: "WARNING"
    };
    return [msg, null];  // 알람 출력
} else {
    return [null, msg];  // 정상 출력
}
```

### 8.2 MQTT 알람 발행

```javascript
// 알람을 MQTT로 발행
msg.topic = "factory/line1/alarms/plc";
msg.payload = JSON.stringify(msg.alarm);
return msg;
```

---

## 9. 실제 PLC 연결

### 9.1 MELSEC PLC 설정

GX Works2/GX Works3에서 설정:

1. **이더넷 모듈 설정**
   - IP 주소 설정
   - 포트 번호 설정 (기본: 5000 또는 5001)

2. **MC 프로토콜 설정**
   - 프레임 타입: 3E Binary
   - 통신 타이머 설정

3. **방화벽 설정**
   - 지정 포트 개방

### 9.2 GX Works 설정 예시

```
[네트워크 파라미터]
- 자국 IP: 192.168.1.10
- 서브넷 마스크: 255.255.255.0
- 게이트웨이: 192.168.1.1

[MELSOFT 접속 설정]
- MC 프로토콜 사용: 허가
- 포트 번호: 5000
- 바이너리/ASCII: Binary
```

### 9.3 Node-RED 설정 변경

```
Host: 192.168.1.10  (실제 PLC IP)
Port: 5000          (설정한 포트)
Frame: 3E Binary
```

---

## 10. 문제 해결

### 10.1 연결 실패

```bash
# 시뮬레이터 로그 확인
docker logs ming-melsec-simulator

# 포트 상태 확인
netstat -tlnp | grep 5000

# 연결 테스트
nc -zv raspberrypi 5000
```

### 10.2 일반적인 오류

| 오류 | 원인 | 해결 |
|------|------|------|
| Connection refused | 포트 미오픈 | 시뮬레이터/PLC 상태 확인 |
| Timeout | 네트워크 지연 | 타임아웃 값 증가 |
| Invalid response | 프레임 불일치 | 3E Binary 설정 확인 |
| Wrong data | 주소 오류 | 디바이스 주소 형식 확인 |

### 10.3 데이터 검증

```javascript
// 디버그용 데이터 출력
node.warn("Raw data: " + JSON.stringify(msg.payload));
node.warn("D0 (Temp): " + msg.payload[0] / 10 + "°C");
```

---

## 11. 고급 기능

### 11.1 다중 영역 읽기

```javascript
// 여러 영역을 순차적으로 읽기
var areas = [
    { device: "D0", count: 10 },
    { device: "M0", count: 20 },
    { device: "D100", count: 5 }
];

// 각 영역별로 읽기 요청
```

### 11.2 32비트 데이터 처리

```javascript
// D20-D21을 32비트 값으로 조합
var lowWord = data[0];   // D20
var highWord = data[1];  // D21
var count32 = (highWord << 16) + lowWord;

// 32비트 값을 2개 워드로 분리
var value32 = 123456789;
var d20 = value32 & 0xFFFF;
var d21 = (value32 >> 16) & 0xFFFF;
msg.payload = [d20, d21];
```

### 11.3 실수형 데이터 처리

```javascript
// D0-D1을 IEEE 754 float로 변환
var buffer = new ArrayBuffer(4);
var view = new DataView(buffer);
view.setUint16(0, data[0], true);  // Little Endian
view.setUint16(2, data[1], true);
var floatValue = view.getFloat32(0, true);
```

---

## 12. 성능 최적화

### 12.1 폴링 주기

| 데이터 타입 | 권장 주기 |
|-------------|-----------|
| 센서 데이터 | 500ms ~ 1s |
| 상태 비트 | 200ms ~ 500ms |
| 카운터 | 1s ~ 5s |
| 알람 | 100ms ~ 200ms |

### 12.2 배치 읽기

```javascript
// 개별 읽기 대신 배치 읽기 사용
// 비효율적: D0 읽기, D1 읽기, D2 읽기 (3회 통신)
// 효율적: D0부터 3개 읽기 (1회 통신)
msg.topic = "D0";
msg.quantity = 3;
```

---

## 참고 자료

- [Mitsubishi Electric FA](https://www.mitsubishielectric.co.jp/fa/)
- [MELSEC Communication Protocol Reference](https://www.mitsubishielectric.com/fa/products/cnt/plc/)
- [node-red-contrib-mcprotocol](https://flows.nodered.org/node/node-red-contrib-mcprotocol)
- [GX Works3 Operating Manual](https://www.mitsubishielectric.co.jp/fa/products/cnt/plceng/)
