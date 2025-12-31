# MQTT 토픽 구조 설계 가이드

> 산업현장 IoT를 위한 체계적인 MQTT 토픽 네이밍 컨벤션

---

## 1. MQTT 토픽 설계 원칙

### 1.1 계층적 구조

산업현장에서는 물리적 위치와 논리적 구조를 반영한 계층적 토픽 구조가 필수적입니다.

```
{company}/{site}/{area}/{line}/{device}/{data_type}
```

### 1.2 설계 원칙

| 원칙 | 설명 | 예시 |
|------|------|------|
| **계층성** | 물리적/논리적 구조 반영 | `factory/building_a/line1/...` |
| **일관성** | 동일한 패턴 유지 | 모든 디바이스에 동일 구조 적용 |
| **확장성** | 미래 확장 고려 | 와일드카드 사용 가능한 구조 |
| **명확성** | 의미가 분명한 네이밍 | `temperature` vs `temp` |
| **소문자** | 대소문자 구분 방지 | `factory` (O), `Factory` (X) |

---

## 2. 산업현장 표준 토픽 구조

### 2.1 기본 토픽 템플릿

```
{namespace}/{site}/{area}/{line}/{device}/{message_type}

예시:
factory/seoul_plant/production/line1/plc_001/data
factory/seoul_plant/production/line1/plc_001/status
factory/seoul_plant/production/line1/plc_001/control
factory/seoul_plant/production/line1/plc_001/config
```

### 2.2 계층별 설명

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MQTT 토픽 계층 구조                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  factory/                    <- 네임스페이스 (조직/시스템)            │
│  ├── seoul_plant/            <- 사이트 (물리적 위치)                 │
│  │   ├── production/         <- 영역 (기능적 구분)                   │
│  │   │   ├── line1/          <- 라인 (세부 영역)                     │
│  │   │   │   ├── plc_001/    <- 디바이스 (장비 ID)                  │
│  │   │   │   │   ├── data    <- 센서 데이터                         │
│  │   │   │   │   ├── status  <- 장비 상태                           │
│  │   │   │   │   ├── control <- 제어 명령                           │
│  │   │   │   │   ├── config  <- 설정 변경                           │
│  │   │   │   │   └── alarm   <- 알람/경고                           │
│  │   │   │   └── sensor_002/ │                                      │
│  │   │   └── line2/          │                                      │
│  │   └── utility/            <- 유틸리티 (전기, 공조 등)             │
│  └── busan_plant/            <- 다른 사이트                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. 메시지 타입별 토픽 구조

### 3.1 데이터 수집 (Telemetry)

```
# 센서 데이터 발행
factory/{site}/{area}/{line}/{device}/data

# 페이로드 예시
{
    "timestamp": "2024-01-15T10:30:00.000Z",
    "temperature": 25.5,
    "humidity": 60.2,
    "pressure": 1.02,
    "motor_speed": 1500
}
```

### 3.2 상태 정보 (Status)

```
# 장비 상태 발행
factory/{site}/{area}/{line}/{device}/status

# 페이로드 예시
{
    "timestamp": "2024-01-15T10:30:00.000Z",
    "state": "running",        # running, stopped, error, maintenance
    "uptime": 86400,           # 초
    "last_error": null,
    "connection": "online"
}
```

### 3.3 제어 명령 (Control)

```
# 제어 명령 수신 (디바이스가 구독)
factory/{site}/{area}/{line}/{device}/control

# 페이로드 예시
{
    "command": "set_speed",
    "parameters": {
        "target_speed": 1800,
        "ramp_time": 10
    },
    "request_id": "cmd-12345",
    "timestamp": "2024-01-15T10:30:00.000Z"
}

# 제어 응답 (디바이스가 발행)
factory/{site}/{area}/{line}/{device}/control/response

# 페이로드 예시
{
    "request_id": "cmd-12345",
    "status": "success",       # success, error, pending
    "message": "Speed changed to 1800 RPM",
    "timestamp": "2024-01-15T10:30:01.000Z"
}
```

### 3.4 알람/경고 (Alarm)

```
# 알람 발행
factory/{site}/{area}/{line}/{device}/alarm

# 페이로드 예시
{
    "alarm_id": "ALM-001",
    "severity": "critical",    # info, warning, critical, emergency
    "type": "temperature_high",
    "message": "Temperature exceeded 40°C",
    "value": 42.5,
    "threshold": 40.0,
    "acknowledged": false,
    "timestamp": "2024-01-15T10:30:00.000Z"
}

# 알람 집계 토픽
factory/{site}/alarms/active    <- 활성 알람 목록
factory/{site}/alarms/history   <- 알람 이력
```

### 3.5 설정 (Configuration)

```
# 설정 변경 명령
factory/{site}/{area}/{line}/{device}/config

# 페이로드 예시
{
    "config_type": "sampling_rate",
    "value": 5000,             # ms
    "apply_immediately": true
}

# 현재 설정 조회
factory/{site}/{area}/{line}/{device}/config/current
```

---

## 4. 와일드카드 활용

### 4.1 단일 레벨 와일드카드 (+)

```bash
# 특정 라인의 모든 디바이스 데이터
factory/seoul_plant/production/line1/+/data

# 모든 라인의 특정 디바이스 타입 데이터
factory/seoul_plant/production/+/plc_001/data
```

### 4.2 다중 레벨 와일드카드 (#)

```bash
# 특정 디바이스의 모든 토픽
factory/seoul_plant/production/line1/plc_001/#

# 전체 공장의 모든 데이터
factory/seoul_plant/#

# 모든 알람 수신
factory/+/+/+/+/alarm
```

---

## 5. 산업현장 구성 예제

### 5.1 스마트 팩토리 구성

```
┌─────────────────────────────────────────────────────────────────────┐
│                    스마트 팩토리 MQTT 토픽 맵                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  factory/                                                           │
│  ├── plant_a/                                                       │
│  │   ├── production/                                                │
│  │   │   ├── assembly_line1/                                        │
│  │   │   │   ├── robot_arm_001/                                     │
│  │   │   │   │   ├── data          <- 위치, 속도, 토크               │
│  │   │   │   │   ├── status        <- 운전 상태                      │
│  │   │   │   │   ├── control       <- 동작 명령                      │
│  │   │   │   │   └── alarm         <- 이상 알람                      │
│  │   │   │   ├── conveyor_001/                                      │
│  │   │   │   │   ├── data          <- 속도, 물품 카운트              │
│  │   │   │   │   ├── status        <- 동작 상태                      │
│  │   │   │   │   └── control       <- 속도 제어                      │
│  │   │   │   └── vision_001/                                        │
│  │   │   │       ├── data          <- 불량 감지 데이터               │
│  │   │   │       └── status        <- 카메라 상태                    │
│  │   │   │                                                          │
│  │   │   └── packaging_line1/                                       │
│  │   │       ├── packer_001/                                        │
│  │   │       └── labeler_001/                                       │
│  │   │                                                              │
│  │   ├── utility/                                                   │
│  │   │   ├── hvac/                                                  │
│  │   │   │   ├── ahu_001/          <- 공조기                         │
│  │   │   │   └── chiller_001/      <- 냉동기                         │
│  │   │   ├── electrical/                                            │
│  │   │   │   ├── transformer_001/  <- 변압기                         │
│  │   │   │   └── pdu_001/          <- 전력분배장치                    │
│  │   │   └── compressed_air/                                        │
│  │   │       └── compressor_001/   <- 공기압축기                      │
│  │   │                                                              │
│  │   └── quality/                                                   │
│  │       └── inspection/                                            │
│  │           ├── xray_001/         <- X-ray 검사기                   │
│  │           └── scale_001/        <- 중량 계측기                     │
│  │                                                                  │
│  └── warehouse/                                                     │
│      ├── storage/                                                   │
│      │   ├── zone_a/                                                │
│      │   └── zone_b/                                                │
│      └── shipping/                                                  │
│          └── dock_001/                                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.2 페이로드 표준 구조

```json
// 센서 데이터 표준 페이로드
{
    "device_id": "robot_arm_001",
    "timestamp": "2024-01-15T10:30:00.000Z",
    "sequence": 12345,
    "data": {
        "joint_positions": [0, 45, 90, 0, -45, 0],
        "joint_speeds": [10, 20, 15, 5, 10, 8],
        "joint_torques": [50, 80, 60, 30, 40, 20],
        "tcp_position": {"x": 500, "y": 200, "z": 300},
        "tcp_orientation": {"rx": 0, "ry": 180, "rz": 0}
    },
    "quality": {
        "rssi": -45,
        "latency_ms": 5
    }
}
```

---

## 6. QoS 및 Retain 정책

### 6.1 메시지 타입별 QoS 권장 설정

| 메시지 타입 | QoS | Retain | 설명 |
|------------|-----|--------|------|
| 센서 데이터 (고빈도) | 0 | No | 주기적 데이터, 손실 허용 |
| 센서 데이터 (저빈도) | 1 | No | 중요 데이터 |
| 상태 정보 | 1 | Yes | 최신 상태 유지 |
| 제어 명령 | 2 | No | 정확히 1회 전달 필수 |
| 알람 | 1 | No | 손실 방지 |
| 설정 | 2 | Yes | 최신 설정 유지 |

### 6.2 Retain 메시지 활용

```bash
# 장비 상태는 Retain으로 발행
# 새 구독자가 즉시 최신 상태 확인 가능

mosquitto_pub -t "factory/line1/plc_001/status" \
    -m '{"state":"running","uptime":86400}' \
    -r  # retain flag
```

---

## 7. 보안 고려사항

### 7.1 토픽 기반 ACL (Access Control List)

```
# 관리자: 모든 접근
user admin
topic readwrite #

# 센서 디바이스: 자신의 토픽만 쓰기
user sensor_device_001
topic write factory/+/+/+/sensor_device_001/data
topic write factory/+/+/+/sensor_device_001/status
topic read factory/+/+/+/sensor_device_001/control
topic read factory/+/+/+/sensor_device_001/config

# 모니터링 시스템: 읽기 전용
user monitoring
topic read factory/#

# 제어 시스템: 특정 토픽 읽기/쓰기
user control_system
topic read factory/+/+/+/+/data
topic read factory/+/+/+/+/status
topic write factory/+/+/+/+/control
```

### 7.2 네트워크 분리

```
┌─────────────────────────────────────────────────────────────────┐
│                     네트워크 분리 구성                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────┐     ┌───────────────┐     ┌───────────────┐ │
│  │  OT Network   │     │  DMZ Network  │     │  IT Network   │ │
│  │  (생산망)      │────▶│  (중계망)      │────▶│  (업무망)      │ │
│  │               │     │               │     │               │ │
│  │  - PLC        │     │  - MQTT       │     │  - Grafana    │ │
│  │  - Sensor     │     │    Bridge     │     │  - InfluxDB   │ │
│  │  - Edge GW    │     │  - Firewall   │     │  - Node-RED   │ │
│  └───────────────┘     └───────────────┘     └───────────────┘ │
│                                                                 │
│  포트 1883              포트 8883 (TLS)        포트 8086, 3000  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. 모범 사례

### 8.1 DO (권장사항)

- 소문자와 언더스코어 사용: `production_line1`
- 의미 있는 디바이스 ID: `temp_sensor_room101`
- 타임스탬프 ISO 8601 형식: `2024-01-15T10:30:00.000Z`
- JSON 페이로드 사용
- 버전 관리 고려: `v1/factory/...`

### 8.2 DON'T (지양사항)

- 공백 사용 금지: `line 1` (X)
- 특수문자 지양: `line#1` (X)
- 토픽에 타임스탬프 포함 금지: `factory/2024/01/15/...` (X)
- 너무 깊은 계층 지양 (6레벨 이하 권장)
- 민감 정보 토픽명에 포함 금지

### 8.3 네이밍 컨벤션

```
# 좋은 예시
factory/plant_a/production/line1/robot_arm_001/data
factory/plant_a/utility/hvac/ahu_001/status

# 나쁜 예시
Factory/Plant A/Production/Line 1/Robot Arm 001/Data  # 공백, 대문자
fac/pa/prod/l1/ra001/d                                # 너무 축약
factory/plant_a/production/line1/robot_arm_001/joint1/position/current/value  # 너무 깊음
```

---

## 9. 구현 체크리스트

- [ ] 토픽 네이밍 컨벤션 정의
- [ ] 계층 구조 설계
- [ ] 메시지 타입별 페이로드 스키마 정의
- [ ] QoS 및 Retain 정책 수립
- [ ] ACL 규칙 설정
- [ ] 와일드카드 구독 패턴 정의
- [ ] 문서화 및 팀 공유

---

## 참고 자료

- [MQTT 5.0 Specification](https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html)
- [Sparkplug B Specification](https://www.eclipse.org/tahu/spec/Sparkplug%20Topic%20Namespace%20and%20State%20ManagementV2.2-with%20errata.pdf)
- [Eclipse Mosquitto Documentation](https://mosquitto.org/documentation/)
