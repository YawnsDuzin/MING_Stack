# OPC-UA 시뮬레이션 가이드

> OPC-UA 프로토콜 시뮬레이터 구성 및 Node-RED 연동

---

## 1. OPC-UA 개요

### 1.1 OPC-UA란?

OPC-UA (Open Platform Communications Unified Architecture)는 산업 자동화를 위한 표준 통신 프로토콜입니다.

| 특징 | 설명 |
|------|------|
| 플랫폼 독립성 | Windows, Linux, 임베디드 시스템 지원 |
| 보안 | 암호화, 인증, 권한 관리 내장 |
| 정보 모델링 | 객체 지향적 데이터 구조 |
| 확장성 | 소규모부터 대규모 시스템까지 |

### 1.2 주요 용어

| 용어 | 설명 |
|------|------|
| Node | OPC-UA 정보 모델의 기본 단위 |
| NodeId | 노드의 고유 식별자 |
| Namespace | 노드 그룹화를 위한 논리적 공간 |
| Browse | 서버의 노드 구조 탐색 |
| Subscription | 데이터 변경 알림 구독 |

---

## 2. 시뮬레이터 구조

### 2.1 시뮬레이터 시작

```bash
# 시뮬레이터 프로파일로 시작
docker compose --profile simulators up -d

# OPC-UA 시뮬레이터만 시작
docker compose up -d opcua-simulator
```

### 2.2 접속 정보

```
Endpoint URL: opc.tcp://raspberrypi:4840/freeopcua/server/
Security Mode: None (개발용)
```

### 2.3 노드 구조

```
Root
└── Objects
    └── FactorySimulation (ns=2)
        ├── ProductionLine1
        │   ├── Temperature (Double)
        │   ├── Humidity (Double)
        │   ├── Pressure (Double)
        │   ├── MotorSpeed (Int32)
        │   ├── ProductCount (Int64)
        │   ├── IsRunning (Boolean)
        │   └── AlarmActive (Boolean)
        └── ProductionLine2
            └── (동일 구조)
```

---

## 3. 시뮬레이터 코드 분석

### 3.1 데이터 시뮬레이션

시뮬레이터는 실제 공장 환경을 모사합니다:

```python
# 온도: 25°C 기준, 30분 주기 일교차 패턴
temperature = 25.0 + 5 * math.sin(elapsed / 1800 * 2 * math.pi)
temperature += random.gauss(0, 0.5)  # 노이즈

# 습도: 60% 기준, 랜덤 변동
humidity = 60.0 + random.gauss(0, 3)

# 압력: 1.0 bar 기준
pressure = 1.0 + random.gauss(0, 0.05)

# 모터 속도: 가동 중일 때 1500 RPM
motor_speed = 1500 + int(random.gauss(0, 50)) if running else 0
```

### 3.2 NodeId 형식

```
ns=2;s=ProductionLine1.Temperature
ns=2;s=ProductionLine1.MotorSpeed
ns=2;i=1001  (숫자형 NodeId)
```

---

## 4. Node-RED 연동

### 4.1 필요 노드 설치

Node-RED 팔레트에서 설치:
- `node-red-contrib-opcua`

### 4.2 OPC-UA Client 노드 설정

```
Endpoint: opc.tcp://opcua-simulator:4840/freeopcua/server/
Security Policy: None
Security Mode: None
```

### 4.3 데이터 읽기 플로우

```json
[
    {
        "id": "opcua-client",
        "type": "OpcUa-Client",
        "endpoint": "opc.tcp://opcua-simulator:4840/freeopcua/server/",
        "action": "read",
        "deadbandtype": "a",
        "deadbandvalue": 1,
        "time": 1,
        "timeUnit": "s"
    },
    {
        "id": "inject-read",
        "type": "inject",
        "repeat": "5",
        "payload": "",
        "topic": "ns=2;s=ProductionLine1.Temperature"
    }
]
```

### 4.4 Subscription 플로우

```json
[
    {
        "id": "opcua-subscription",
        "type": "OpcUa-Client",
        "action": "subscribe",
        "time": 1,
        "timeUnit": "s"
    },
    {
        "id": "setup-subscription",
        "type": "function",
        "func": "msg.topic = 'ns=2;s=ProductionLine1.Temperature';\nreturn msg;"
    }
]
```

---

## 5. Subscription 구성

### 5.1 다중 노드 구독

```javascript
// Function 노드에서 구독할 노드 목록 설정
var nodes = [
    "ns=2;s=ProductionLine1.Temperature",
    "ns=2;s=ProductionLine1.Humidity",
    "ns=2;s=ProductionLine1.Pressure",
    "ns=2;s=ProductionLine1.MotorSpeed"
];

msg.topic = nodes.join(",");
return msg;
```

### 5.2 데이터 처리

```javascript
// Function 노드에서 수신 데이터 처리
var nodeId = msg.topic;
var value = msg.payload;
var timestamp = new Date();

// InfluxDB로 전송할 형식으로 변환
msg.payload = {
    measurement: "opcua_data",
    tags: {
        nodeId: nodeId,
        line: "ProductionLine1"
    },
    fields: {
        value: value
    },
    timestamp: timestamp
};

return msg;
```

---

## 6. 데이터 쓰기

### 6.1 값 쓰기 플로우

```json
[
    {
        "id": "opcua-write",
        "type": "OpcUa-Client",
        "action": "write"
    },
    {
        "id": "prepare-write",
        "type": "function",
        "func": "msg.topic = 'ns=2;s=ProductionLine1.MotorSpeed';\nmsg.payload = 1800;\nreturn msg;"
    }
]
```

### 6.2 메서드 호출

```javascript
// OPC-UA 메서드 호출 (시뮬레이터 지원 시)
msg.topic = "ns=2;s=ProductionLine1.StartMotor";
msg.methodId = "ns=2;s=StartMethod";
msg.inputArguments = [];
return msg;
```

---

## 7. InfluxDB 저장

### 7.1 완전한 플로우 예시

```
[OPC-UA Subscribe] → [Function: 데이터 변환] → [InfluxDB Out]
```

### 7.2 데이터 변환 함수

```javascript
// OPC-UA 데이터를 InfluxDB 형식으로 변환
var nodeId = msg.topic;
var nodeName = nodeId.split(".").pop();  // Temperature, Humidity 등

msg.payload = [{
    measurement: "sensor_data",
    tags: {
        source: "opcua",
        device: "ProductionLine1",
        sensor: nodeName
    },
    fields: {},
    timestamp: new Date()
}];

// 필드명 동적 설정
msg.payload[0].fields[nodeName.toLowerCase()] = msg.payload;

return msg;
```

---

## 8. 알람 처리

### 8.1 알람 조건 감지

```javascript
// 온도 알람 조건 체크
var temperature = msg.payload;
var alarmThreshold = 35;

if (temperature > alarmThreshold) {
    msg.alarm = {
        type: "HIGH_TEMPERATURE",
        value: temperature,
        threshold: alarmThreshold,
        timestamp: new Date(),
        severity: "WARNING"
    };
    return [msg, null];  // 알람 출력으로
} else {
    return [null, msg];  // 정상 출력으로
}
```

### 8.2 MQTT 알람 발행

```javascript
// 알람을 MQTT로 발행
msg.topic = "factory/line1/alarms/temperature";
msg.payload = JSON.stringify(msg.alarm);
return msg;
```

---

## 9. 보안 설정 (프로덕션)

### 9.1 인증서 기반 보안

```
Security Policy: Basic256Sha256
Security Mode: SignAndEncrypt
```

### 9.2 사용자 인증

```javascript
// OPC-UA 클라이언트 인증 설정
{
    "endpoint": "opc.tcp://server:4840",
    "securityPolicy": "Basic256Sha256",
    "securityMode": "SignAndEncrypt",
    "credentials": {
        "user": "operator",
        "password": "secure_password"
    }
}
```

---

## 10. 문제 해결

### 10.1 연결 실패

```bash
# 시뮬레이터 상태 확인
docker logs ming-opcua-simulator

# 포트 확인
netstat -tlnp | grep 4840
```

### 10.2 NodeId 찾기

```bash
# Python 클라이언트로 브라우징
docker exec -it ming-opcua-simulator python3 -c "
from opcua import Client
c = Client('opc.tcp://localhost:4840/freeopcua/server/')
c.connect()
root = c.get_root_node()
print(root.get_children())
c.disconnect()
"
```

### 10.3 일반적인 오류

| 오류 | 원인 | 해결 |
|------|------|------|
| BadSecurityModeRejected | 보안 모드 불일치 | Security Mode를 None으로 설정 |
| BadNodeIdUnknown | 잘못된 NodeId | Browse로 정확한 NodeId 확인 |
| BadTimeout | 연결 시간 초과 | 네트워크 및 방화벽 확인 |

---

## 11. 성능 최적화

### 11.1 Subscription 최적화

- Publishing Interval: 1000ms 이상 권장
- Sampling Interval: 500ms 이상
- Queue Size: 10 이하

### 11.2 배치 읽기

```javascript
// 여러 노드를 한 번에 읽기
var nodes = [
    "ns=2;s=ProductionLine1.Temperature",
    "ns=2;s=ProductionLine1.Humidity",
    "ns=2;s=ProductionLine1.Pressure"
];
msg.topic = nodes.join(",");
msg.payload = "readmultiple";
return msg;
```

---

## 참고 자료

- [OPC Foundation](https://opcfoundation.org/)
- [python-opcua Documentation](https://python-opcua.readthedocs.io/)
- [node-red-contrib-opcua](https://flows.nodered.org/node/node-red-contrib-opcua)
