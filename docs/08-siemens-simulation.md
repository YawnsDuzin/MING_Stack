# Siemens S7 시뮬레이션 가이드

> Siemens S7 PLC 통신 시뮬레이터 및 Node-RED 연동

---

## 1. Siemens S7 통신 개요

### 1.1 S7 프로토콜이란?

S7 통신은 Siemens PLC (S7-300, S7-400, S7-1200, S7-1500)와 통신하기 위한 프로토콜입니다.

| 계층 | 프로토콜 |
|------|----------|
| Application | S7 Protocol |
| Transport | ISO-on-TCP (RFC 1006) |
| Network | TCP/IP |

### 1.2 데이터 영역

| 영역 | 약어 | 설명 |
|------|------|------|
| Data Block | DB | 사용자 데이터 저장 |
| Marker | M | 중간 결과 저장 |
| Input | I | 디지털/아날로그 입력 |
| Output | Q | 디지털/아날로그 출력 |
| Timer | T | 타이머 |
| Counter | C | 카운터 |

---

## 2. 시뮬레이터 구조

### 2.1 시뮬레이터 시작

```bash
# 시뮬레이터 프로파일로 시작
docker compose --profile simulators up -d

# S7 시뮬레이터만 시작
docker compose up -d s7-simulator
```

### 2.2 접속 정보

```
Host: raspberrypi (또는 IP 주소)
Port: 1102 (기본 S7 포트 102 대신 non-privileged 포트 사용)
Rack: 0
Slot: 1
```

> **Note**: 표준 S7 포트는 102이지만, 루트 권한이 필요하므로
> 이 시뮬레이터는 1102 포트를 사용합니다.

### 2.3 데이터 블록 구조 (DB1)

```
Offset  Type    Name            Description
------  ----    ----            -----------
0       REAL    Temperature     온도 (°C)
4       REAL    Humidity        습도 (%)
8       REAL    Pressure        압력 (bar)
12      INT     MotorSpeed      모터 속도 (RPM)
14      DINT    ProductCount    생산 카운트
18      BYTE    StatusBits      상태 비트
19      BYTE    ErrorCode       에러 코드
```

### 2.4 상태 비트 (StatusBits, Offset 18)

| Bit | 이름 | 설명 |
|-----|------|------|
| 0 | Motor Running | 모터 가동 중 |
| 1 | Alarm Active | 알람 활성화 |
| 2 | Safety OK | 안전 상태 |
| 3 | Auto Mode | 자동 운전 모드 |

### 2.5 마커 영역 (M)

| 주소 | 이름 | 설명 |
|------|------|------|
| M0.0 | Motor Start | 모터 시작 명령 |
| M0.1 | Motor Stop | 모터 정지 명령 |
| M0.2 | Alarm Reset | 알람 리셋 |
| M0.3 | Emergency Stop | 비상 정지 |

---

## 3. 시뮬레이터 동작

### 3.1 데이터 시뮬레이션

시뮬레이터는 1초마다 데이터를 업데이트합니다:

```python
# 온도: 25°C 기준, 30분 주기
temp = 25.0 + 5 * math.sin(elapsed / 1800 * 2 * math.pi)
temp += random.gauss(0, 0.3)

# 습도: 60% 기준
humidity = 60.0 + random.gauss(0, 2)

# 압력: 1.0 bar 기준
pressure = 1.0 + random.gauss(0, 0.02)

# 모터 속도: 가동 시 1500 RPM
motor_speed = 1500 + random.gauss(0, 20) if running else 0
```

### 3.2 알람 조건

- 온도 > 35°C → 알람 활성화, 에러 코드 1
- 습도 > 80% → 알람 활성화, 에러 코드 2

---

## 4. Node-RED 연동

### 4.1 필요 노드 설치

Node-RED 팔레트에서 설치:
- `node-red-contrib-s7`

### 4.2 S7 연결 설정

```
Name: S7-Simulator
Transport: ISO-on-TCP
Address: s7-simulator
Port: 1102
Rack: 0
Slot: 1
Cycle Time: 500 (ms)
```

### 4.3 변수 설정

S7 Endpoint 노드에서 변수 정의:

```
Name: Temperature
Address: DB1,REAL0
Mode: Read

Name: Humidity
Address: DB1,REAL4
Mode: Read

Name: Pressure
Address: DB1,REAL8
Mode: Read

Name: MotorSpeed
Address: DB1,INT12
Mode: Read

Name: ProductCount
Address: DB1,DINT14
Mode: Read

Name: StatusBits
Address: DB1,BYTE18
Mode: Read

Name: MotorStart
Address: M0.0
Mode: Write
```

---

## 5. S7 주소 형식

### 5.1 데이터 블록 (DB)

```
DB{번호},{타입}{오프셋}

예시:
DB1,REAL0      - DB1의 오프셋 0에서 REAL(4바이트) 읽기
DB1,INT12      - DB1의 오프셋 12에서 INT(2바이트) 읽기
DB1,DINT14     - DB1의 오프셋 14에서 DINT(4바이트) 읽기
DB1,BYTE18     - DB1의 오프셋 18에서 BYTE(1바이트) 읽기
DB1,X18.0      - DB1의 오프셋 18, 비트 0 읽기
```

### 5.2 마커 영역 (M)

```
M{바이트}.{비트}
MB{바이트}
MW{워드}
MD{더블워드}

예시:
M0.0           - 마커 바이트 0, 비트 0
M0.1           - 마커 바이트 0, 비트 1
MB0            - 마커 바이트 0 (8비트)
MW0            - 마커 워드 0 (16비트)
```

### 5.3 데이터 타입

| 타입 | 크기 | 설명 |
|------|------|------|
| X | 1 bit | Boolean |
| BYTE | 1 byte | 0-255 |
| CHAR | 1 byte | ASCII 문자 |
| INT | 2 bytes | -32768 ~ 32767 |
| WORD | 2 bytes | 0-65535 |
| DINT | 4 bytes | 32비트 정수 |
| DWORD | 4 bytes | 32비트 unsigned |
| REAL | 4 bytes | 부동소수점 |

---

## 6. 데이터 읽기 플로우

### 6.1 기본 읽기

```
[S7 In] → [Function: 데이터 처리] → [InfluxDB Out]
```

### 6.2 S7 In 노드 설정

```
Name: Read PLC Data
Mode: All variables
```

### 6.3 데이터 처리 함수

```javascript
// S7에서 읽은 데이터를 InfluxDB 형식으로 변환
var data = msg.payload;

msg.payload = [{
    measurement: "plc_data",
    tags: {
        source: "s7",
        plc: "S7-Simulator",
        line: "ProductionLine1"
    },
    fields: {
        temperature: data.Temperature,
        humidity: data.Humidity,
        pressure: data.Pressure,
        motor_speed: data.MotorSpeed,
        product_count: data.ProductCount,
        status: data.StatusBits
    },
    timestamp: new Date()
}];

return msg;
```

---

## 7. 데이터 쓰기 플로우

### 7.1 모터 제어

```
[Inject: Start] → [Function] → [S7 Out]
```

### 7.2 모터 시작 함수

```javascript
// 모터 시작 명령
msg.payload = {
    "MotorStart": true
};
return msg;
```

### 7.3 모터 정지 함수

```javascript
// 모터 정지 명령
msg.payload = {
    "MotorStop": true
};
return msg;
```

### 7.4 MQTT 연동 제어

```
[MQTT In: factory/+/control/motor] → [Function] → [S7 Out]
```

```javascript
// MQTT 메시지를 S7 명령으로 변환
var command = JSON.parse(msg.payload);

if (command.action === "start") {
    msg.payload = { "MotorStart": true };
} else if (command.action === "stop") {
    msg.payload = { "MotorStop": true };
} else if (command.action === "emergency_stop") {
    msg.payload = { "EmergencyStop": true };
}

return msg;
```

---

## 8. 상태 비트 처리

### 8.1 비트 파싱

```javascript
// StatusBits 바이트를 개별 상태로 분리
var status = msg.payload.StatusBits;

var states = {
    motorRunning: (status & 0x01) !== 0,
    alarmActive: (status & 0x02) !== 0,
    safetyOK: (status & 0x04) !== 0,
    autoMode: (status & 0x08) !== 0
};

msg.payload = states;
return msg;
```

### 8.2 알람 감지

```javascript
// 알람 상태 변경 감지
var status = msg.payload.StatusBits;
var alarmActive = (status & 0x02) !== 0;

// 이전 상태와 비교 (컨텍스트 사용)
var prevAlarm = context.get('prevAlarm') || false;
context.set('prevAlarm', alarmActive);

if (alarmActive && !prevAlarm) {
    // 새 알람 발생
    msg.topic = "factory/line1/alarms/plc";
    msg.payload = {
        type: "PLC_ALARM",
        errorCode: msg.payload.ErrorCode,
        timestamp: new Date().toISOString()
    };
    return msg;
}

return null;  // 알람 변경 없음
```

---

## 9. 완전한 모니터링 플로우

### 9.1 플로우 구성

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  [S7 In] ──┬──→ [InfluxDB 저장]                            │
│            │                                                │
│            ├──→ [상태 비트 파싱] ──→ [알람 체크] ──→ [MQTT] │
│            │                                                │
│            └──→ [Debug]                                     │
│                                                             │
│  [MQTT In: control] ──→ [명령 변환] ──→ [S7 Out]           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 9.2 전체 데이터 처리 함수

```javascript
// S7 데이터 종합 처리
var data = msg.payload;

// 1. InfluxDB용 메시지
var influxMsg = {
    payload: [{
        measurement: "plc_data",
        tags: {
            plc: "S7-Simulator",
            line: "Line1"
        },
        fields: {
            temperature: data.Temperature,
            humidity: data.Humidity,
            pressure: data.Pressure,
            motor_speed: data.MotorSpeed,
            product_count: data.ProductCount
        }
    }]
};

// 2. 상태 메시지 (MQTT 발행용)
var status = data.StatusBits;
var statusMsg = {
    topic: "factory/line1/status",
    payload: JSON.stringify({
        motorRunning: (status & 0x01) !== 0,
        alarmActive: (status & 0x02) !== 0,
        safetyOK: (status & 0x04) !== 0,
        autoMode: (status & 0x08) !== 0,
        errorCode: data.ErrorCode,
        timestamp: new Date().toISOString()
    })
};

return [influxMsg, statusMsg];
```

---

## 10. 문제 해결

### 10.1 연결 실패

```bash
# 시뮬레이터 로그 확인
docker logs ming-s7-simulator

# 포트 상태 확인
netstat -tlnp | grep 1102

# 연결 테스트
nc -zv raspberrypi 1102
```

### 10.2 일반적인 오류

| 오류 | 원인 | 해결 |
|------|------|------|
| Connection refused | 포트 미오픈 | 시뮬레이터 재시작 |
| Wrong CPU type | Rack/Slot 오류 | Rack: 0, Slot: 1 설정 |
| Read/Write failed | 주소 오류 | 주소 형식 확인 |

### 10.3 데이터 검증

```javascript
// 디버그용 데이터 출력
node.warn("Temperature: " + msg.payload.Temperature);
node.warn("Raw bytes: " + JSON.stringify(msg.payload));
```

---

## 11. ARM64 호환성

### 11.1 순수 Python 구현

이 시뮬레이터는 ARM64 (라즈베리파이) 호환을 위해 순수 Python으로 구현되었습니다.
snap7 라이브러리를 사용하지 않아 별도의 컴파일 없이 실행됩니다.

### 11.2 제한 사항

- 기본적인 읽기/쓰기만 지원
- 복잡한 S7 기능 (블록 전송 등)은 미지원
- 개발/테스트 용도로 적합

---

## 12. 실제 PLC 연결

### 12.1 실제 Siemens PLC 설정

실제 PLC 연결 시 주의사항:

```
1. PLC 설정에서 PUT/GET 통신 허용
2. 방화벽에서 포트 102 개방
3. 올바른 Rack/Slot 번호 확인
   - S7-300: Rack=0, Slot=2
   - S7-400: Rack=0, Slot=3
   - S7-1200: Rack=0, Slot=1
   - S7-1500: Rack=0, Slot=1
```

### 12.2 Node-RED 설정 변경

```
Address: 192.168.1.10  (실제 PLC IP)
Port: 102              (표준 S7 포트)
Rack: 0
Slot: 1                (또는 2, 모델에 따라)
```

---

## 참고 자료

- [node-red-contrib-s7](https://flows.nodered.org/node/node-red-contrib-s7)
- [Siemens S7 Communication](https://support.industry.siemens.com/)
- [ISO-on-TCP (RFC 1006)](https://tools.ietf.org/html/rfc1006)
