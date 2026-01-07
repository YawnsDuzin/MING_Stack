# Node-RED 설정 가이드

> Node-RED 플로우 기반 프로그래밍 환경 설정

---

## 1. Node-RED 개요

Node-RED는 IBM이 개발한 플로우 기반 프로그래밍 도구로, 하드웨어 장치, API, 온라인 서비스를 시각적으로 연결합니다.

### 1.1 MING Stack에 설치된 노드

| 노드 패키지 | 용도 |
|------------|------|
| node-red-contrib-modbus | Modbus TCP/RTU 통신 |
| node-red-contrib-opcua | OPC-UA 클라이언트 |
| node-red-contrib-s7 | Siemens S7 PLC 통신 |
| node-red-contrib-influxdb | InfluxDB 연동 |
| node-red-dashboard | 웹 대시보드 |

---

## 2. 접속 정보

```
URL: http://raspberrypi:1880
Username: admin
Password: admin123
```

---

## 3. 에디터 인터페이스

### 3.1 기본 구성

```
┌─────────────────────────────────────────────────────────────┐
│  [팔레트]    │         [플로우 캔버스]         │  [정보/디버그] │
│             │                                │              │
│  - Input    │   ┌─────┐    ┌─────┐          │  ● 디버그    │
│  - Output   │   │노드1│───▶│노드2│          │  ○ 정보     │
│  - Function │   └─────┘    └─────┘          │              │
│  - Network  │                                │              │
│  ...        │                                │              │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 단축키

| 단축키 | 기능 |
|--------|------|
| Ctrl+E | 내보내기 |
| Ctrl+I | 가져오기 |
| Ctrl+D | 배포 |
| Ctrl+Space | 자동완성 |
| Ctrl+Z | 실행취소 |

---

## 4. MQTT 연결 설정

### 4.1 MQTT Broker 노드 설정

```
Server: mosquitto (Docker 내부) 또는 IP 주소
Port: 1883
Client ID: nodered-client
Username: nodered
Password: mqtt_pass
```

### 4.2 Subscribe 플로우

```
[MQTT In] ──▶ [JSON Parse] ──▶ [Function] ──▶ [Debug]
```

### 4.3 Publish 플로우

```
[Inject] ──▶ [Function] ──▶ [MQTT Out]
```

---

## 5. InfluxDB 연결 설정

### 5.1 InfluxDB 노드 설정

```
Version: 2.0
URL: http://influxdb:8086
Token: ming-super-secret-token
Organization: ming-org
Bucket: factory
```

### 5.2 데이터 쓰기 함수

```javascript
// 센서 데이터를 InfluxDB 형식으로 변환
msg.payload = [{
    measurement: "sensor_data",
    tags: {
        location: msg.topic.split('/')[2],
        device: msg.topic.split('/')[3]
    },
    fields: msg.payload,
    timestamp: new Date()
}];
return msg;
```

---

## 6. 산업용 프로토콜 설정

### 6.1 Modbus TCP 읽기

```
Modbus Read 노드 설정:
- Server: modbus-simulator (또는 실제 PLC IP)
- Port: 5020
- Unit-ID: 1
- FC: Read Holding Registers (FC3)
- Address: 0
- Quantity: 10
```

### 6.2 OPC-UA 읽기

```
OPC-UA Client 노드 설정:
- Endpoint: opc.tcp://opcua-simulator:4840
- Security Mode: None
- Action: Read
```

### 6.3 S7 PLC 읽기

```
S7 Endpoint 설정:
- Address: s7-simulator
- Port: 1102
- Rack: 0
- Slot: 1

Variables:
- DB1,REAL0 → Temperature
- DB1,REAL4 → Humidity
- DB1,INT12 → MotorSpeed
```

---

## 7. 함수 노드 예제

### 7.1 데이터 변환

```javascript
// Modbus 레지스터를 실제 값으로 변환
const registers = msg.payload;

msg.payload = {
    temperature: registers[0] / 10,
    humidity: registers[1] / 10,
    pressure: registers[2] / 100,
    motor_speed: registers[3]
};

return msg;
```

### 7.2 임계값 체크

```javascript
const data = msg.payload;
const thresholds = {
    temperature: { max: 35, min: 10 },
    humidity: { max: 80, min: 20 }
};

const alerts = [];

if (data.temperature > thresholds.temperature.max) {
    alerts.push({
        type: 'HIGH_TEMP',
        value: data.temperature,
        threshold: thresholds.temperature.max
    });
}

if (alerts.length > 0) {
    msg.payload = { alerts, timestamp: new Date().toISOString() };
    return msg;
}

return null;  // 알람 없으면 전달 안함
```

### 7.3 데이터 집계

```javascript
// 컨텍스트에 데이터 저장 및 평균 계산
const data = msg.payload;
let buffer = context.get('buffer') || [];

buffer.push(data.temperature);
if (buffer.length > 60) buffer.shift();  // 최근 60개 유지

context.set('buffer', buffer);

const avg = buffer.reduce((a, b) => a + b, 0) / buffer.length;

msg.payload = {
    current: data.temperature,
    average: Math.round(avg * 100) / 100,
    samples: buffer.length
};

return msg;
```

---

## 8. 대시보드 설정

### 8.1 대시보드 접속

```
URL: http://raspberrypi:1880/ui
```

### 8.2 대시보드 위젯

- **Gauge**: 실시간 값 표시
- **Chart**: 시계열 그래프
- **Text**: 텍스트 표시
- **Button**: 제어 버튼
- **Switch**: ON/OFF 스위치

---

## 9. 보안 설정

### 9.1 settings.js 수정

```javascript
// 관리자 인증
adminAuth: {
    type: "credentials",
    users: [{
        username: "admin",
        password: "$2b$08$...",  // bcrypt 해시
        permissions: "*"
    }]
},

// 크리덴셜 암호화
credentialSecret: "your-secret-key"
```

### 9.2 비밀번호 해시 생성

```bash
node -e "console.log(require('bcryptjs').hashSync('your_password', 8));"
```

---

## 10. 백업

### 10.1 플로우 내보내기

메뉴 → Export → Download

### 10.2 파일 백업

```bash
# 플로우 파일 백업
cp nodered/data/flows.json backup/
cp nodered/data/flows_cred.json backup/
```

---

## 참고 자료

- [Node-RED Documentation](https://nodered.org/docs/)
- [Node-RED Cookbook](https://cookbook.nodered.org/)
