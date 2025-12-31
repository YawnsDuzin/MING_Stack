# Modbus TCP 시뮬레이션 가이드

> Node-RED를 활용한 Modbus 디바이스 데이터 수집 및 제어

---

## 1. Modbus 프로토콜 개요

### 1.1 Modbus TCP란?

Modbus TCP는 산업용 통신 프로토콜로, PLC, 센서, 모터 드라이브 등과 통신하는 데 사용됩니다.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Modbus TCP 통신 구조                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐              ┌─────────────┐              ┌─────┐ │
│  │  Node-RED   │◀──TCP/IP───▶│   Modbus    │◀──Internal──▶│ PLC │ │
│  │  (Client)   │              │   Gateway   │              │     │ │
│  └─────────────┘              └─────────────┘              └─────┘ │
│                                                                     │
│  포트: 502 (표준) 또는 5020 (시뮬레이터)                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 데이터 타입

| 타입 | Function Code | 읽기 | 쓰기 | 설명 |
|------|--------------|------|------|------|
| Coils | FC 01/05/15 | O | O | 디지털 출력 (1비트) |
| Discrete Inputs | FC 02 | O | X | 디지털 입력 (1비트) |
| Input Registers | FC 04 | O | X | 아날로그 입력 (16비트) |
| Holding Registers | FC 03/06/16 | O | O | 아날로그 출력 (16비트) |

---

## 2. 시뮬레이터 구성

### 2.1 시뮬레이터 레지스터 맵

```
┌────────────────────────────────────────────────────────────────┐
│                    Modbus 레지스터 맵                           │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Holding Registers (FC 03/06/16):                              │
│  ├── 0:  온도 (x0.1 °C)     예: 255 = 25.5°C                  │
│  ├── 1:  습도 (x0.1 %)      예: 602 = 60.2%                   │
│  ├── 2:  압력 (x0.01 bar)   예: 120 = 1.20 bar                │
│  ├── 3:  모터 속도 (RPM)                                       │
│  ├── 4:  전류 (x0.01 A)                                        │
│  ├── 5:  전압 (x0.1 V)                                         │
│  ├── 6:  전력 (W)                                              │
│  ├── 7:  생산 카운트                                            │
│  ├── 8:  에러 코드                                              │
│  └── 9:  상태 비트                                              │
│                                                                │
│  Coils (FC 01/05/15):                                          │
│  ├── 0:  모터 시작/정지                                         │
│  ├── 1:  알람 리셋                                              │
│  └── 2:  비상 정지                                              │
│                                                                │
│  Discrete Inputs (FC 02):                                      │
│  ├── 0:  모터 운전 중                                           │
│  ├── 1:  알람 활성                                              │
│  └── 2:  안전 상태                                              │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 2.2 시뮬레이터 시작

```bash
# Docker Compose로 시뮬레이터 시작
docker compose up -d modbus-simulator

# 로그 확인
docker logs -f ming-modbus-simulator
```

---

## 3. Node-RED 플로우 구성

### 3.1 Modbus 클라이언트 설정

```
1. node-red-contrib-modbus 노드 설치
2. Modbus-Client 노드 설정:
   - Type: TCP
   - Host: modbus-simulator (Docker) 또는 IP 주소
   - Port: 5020
   - Unit-Id: 1
```

### 3.2 데이터 읽기 플로우

```
[Inject 5초] → [Modbus Read] → [Transform] → [MQTT Publish]
                    ↓
              [Debug]
```

**Modbus Read 설정:**
- FC: Read Holding Registers (FC 03)
- Address: 0
- Quantity: 10
- Poll Rate: 5 seconds

### 3.3 데이터 변환 함수

```javascript
// Modbus 레지스터 값을 실제 값으로 변환
const registers = msg.payload;

const data = {
    temperature: registers[0] / 10,      // °C
    humidity: registers[1] / 10,         // %
    pressure: registers[2] / 100,        // bar
    motor_speed: registers[3],           // RPM
    current: registers[4] / 100,         // A
    voltage: registers[5] / 10,          // V
    power: registers[6],                 // W
    production_count: registers[7],
    error_code: registers[8],
    status: {
        motor_running: (registers[9] & 0x01) === 1,
        alarm_active: (registers[9] & 0x02) === 2,
        safety_ok: (registers[9] & 0x04) === 4
    }
};

msg.topic = 'factory/line1/modbus_device/data';
msg.payload = data;

return msg;
```

---

## 4. 제어 명령 구현

### 4.1 제어 토픽 구조

```
factory/line1/modbus_device/control
{
    "command": "set_speed",
    "register": 10,
    "value": 1500
}

factory/line1/modbus_device/control
{
    "command": "motor_start",
    "coil": 0,
    "value": true
}
```

### 4.2 제어 플로우

```
[MQTT Subscribe] → [Parse Command] → [Modbus Write] → [Response]
```

### 4.3 제어 명령 처리 함수

```javascript
// 제어 명령 파싱 및 Modbus 형식 변환
const command = msg.payload;

switch (command.command) {
    case 'motor_start':
        msg.payload = {
            value: command.value ? 1 : 0,
            'fc': 5,  // Write Single Coil
            'unitid': 1,
            'address': 0,
            'quantity': 1
        };
        break;

    case 'motor_stop':
        msg.payload = {
            value: 0,
            'fc': 5,
            'unitid': 1,
            'address': 0,
            'quantity': 1
        };
        break;

    case 'set_speed':
        msg.payload = {
            value: command.value,
            'fc': 6,  // Write Single Register
            'unitid': 1,
            'address': command.register || 10,
            'quantity': 1
        };
        break;

    case 'emergency_stop':
        msg.payload = {
            value: 1,
            'fc': 5,
            'unitid': 1,
            'address': 2,  // 비상정지 Coil
            'quantity': 1
        };
        break;

    default:
        node.warn('Unknown command: ' + command.command);
        return null;
}

msg.command_info = command;
return msg;
```

---

## 5. 실제 PLC 연결 시 고려사항

### 5.1 일반적인 Modbus TCP 연결

```javascript
// Modbus Client 설정 예시
{
    "name": "Production PLC",
    "clienttype": "tcp",
    "tcpHost": "192.168.1.10",
    "tcpPort": "502",
    "unit_id": "1",
    "commandDelay": "1",
    "clientTimeout": "1000",
    "reconnectOnTimeout": true,
    "reconnectTimeout": "2000"
}
```

### 5.2 다중 슬레이브 연결

```
┌─────────────────────────────────────────────────────────────────┐
│                   다중 Modbus 슬레이브 구성                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Node-RED                                                       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                                                            │ │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐             │ │
│  │  │ Read     │    │ Read     │    │ Read     │             │ │
│  │  │ Unit 1   │    │ Unit 2   │    │ Unit 3   │             │ │
│  │  └────┬─────┘    └────┬─────┘    └────┬─────┘             │ │
│  │       │               │               │                    │ │
│  │       └───────────────┼───────────────┘                    │ │
│  │                       │                                    │ │
│  │               ┌───────┴───────┐                            │ │
│  │               │ Modbus Client │                            │ │
│  │               └───────┬───────┘                            │ │
│  └───────────────────────┼────────────────────────────────────┘ │
│                          │                                      │
│                          ▼                                      │
│              ┌───────────────────────┐                          │
│              │   Modbus Gateway      │                          │
│              │   192.168.1.10:502    │                          │
│              └───────────────────────┘                          │
│                          │                                      │
│          ┌───────────────┼───────────────┐                      │
│          ▼               ▼               ▼                      │
│      ┌───────┐       ┌───────┐       ┌───────┐                  │
│      │ PLC 1 │       │ PLC 2 │       │ PLC 3 │                  │
│      │ ID: 1 │       │ ID: 2 │       │ ID: 3 │                  │
│      └───────┘       └───────┘       └───────┘                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 에러 처리

```javascript
// Modbus 읽기 결과 에러 처리
if (msg.payload === null || msg.payload === undefined) {
    node.error('Modbus read failed');

    // 알람 발행
    msg.topic = 'factory/alerts/communication';
    msg.payload = {
        type: 'communication_error',
        device: 'modbus_device_001',
        message: 'Failed to read Modbus registers',
        timestamp: new Date().toISOString()
    };

    return [null, msg];  // 두 번째 출력으로 에러 전달
}

// 정상 처리
return [msg, null];
```

---

## 6. 성능 최적화

### 6.1 폴링 최적화

```javascript
// 데이터 중요도에 따른 폴링 주기 설정
const pollingConfig = {
    critical: {
        registers: [0, 1, 2],    // 온도, 습도, 압력
        interval: 1000           // 1초
    },
    normal: {
        registers: [3, 4, 5, 6], // 모터 데이터
        interval: 5000           // 5초
    },
    slow: {
        registers: [7, 8, 9],    // 카운트, 상태
        interval: 10000          // 10초
    }
};
```

### 6.2 변경 감지 (Change Detection)

```javascript
// 이전 값과 비교하여 변경된 경우만 발행
const previousValues = flow.get('previousModbusValues') || {};
const currentValues = msg.payload;
const changes = {};

for (const [key, value] of Object.entries(currentValues)) {
    if (previousValues[key] !== value) {
        changes[key] = {
            previous: previousValues[key],
            current: value
        };
    }
}

if (Object.keys(changes).length > 0) {
    flow.set('previousModbusValues', currentValues);
    msg.payload = {
        data: currentValues,
        changes: changes,
        timestamp: new Date().toISOString()
    };
    return msg;
}

return null;  // 변경 없으면 전달하지 않음
```

---

## 7. 테스트

### 7.1 시뮬레이터 테스트

```bash
# modbus-cli 도구로 테스트
pip install modbus-cli

# Holding Register 읽기
modbus -s 1 192.168.10.100 5020 h@0/10

# Coil 쓰기 (모터 시작)
modbus -s 1 192.168.10.100 5020 c@0=1

# Register 쓰기
modbus -s 1 192.168.10.100 5020 h@10=1500
```

### 7.2 MQTT 메시지 확인

```bash
# MQTT 구독으로 데이터 확인
mosquitto_sub -h localhost -t 'factory/line1/modbus_device/#' -v

# 제어 명령 발행 테스트
mosquitto_pub -h localhost -t 'factory/line1/modbus_device/control' \
    -m '{"command":"motor_start","value":true}'
```

---

## 참고 자료

- [Modbus Protocol Specification](https://modbus.org/specs.php)
- [node-red-contrib-modbus](https://flows.nodered.org/node/node-red-contrib-modbus)
