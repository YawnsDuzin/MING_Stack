# 스마트 팩토리 구성 예제

> 실제 산업현장에서 MING Stack을 활용한 IoT 시스템 구축 가이드

---

## 1. 시나리오 개요

### 1.1 공장 구성

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        스마트 팩토리 시스템 구성도                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         생산 라인 1                                  │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │   │
│  │  │Conveyor │─▶│CNC 가공 │─▶│ 조립기  │─▶│ 검사기  │─▶│ 포장기  │   │   │
│  │  │ PLC-001 │  │ PLC-002 │  │ PLC-003 │  │ PLC-004 │  │ PLC-005 │   │   │
│  │  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘   │   │
│  │       │            │            │            │            │        │   │
│  │  ┌────┴────┐  ┌────┴────┐  ┌────┴────┐  ┌────┴────┐  ┌────┴────┐   │   │
│  │  │온습도   │  │진동/온도│  │전류/토크│  │비전센서 │  │중량계   │   │   │
│  │  │센서    │  │센서     │  │센서     │  │         │  │         │   │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                      │
│                                      ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Edge Gateway (라즈베리파이)                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │                        MING Stack                            │   │   │
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │   │   │
│  │  │  │Mosquitto│  │InfluxDB │  │ Node-RED│  │ Grafana │        │   │   │
│  │  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                      │
│                                      ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         클라우드/MES 연동                            │   │
│  │                    (선택적 - 상위 시스템 연계)                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 수집 데이터 항목

| 설비 | 수집 데이터 | 수집 주기 | 프로토콜 |
|------|------------|----------|---------|
| 컨베이어 | 속도, 전류, 물품 카운트 | 1초 | Modbus TCP |
| CNC 가공기 | 스핀들 온도, 진동, RPM | 500ms | OPC-UA |
| 조립기 | 토크, 사이클 타임, 카운트 | 1초 | S7 (Siemens) |
| 검사기 | 양품/불량 판정, 이미지 | 이벤트 | MQTT |
| 포장기 | 중량, 포장 속도, 상태 | 1초 | Modbus TCP |
| 환경 센서 | 온도, 습도, 조도 | 10초 | MQTT |

---

## 2. 시스템 구성

### 2.1 네트워크 구성

```
┌─────────────────────────────────────────────────────────────────────┐
│                        네트워크 구성도                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  OT 네트워크 (192.168.10.0/24)                                      │
│  ├── PLC-001 (192.168.10.11)  - Modbus TCP                         │
│  ├── PLC-002 (192.168.10.12)  - OPC-UA                             │
│  ├── PLC-003 (192.168.10.13)  - S7 Protocol                        │
│  ├── PLC-004 (192.168.10.14)  - MQTT                               │
│  ├── PLC-005 (192.168.10.15)  - Modbus TCP                         │
│  └── 환경 센서들 (192.168.10.100-110) - MQTT                        │
│                                                                     │
│  Edge 네트워크 (192.168.10.0/24)                                    │
│  └── Raspberry Pi (192.168.10.100)                                  │
│      ├── Mosquitto   :1883                                          │
│      ├── Node-RED    :1880                                          │
│      ├── InfluxDB    :8086                                          │
│      └── Grafana     :3000                                          │
│                                                                     │
│  IT 네트워크 (192.168.1.0/24) - 선택적                              │
│  └── 상위 시스템 연동                                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 MQTT 토픽 구조

```
factory/
├── plant_seoul/
│   ├── line1/
│   │   ├── conveyor_001/
│   │   │   ├── data           # 센서 데이터
│   │   │   ├── status         # 설비 상태
│   │   │   ├── control        # 제어 명령
│   │   │   └── alarm          # 알람
│   │   ├── cnc_001/
│   │   ├── assembly_001/
│   │   ├── inspection_001/
│   │   └── packing_001/
│   ├── environment/
│   │   ├── zone_a/
│   │   │   └── sensor_001/
│   │   └── zone_b/
│   └── production/
│       ├── summary            # 생산 요약
│       ├── oee                # OEE 데이터
│       └── quality            # 품질 데이터
└── alerts/
    ├── critical               # 긴급 알람
    ├── warning                # 경고
    └── info                   # 정보
```

---

## 3. Node-RED 플로우 구성

### 3.1 데이터 수집 플로우

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Node-RED 데이터 수집 플로우                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  [Modbus Read]──┬──[Transform]──┬──[MQTT Pub]                          │
│  (컨베이어)     │               │                                       │
│                 │               ├──[InfluxDB]                           │
│  [OPC-UA Read]──┤               │                                       │
│  (CNC)         │               ├──[Threshold]──[Alert]                 │
│                 │               │                                       │
│  [S7 Read]─────┤               └──[Dashboard]                          │
│  (조립기)      │                                                        │
│                 │                                                        │
│  [MQTT Sub]────┘                                                        │
│  (검사기)                                                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 데이터 변환 함수 예제

```javascript
// Modbus 데이터 변환
const registers = msg.payload;

const data = {
    timestamp: new Date().toISOString(),
    speed: registers[0] / 10,        // RPM
    current: registers[1] / 100,     // A
    item_count: registers[2],        // 개수
    running: (registers[3] & 0x01) === 1,
    error: (registers[3] & 0x02) === 2
};

msg.topic = 'factory/plant_seoul/line1/conveyor_001/data';
msg.payload = data;

return msg;
```

### 3.3 알람 처리 함수

```javascript
// 임계값 체크 및 알람 생성
const data = msg.payload;
const thresholds = flow.get('thresholds') || {
    temperature: { min: 15, max: 35, critical: 40 },
    vibration: { max: 2.0, critical: 3.0 },
    current: { max: 10, critical: 15 }
};

const alerts = [];

// 온도 체크
if (data.temperature > thresholds.temperature.critical) {
    alerts.push({
        severity: 'critical',
        type: 'temperature_high',
        value: data.temperature,
        threshold: thresholds.temperature.critical,
        message: `온도 임계값 초과: ${data.temperature}°C`
    });
} else if (data.temperature > thresholds.temperature.max) {
    alerts.push({
        severity: 'warning',
        type: 'temperature_high',
        value: data.temperature,
        threshold: thresholds.temperature.max,
        message: `온도 주의: ${data.temperature}°C`
    });
}

// 진동 체크
if (data.vibration > thresholds.vibration.critical) {
    alerts.push({
        severity: 'critical',
        type: 'vibration_high',
        value: data.vibration,
        message: `비정상 진동 감지: ${data.vibration} mm/s`
    });
}

if (alerts.length > 0) {
    msg.payload = {
        device: msg.device,
        timestamp: new Date().toISOString(),
        alerts: alerts
    };
    return msg;
}

return null;
```

---

## 4. InfluxDB 데이터 모델

### 4.1 Measurement 구조

```
# 센서 데이터
measurement: sensor_data
tags:
  - site: plant_seoul
  - line: line1
  - device: conveyor_001
  - sensor_type: motor
fields:
  - speed (float)
  - current (float)
  - temperature (float)
timestamp: 2024-01-15T10:30:00Z

# 생산 데이터
measurement: production
tags:
  - site: plant_seoul
  - line: line1
  - product: product_a
fields:
  - total_count (int)
  - good_count (int)
  - defect_count (int)
  - cycle_time (float)
timestamp: 2024-01-15T10:30:00Z

# 알람 데이터
measurement: alarms
tags:
  - site: plant_seoul
  - device: cnc_001
  - severity: critical
  - type: temperature_high
fields:
  - value (float)
  - threshold (float)
  - acknowledged (bool)
timestamp: 2024-01-15T10:30:00Z
```

### 4.2 보존 정책

```flux
// Raw 데이터 (1초 간격) - 7일
// 다운샘플링 후:
// - 1분 평균 - 30일
// - 1시간 평균 - 1년
// - 1일 평균 - 영구

// InfluxDB Task 예시 (1분 평균)
option task = {name: "downsample_1m", every: 1m}

from(bucket: "factory")
  |> range(start: -2m)
  |> filter(fn: (r) => r["_measurement"] == "sensor_data")
  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
  |> to(bucket: "factory_1m", org: "ming-org")
```

---

## 5. Grafana 대시보드 구성

### 5.1 대시보드 레이아웃

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      생산라인 모니터링 대시보드                           │
├─────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │
│ │ 가동률      │ │ 금일 생산량  │ │ 불량률      │ │     OEE             │ │
│ │   95.2%     │ │   1,234개   │ │   2.1%      │ │     87.5%           │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│ ┌───────────────────────────────────────────────────────────────────┐   │
│ │                      시간별 생산량 추이                            │   │
│ │     ▄▄  ▄▄  ▄▄  ▄▄  ▄▄  ▄▄  ▄▄  ▄▄  ▄▄  ▄▄  ▄▄  ▄▄              │   │
│ │   ████████████████████████████████████████████████              │   │
│ │   08   09   10   11   12   13   14   15   16   17               │   │
│ └───────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────┐ ┌─────────────────────────────────────────┐ │
│ │    설비 상태 맵         │ │        알람 히스토리                     │ │
│ │  ┌───┐ ┌───┐ ┌───┐     │ │  10:25 [경고] CNC 온도 상승              │ │
│ │  │ ● │ │ ● │ │ ● │     │ │  09:15 [정보] 컨베이어 시작              │ │
│ │  └───┘ └───┘ └───┘     │ │  08:30 [긴급] 조립기 정지                │ │
│ │  컨베이어 CNC  조립     │ │                                          │ │
│ └─────────────────────────┘ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2 주요 지표 쿼리

```flux
// OEE (Overall Equipment Effectiveness) 계산
availability = (actual_runtime / planned_runtime) * 100
performance = (actual_output / theoretical_output) * 100
quality = (good_count / total_count) * 100
oee = availability * performance * quality / 10000

// Flux 쿼리 예시
from(bucket: "factory")
  |> range(start: -24h)
  |> filter(fn: (r) => r["_measurement"] == "production")
  |> filter(fn: (r) => r["line"] == "line1")
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> map(fn: (r) => ({
      r with
      quality: float(v: r.good_count) / float(v: r.total_count) * 100.0
  }))
```

---

## 6. 알람 및 알림 구성

### 6.1 알람 계층 구조

```
┌─────────────────────────────────────────────────────────────────────┐
│                         알람 계층 구조                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Level 4: Emergency (비상)                                          │
│  ├── 즉시 생산 정지 필요                                             │
│  ├── 사이렌, SMS, 전화 알림                                          │
│  └── 예: 화재, 가스 누출, 중대 설비 고장                              │
│                                                                     │
│  Level 3: Critical (긴급)                                           │
│  ├── 30분 내 조치 필요                                               │
│  ├── Email, SMS, Telegram 알림                                      │
│  └── 예: 온도 임계값 초과, 주요 설비 이상                             │
│                                                                     │
│  Level 2: Warning (경고)                                            │
│  ├── 4시간 내 조치 필요                                              │
│  ├── Email, Dashboard 표시                                          │
│  └── 예: 경미한 이상, 예방 정비 필요                                  │
│                                                                     │
│  Level 1: Info (정보)                                               │
│  ├── 조치 불필요, 기록용                                             │
│  ├── Dashboard 기록                                                  │
│  └── 예: 설비 시작/정지, 배치 완료                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 6.2 Grafana 알람 규칙 예시

```yaml
# 온도 알람 규칙
name: High Temperature Alert
condition: A
data:
  - refId: A
    queryType: flux
    query: |
      from(bucket: "factory")
        |> range(start: -5m)
        |> filter(fn: (r) => r["_measurement"] == "sensor_data")
        |> filter(fn: (r) => r["_field"] == "temperature")
        |> mean()
noDataState: NoData
execErrState: Error
for: 2m
labels:
  severity: critical
  team: production
notifications:
  - email-alerts
  - telegram-production
```

---

## 7. 시스템 모니터링

### 7.1 헬스체크

```yaml
# docker-compose.yml의 헬스체크 설정
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:1880/"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### 7.2 시스템 대시보드

Node-RED에서 시스템 상태 모니터링:

```javascript
// 시스템 상태 수집
const os = require('os');

const systemStatus = {
    hostname: os.hostname(),
    uptime: os.uptime(),
    loadavg: os.loadavg(),
    totalmem: os.totalmem(),
    freemem: os.freemem(),
    cpus: os.cpus().length
};

msg.topic = 'system/edge_gateway/status';
msg.payload = systemStatus;

return msg;
```

---

## 8. 운영 가이드

### 8.1 일일 점검 항목

- [ ] Docker 컨테이너 상태 확인
- [ ] 디스크 사용량 확인 (80% 미만 유지)
- [ ] 알람 이력 검토
- [ ] 데이터 수집 정상 여부 확인
- [ ] 네트워크 연결 상태 확인

### 8.2 주간 점검 항목

- [ ] 시스템 리소스 추이 분석
- [ ] 미해결 알람 처리
- [ ] 백업 상태 확인
- [ ] 보안 업데이트 확인

### 8.3 월간 점검 항목

- [ ] 데이터 보존 정책 검토
- [ ] 시스템 성능 최적화
- [ ] 백업 복원 테스트
- [ ] 문서 업데이트

---

## 9. 확장 고려사항

### 9.1 수평 확장

```
┌─────────────────────────────────────────────────────────────────────┐
│                        다중 라인 확장 구성                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  라인 1 Edge         라인 2 Edge         라인 3 Edge               │
│  ┌─────────┐         ┌─────────┐         ┌─────────┐               │
│  │  MING   │         │  MING   │         │  MING   │               │
│  │  Stack  │         │  Stack  │         │  Stack  │               │
│  └────┬────┘         └────┬────┘         └────┬────┘               │
│       │                   │                   │                    │
│       └───────────────────┼───────────────────┘                    │
│                           │                                        │
│                           ▼                                        │
│               ┌───────────────────────┐                            │
│               │    중앙 MQTT Broker   │                            │
│               │    (클러스터 구성)     │                            │
│               └───────────────────────┘                            │
│                           │                                        │
│                           ▼                                        │
│               ┌───────────────────────┐                            │
│               │   중앙 InfluxDB/      │                            │
│               │   TimescaleDB         │                            │
│               └───────────────────────┘                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 9.2 클라우드 연동

```javascript
// AWS IoT Core 연동 예시
const awsIot = require('aws-iot-device-sdk');

const device = awsIot.device({
    keyPath: '/path/to/private.pem.key',
    certPath: '/path/to/certificate.pem.crt',
    caPath: '/path/to/AmazonRootCA1.pem',
    clientId: 'ming-edge-gateway',
    host: 'your-endpoint.iot.region.amazonaws.com'
});

device.on('connect', function() {
    device.subscribe('cloud/commands/#');
    device.publish('factory/edge/status', JSON.stringify({
        status: 'online',
        timestamp: new Date().toISOString()
    }));
});
```

---

## 참고 자료

- ISA-95 (Enterprise-Control System Integration)
- IEC 62443 (Industrial Cybersecurity)
- MQTT Sparkplug B Specification
