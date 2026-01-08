# Node-RED 완전 정복 튜토리얼

> 처음 시작하는 분들을 위한 플로우 프로그래밍 기초부터 실전까지

---

## 📚 목차

1. [Node-RED란 무엇인가?](#1-node-red란-무엇인가)
2. [Node-RED 시작하기](#2-node-red-시작하기)
3. [기본 노드 배우기](#3-기본-노드-배우기)
4. [첫 번째 플로우 만들기](#4-첫-번째-플로우-만들기)
5. [Function 노드 마스터](#5-function-노드-마스터)
6. [MQTT 연동하기](#6-mqtt-연동하기)
7. [InfluxDB 연동하기](#7-influxdb-연동하기)
8. [실전 프로젝트](#8-실전-프로젝트)
9. [문제 해결](#9-문제-해결)

---

## 1. Node-RED란 무엇인가?

### 1.1 쉬운 설명

**Node-RED**는 **레고 블록 조립**처럼 프로그래밍하는 도구입니다.

```
일상 비유:
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   🧱 레고 블록 = Node-RED                                │
│                                                         │
│   - 각 블록 = 노드 (기능 하나)                           │
│   - 블록 연결 = 와이어                                   │
│   - 완성품 = 플로우                                      │
│                                                         │
│   [입력블록] ──→ [처리블록] ──→ [출력블록]              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 1.2 무엇을 할 수 있나?

```
┌─────────────────────────────────────────────────────────┐
│  Node-RED로 할 수 있는 것들                              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  📡 데이터 수집                                          │
│     센서 → MQTT → Node-RED → 데이터베이스               │
│                                                         │
│  🔔 알림 보내기                                          │
│     온도 30도 초과 → 이메일/SMS 발송                     │
│                                                         │
│  🔄 데이터 변환                                          │
│     CSV → JSON → 데이터베이스                           │
│                                                         │
│  🤖 자동화                                               │
│     매일 아침 8시 → 보고서 생성                          │
│                                                         │
│  🌐 API 만들기                                           │
│     웹 요청 받아서 처리 후 응답                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 1.3 왜 Node-RED를 사용할까?

| 장점 | 설명 |
|------|------|
| 쉬움 | 드래그 앤 드롭으로 프로그래밍 |
| 빠름 | 몇 분만에 자동화 구현 |
| 시각적 | 데이터 흐름이 눈에 보임 |
| 확장성 | 5000+ 노드 추가 가능 |

---

## 2. Node-RED 시작하기

### 2.1 웹 에디터 접속

```
URL: http://라즈베리파이IP:1880
```

### 2.2 화면 구성

```
┌─────────────────────────────────────────────────────────┐
│  Node-RED                                    배포  ☰    │
├────────────┬──────────────────────────┬─────────────────┤
│            │                          │                 │
│  팔레트    │      작업 영역           │    정보/디버그  │
│            │      (플로우)            │                 │
│  - input   │                          │    ℹ️ 정보     │
│  - output  │   [노드] ──→ [노드]      │    🐛 디버그   │
│  - function│                          │                 │
│  - ...     │                          │                 │
│            │                          │                 │
└────────────┴──────────────────────────┴─────────────────┘
     ①              ②                        ③
```

1. **팔레트**: 사용할 노드들
2. **작업 영역**: 노드 배치 및 연결
3. **사이드바**: 정보, 디버그 메시지

### 2.3 기본 조작법

| 동작 | 방법 |
|------|------|
| 노드 추가 | 팔레트에서 드래그 |
| 노드 연결 | 포트에서 드래그 |
| 노드 설정 | 더블클릭 |
| 노드 삭제 | 선택 후 Delete |
| 배포 | 오른쪽 상단 **배포** 버튼 |

---

## 3. 기본 노드 배우기

### 3.1 입력 노드 (Input)

```
┌──────────────────────────────────────────┐
│  입력 노드 - 데이터가 들어오는 곳        │
├──────────────────────────────────────────┤
│                                          │
│  [inject]     수동/자동 트리거           │
│  [mqtt in]    MQTT 메시지 수신           │
│  [http in]    HTTP 요청 수신             │
│  [tcp in]     TCP 데이터 수신            │
│                                          │
└──────────────────────────────────────────┘
```

### 3.2 출력 노드 (Output)

```
┌──────────────────────────────────────────┐
│  출력 노드 - 데이터가 나가는 곳          │
├──────────────────────────────────────────┤
│                                          │
│  [debug]      디버그 메시지 출력         │
│  [mqtt out]   MQTT 메시지 발행           │
│  [http response] HTTP 응답               │
│                                          │
└──────────────────────────────────────────┘
```

### 3.3 기능 노드 (Function)

```
┌──────────────────────────────────────────┐
│  기능 노드 - 데이터 처리                 │
├──────────────────────────────────────────┤
│                                          │
│  [function]   JavaScript 코드 실행       │
│  [change]     값 변경/삭제/이동          │
│  [switch]     조건 분기                  │
│  [template]   템플릿 적용                │
│  [delay]      지연/속도 제한             │
│                                          │
└──────────────────────────────────────────┘
```

### 3.4 메시지 구조

Node-RED에서 데이터는 **msg** 객체로 전달됩니다:

```javascript
msg = {
    payload: "실제 데이터",      // 가장 중요!
    topic: "주제",               // 선택
    _msgid: "고유ID"             // 자동 생성
}
```

---

## 4. 첫 번째 플로우 만들기

### 4.1 Hello World

**목표**: 버튼 클릭하면 "Hello World" 출력

**단계:**

1. **inject 노드** 드래그 (팔레트 → 작업영역)
2. **debug 노드** 드래그
3. 두 노드 **연결** (inject 출력 → debug 입력)
4. inject 노드 **더블클릭**
   - payload 타입: 문자열
   - 값: `Hello World`
5. **배포** 클릭
6. inject 노드 왼쪽 버튼 **클릭**
7. 오른쪽 **디버그** 탭에서 "Hello World" 확인!

```
[inject: Hello World] ──→ [debug]
```

### 4.2 현재 시간 출력

**목표**: 1초마다 현재 시간 출력

1. inject 노드 설정:
   - payload: 타임스탬프
   - 반복: 1초마다
2. debug 노드 연결
3. 배포

```
[inject: 1초마다] ──→ [debug]

출력: 1705312200000 (유닉스 타임스탬프)
```

### 4.3 타임스탬프를 날짜로 변환

**function 노드** 추가:

```javascript
// 타임스탬프를 읽기 쉬운 날짜로 변환
var date = new Date(msg.payload);
msg.payload = date.toLocaleString('ko-KR');
return msg;
```

```
[inject] ──→ [function] ──→ [debug]

출력: 2024. 1. 15. 오후 2:30:00
```

---

## 5. Function 노드 마스터

### 5.1 기본 문법

```javascript
// msg.payload = 입력 데이터
// return msg = 다음 노드로 전달

// 기본 형태
msg.payload = "새로운 값";
return msg;
```

### 5.2 값 변경하기

```javascript
// 숫자 계산
msg.payload = msg.payload * 2;
return msg;

// 문자열 추가
msg.payload = "온도: " + msg.payload + "°C";
return msg;
```

### 5.3 JSON 다루기

```javascript
// JSON 문자열 → 객체
var data = JSON.parse(msg.payload);
msg.payload = data.temperature;
return msg;

// 객체 → JSON 문자열
var obj = {
    temperature: 25,
    humidity: 60
};
msg.payload = JSON.stringify(obj);
return msg;
```

### 5.4 조건문

```javascript
var temp = msg.payload;

if (temp > 30) {
    msg.payload = "고온 경고!";
} else if (temp < 10) {
    msg.payload = "저온 경고!";
} else {
    msg.payload = "정상";
}

return msg;
```

### 5.5 여러 출력으로 분기

Function 노드 설정에서 출력 수를 2로 변경:

```javascript
var temp = msg.payload;

if (temp > 30) {
    // 첫 번째 출력으로 (경고)
    return [msg, null];
} else {
    // 두 번째 출력으로 (정상)
    return [null, msg];
}
```

```
                    ┌→ [알람 처리]
[입력] → [function] ┤
                    └→ [정상 처리]
```

### 5.6 메시지 여러 개 보내기

```javascript
// 배열의 각 항목을 개별 메시지로
var items = [1, 2, 3, 4, 5];
var messages = [];

for (var i = 0; i < items.length; i++) {
    messages.push({payload: items[i]});
}

return [messages];
```

### 5.7 컨텍스트 (데이터 저장)

```javascript
// 값 저장 (노드 수준)
context.set("count", 0);

// 값 불러오기
var count = context.get("count") || 0;
count++;
context.set("count", count);
msg.payload = count;

return msg;
```

```javascript
// 플로우 수준 (같은 탭의 모든 노드 공유)
flow.set("sharedValue", 100);
var value = flow.get("sharedValue");

// 전역 수준 (모든 플로우 공유)
global.set("globalValue", 200);
var gValue = global.get("globalValue");
```

---

## 6. MQTT 연동하기

### 6.1 MQTT 브로커 설정

1. **mqtt in** 또는 **mqtt out** 노드 추가
2. 노드 더블클릭
3. **서버** 옆 연필 아이콘 클릭
4. 설정 입력:

```
서버: mosquitto (Docker 내부) 또는 localhost
포트: 1883
클라이언트ID: nodered-client

보안 탭:
사용자: mqtt_user
비밀번호: mqtt_pass
```

### 6.2 MQTT 메시지 받기

```
[mqtt in: factory/+/sensor/#] ──→ [debug]

설정:
- 토픽: factory/+/sensor/#
- QoS: 0
- 출력: 자동 감지
```

### 6.3 MQTT 메시지 보내기

```
[inject] ──→ [function] ──→ [mqtt out: factory/line1/control]

Function 노드:
msg.payload = JSON.stringify({
    action: "start",
    speed: 1500
});
return msg;
```

### 6.4 MQTT → 처리 → MQTT

```
[mqtt in] ──→ [function: 데이터 변환] ──→ [mqtt out]

예: 온도 수신 → 화씨 변환 → 재발행
```

```javascript
// 섭씨 → 화씨 변환
var celsius = msg.payload;
var fahrenheit = (celsius * 9/5) + 32;

msg.topic = "factory/line1/temperature_f";
msg.payload = fahrenheit;
return msg;
```

---

## 7. InfluxDB 연동하기

### 7.1 노드 설치

1. 오른쪽 상단 **☰** 클릭
2. **팔레트 관리** 선택
3. **설치** 탭
4. `node-red-contrib-influxdb` 검색
5. **설치** 클릭

### 7.2 InfluxDB 연결 설정

1. **influxdb out** 노드 추가
2. 노드 더블클릭
3. **Server** 옆 연필 아이콘

```
Version: 2.0
URL: http://influxdb:8086
Token: ming-super-secret-token
Organization: ming-org
Default Bucket: factory
```

### 7.3 데이터 저장하기

```
[mqtt in] ──→ [function] ──→ [influxdb out]
```

**Function 노드:**
```javascript
// MQTT JSON 메시지를 InfluxDB 형식으로 변환
var data = JSON.parse(msg.payload);

msg.payload = [{
    measurement: "sensor_data",
    tags: {
        location: "factory1",
        line: msg.topic.split("/")[1]  // 토픽에서 추출
    },
    fields: {
        temperature: data.temperature,
        humidity: data.humidity
    }
}];

return msg;
```

### 7.4 데이터 조회하기

```
[inject] ──→ [influxdb in] ──→ [debug]
```

**influxdb in 노드 쿼리:**
```flux
from(bucket: "factory")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "sensor_data")
  |> filter(fn: (r) => r._field == "temperature")
  |> last()
```

---

## 8. 실전 프로젝트

### 8.1 프로젝트: 센서 데이터 수집 시스템

**목표:** MQTT로 센서 데이터 받아서 InfluxDB에 저장

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  [mqtt in] ──→ [JSON 파싱] ──→ [InfluxDB 변환] ──→ [influxdb out]
│      │                                                  │
│      └──→ [debug]                                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**플로우 JSON (가져오기용):**
```json
[
    {
        "id": "mqtt-in",
        "type": "mqtt in",
        "topic": "factory/+/sensor/data",
        "qos": "0",
        "name": "센서 데이터 수신"
    },
    {
        "id": "json-parse",
        "type": "json",
        "name": "JSON 파싱"
    },
    {
        "id": "influx-convert",
        "type": "function",
        "name": "InfluxDB 변환",
        "func": "var parts = msg.topic.split('/');\nmsg.payload = [{\n    measurement: 'sensor_data',\n    tags: {\n        location: parts[0],\n        line: parts[1]\n    },\n    fields: msg.payload\n}];\nreturn msg;"
    },
    {
        "id": "influxdb-out",
        "type": "influxdb out",
        "name": "InfluxDB 저장"
    }
]
```

### 8.2 프로젝트: 온도 알람 시스템

**목표:** 온도 30도 초과 시 알람 발생

```
[mqtt in] ──→ [JSON] ──→ [switch: temp > 30] ──→ [알람 처리] ──→ [mqtt out]
                              │
                              └──→ [정상 처리]
```

**Switch 노드 설정:**
```
속성: msg.payload.temperature
규칙 1: > 30 (고온)
규칙 2: otherwise (정상)
```

**알람 Function 노드:**
```javascript
msg.topic = "factory/alarms/temperature";
msg.payload = {
    type: "HIGH_TEMPERATURE",
    value: msg.payload.temperature,
    threshold: 30,
    timestamp: new Date().toISOString(),
    severity: "WARNING"
};
msg.payload = JSON.stringify(msg.payload);
return msg;
```

### 8.3 프로젝트: 1분 평균 계산

**목표:** 1분 동안의 평균 온도 계산

```
[mqtt in] ──→ [function: 누적] ──→ [trigger: 1분] ──→ [function: 평균] ──→ [debug]
```

**누적 Function:**
```javascript
// 컨텍스트에서 배열 가져오기
var temps = context.get("temps") || [];

// 새 값 추가
temps.push(msg.payload.temperature);

// 저장
context.set("temps", temps);

return null;  // 다음으로 안 보냄
```

**평균 계산 Function:**
```javascript
var temps = context.get("temps") || [];

if (temps.length > 0) {
    var sum = temps.reduce((a, b) => a + b, 0);
    var avg = sum / temps.length;

    msg.payload = {
        average: avg.toFixed(2),
        count: temps.length,
        timestamp: new Date().toISOString()
    };

    // 배열 초기화
    context.set("temps", []);

    return msg;
}

return null;
```

### 8.4 프로젝트: REST API 만들기

**목표:** HTTP로 현재 센서 값 조회

```
[http in: GET /api/sensors] ──→ [influxdb in] ──→ [function] ──→ [http response]
```

**HTTP In 설정:**
```
Method: GET
URL: /api/sensors
```

**Function (응답 형식):**
```javascript
msg.payload = {
    status: "success",
    data: msg.payload,
    timestamp: new Date().toISOString()
};
return msg;
```

**테스트:**
```bash
curl http://라즈베리파이IP:1880/api/sensors
```

---

## 9. 문제 해결

### 9.1 배포 실패

```
오류: "flows contain errors"

해결:
1. 모든 노드의 연결 확인
2. 빨간 삼각형 있는 노드 확인
3. 필수 설정 누락 확인
```

### 9.2 MQTT 연결 안 됨

```
오류: "connection refused"

해결:
1. 브로커 주소 확인 (Docker: mosquitto, 외부: IP)
2. 포트 확인 (1883)
3. 인증 정보 확인
```

### 9.3 Function 노드 에러

```javascript
// 디버그 방법
node.warn("변수값: " + myVariable);
node.error("에러 발생!", msg);

// 타입 확인
node.warn("타입: " + typeof msg.payload);
```

### 9.4 메시지가 안 흘러감

```
확인사항:
1. 배포했는지 확인
2. 와이어 연결 확인
3. Function에서 return msg; 확인
4. 조건문에서 null 반환하는지 확인
```

### 9.5 유용한 디버그 팁

```
1. debug 노드를 중간에 여러 개 배치
2. "전체 msg 객체" 출력으로 설정
3. node.warn()으로 로그 출력
```

---

## 📝 핵심 요약

| 개념 | 설명 |
|------|------|
| 노드 | 하나의 기능 블록 |
| 와이어 | 노드 간 연결 |
| 플로우 | 노드+와이어의 집합 |
| msg | 노드 간 전달되는 데이터 |
| msg.payload | 실제 데이터 |
| 배포 | 변경사항 적용 |

### 자주 쓰는 노드

| 노드 | 용도 |
|------|------|
| inject | 수동/자동 트리거 |
| debug | 디버그 출력 |
| function | JavaScript 코드 |
| change | 값 변경 |
| switch | 조건 분기 |
| mqtt in/out | MQTT 통신 |
| http in/response | REST API |
| influxdb in/out | DB 연동 |

---

## 다음 단계

- [Grafana 튜토리얼](./04-grafana-tutorial.md) - 대시보드 만들기
