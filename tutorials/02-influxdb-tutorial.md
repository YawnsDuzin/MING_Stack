# InfluxDB 완전 정복 튜토리얼

> 처음 시작하는 분들을 위한 시계열 데이터베이스 기초부터 실전까지

---

## 📚 목차

1. [InfluxDB란 무엇인가?](#1-influxdb란-무엇인가)
2. [핵심 개념 이해하기](#2-핵심-개념-이해하기)
3. [InfluxDB 시작하기](#3-influxdb-시작하기)
4. [데이터 쓰기](#4-데이터-쓰기)
5. [데이터 조회하기 (Flux)](#5-데이터-조회하기-flux)
6. [실전 쿼리 예제](#6-실전-쿼리-예제)
7. [데이터 관리](#7-데이터-관리)
8. [Node-RED 연동](#8-node-red-연동)
9. [문제 해결](#9-문제-해결)

---

## 1. InfluxDB란 무엇인가?

### 1.1 쉬운 설명

**InfluxDB**는 **시간이 찍힌 데이터**를 저장하는 특별한 데이터베이스입니다.

```
일상 비유:
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   📊 체중 기록 앱 = InfluxDB                             │
│                                                         │
│   - 날짜/시간 = 타임스탬프                               │
│   - 체중 값 = 필드                                      │
│   - 사람 이름 = 태그                                    │
│   - "체중 기록" = 측정값(Measurement)                   │
│                                                         │
│   2024-01-01 08:00  홍길동  72.5kg                      │
│   2024-01-02 08:00  홍길동  72.3kg                      │
│   2024-01-01 08:00  김철수  68.0kg                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 1.2 왜 InfluxDB를 사용할까?

| 비교 | MySQL/PostgreSQL | InfluxDB |
|------|------------------|----------|
| 용도 | 일반 데이터 | 시계열 데이터 |
| 쓰기 속도 | 보통 | 매우 빠름 |
| 시간 쿼리 | 복잡 | 간단 |
| 자동 삭제 | 수동 | 자동 (Retention) |
| 집계 함수 | 기본 | 시계열 특화 |

### 1.3 어디에 사용할까?

- 📈 센서 데이터 (온도, 습도, 압력)
- 📊 서버 모니터링 (CPU, 메모리)
- 💰 주식/금융 데이터
- 🏭 공장 설비 상태

---

## 2. 핵심 개념 이해하기

### 2.1 데이터 구조

```
┌─────────────────────────────────────────────────────────┐
│              InfluxDB 데이터 구조                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   Bucket (버킷) = 데이터베이스                           │
│     └── Measurement (측정값) = 테이블                   │
│           ├── Timestamp (시간) = 필수!                  │
│           ├── Tags (태그) = 인덱스, 문자열만            │
│           └── Fields (필드) = 실제 값                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2.2 실제 데이터 예시

```
측정값: sensor_data
시간: 2024-01-15T10:30:00Z

┌──────────────────────────────────────────────────────┐
│ 태그 (검색용, 인덱스)         │ 필드 (실제 값)        │
├──────────────────────────────┼───────────────────────┤
│ location = "factory1"        │ temperature = 25.5    │
│ line = "line1"               │ humidity = 60.2       │
│ sensor_id = "sensor001"      │ pressure = 1.013      │
└──────────────────────────────┴───────────────────────┘
```

### 2.3 태그 vs 필드

| 구분 | 태그 (Tag) | 필드 (Field) |
|------|-----------|--------------|
| 용도 | 분류/검색 | 실제 데이터 |
| 타입 | 문자열만 | 숫자, 문자열, 불린 |
| 인덱스 | ✓ (빠른 검색) | ✗ |
| 예시 | 위치, 장비ID | 온도, 습도 |

**쉬운 구분법:**
- "이 값으로 검색할까?" → 태그
- "이 값을 계산할까?" → 필드

### 2.4 Line Protocol (데이터 형식)

```
측정값,태그1=값1,태그2=값2 필드1=값1,필드2=값2 타임스탬프

예시:
sensor_data,location=factory1,line=line1 temperature=25.5,humidity=60 1705312200000000000
```

---

## 3. InfluxDB 시작하기

### 3.1 웹 UI 접속

```
URL: http://라즈베리파이IP:8086
사용자: admin
비밀번호: admin123456 (기본값)
조직: ming-org
버킷: factory
```

### 3.2 웹 UI 둘러보기

```
┌─────────────────────────────────────────────────────────┐
│  InfluxDB                                               │
├──────────────┬──────────────────────────────────────────┤
│              │                                          │
│  📊 Explore  │  ← 데이터 조회 (가장 많이 사용)          │
│              │                                          │
│  📝 Boards   │  ← 대시보드                              │
│              │                                          │
│  ⚡ Load Data│  ← 데이터 입력                           │
│              │                                          │
│  ⚙️ Settings │  ← 설정                                  │
│              │                                          │
└──────────────┴──────────────────────────────────────────┘
```

### 3.3 API 토큰 확인

```
웹 UI → Load Data → API Tokens → ming-super-secret-token
```

또는 환경변수에서:
```bash
echo $INFLUXDB_TOKEN
# ming-super-secret-token
```

---

## 4. 데이터 쓰기

### 4.1 웹 UI에서 직접 쓰기

1. **Load Data** 클릭
2. **Line Protocol** 선택
3. 데이터 입력:
```
sensor_data,location=factory1,line=line1 temperature=25.5,humidity=60
```
4. **Write Data** 클릭

### 4.2 curl로 데이터 쓰기

```bash
# 단일 데이터 포인트
curl -X POST "http://localhost:8086/api/v2/write?org=ming-org&bucket=factory" \
  -H "Authorization: Token ming-super-secret-token" \
  -H "Content-Type: text/plain" \
  -d "sensor_data,location=factory1,line=line1 temperature=25.5,humidity=60"
```

### 4.3 여러 데이터 한 번에 쓰기

```bash
curl -X POST "http://localhost:8086/api/v2/write?org=ming-org&bucket=factory" \
  -H "Authorization: Token ming-super-secret-token" \
  -H "Content-Type: text/plain" \
  -d "sensor_data,location=factory1,line=line1 temperature=25.5,humidity=60
sensor_data,location=factory1,line=line2 temperature=26.0,humidity=58
sensor_data,location=factory1,line=line3 temperature=24.8,humidity=62"
```

### 4.4 Python으로 데이터 쓰기

```python
# pip install influxdb-client

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import time

# 연결 설정
client = InfluxDBClient(
    url="http://localhost:8086",
    token="ming-super-secret-token",
    org="ming-org"
)

# 쓰기 API
write_api = client.write_api(write_options=SYNCHRONOUS)

# 데이터 포인트 생성
point = Point("sensor_data") \
    .tag("location", "factory1") \
    .tag("line", "line1") \
    .field("temperature", 25.5) \
    .field("humidity", 60.0)

# 데이터 쓰기
write_api.write(bucket="factory", record=point)
print("데이터 저장 완료!")

# 연속 데이터 쓰기
while True:
    point = Point("sensor_data") \
        .tag("location", "factory1") \
        .tag("line", "line1") \
        .field("temperature", 25.0 + (time.time() % 10) / 10) \
        .field("humidity", 60.0)

    write_api.write(bucket="factory", record=point)
    print(f"저장: temp={point._fields['temperature']}")
    time.sleep(5)
```

---

## 5. 데이터 조회하기 (Flux)

### 5.1 Flux란?

**Flux**는 InfluxDB의 쿼리 언어입니다. SQL과 다르게 **파이프라인** 방식으로 작동합니다.

```
데이터소스 → 필터 → 변환 → 집계 → 결과
    |          |        |       |       |
  from()  → filter() → map() → mean() → yield()
```

### 5.2 기본 쿼리 구조

```flux
from(bucket: "factory")           // 1. 버킷 선택
  |> range(start: -1h)            // 2. 시간 범위
  |> filter(fn: (r) => r._measurement == "sensor_data")  // 3. 필터
  |> filter(fn: (r) => r._field == "temperature")        // 4. 필드 선택
```

### 5.3 웹 UI에서 쿼리 실행

1. **Explore** 클릭
2. **Script Editor** 클릭 (오른쪽 상단)
3. 쿼리 입력
4. **Submit** 클릭

### 5.4 시간 범위 지정

```flux
// 최근 1시간
|> range(start: -1h)

// 최근 24시간
|> range(start: -24h)

// 최근 7일
|> range(start: -7d)

// 특정 기간
|> range(start: 2024-01-01T00:00:00Z, stop: 2024-01-02T00:00:00Z)

// 최근 30분
|> range(start: -30m)
```

### 5.5 필터링

```flux
// 측정값 필터
|> filter(fn: (r) => r._measurement == "sensor_data")

// 태그 필터
|> filter(fn: (r) => r.location == "factory1")
|> filter(fn: (r) => r.line == "line1")

// 필드 필터
|> filter(fn: (r) => r._field == "temperature")

// 조건 조합
|> filter(fn: (r) =>
    r._measurement == "sensor_data" and
    r.location == "factory1" and
    r._field == "temperature"
)
```

---

## 6. 실전 쿼리 예제

### 6.1 최근 온도 데이터 조회

```flux
from(bucket: "factory")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "sensor_data")
  |> filter(fn: (r) => r._field == "temperature")
```

### 6.2 평균 온도 계산

```flux
from(bucket: "factory")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "sensor_data")
  |> filter(fn: (r) => r._field == "temperature")
  |> mean()
```

### 6.3 5분 단위 평균

```flux
from(bucket: "factory")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "sensor_data")
  |> filter(fn: (r) => r._field == "temperature")
  |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
```

### 6.4 최대/최소값 찾기

```flux
// 최대값
from(bucket: "factory")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "sensor_data")
  |> filter(fn: (r) => r._field == "temperature")
  |> max()

// 최소값
from(bucket: "factory")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "sensor_data")
  |> filter(fn: (r) => r._field == "temperature")
  |> min()
```

### 6.5 라인별 평균 온도 비교

```flux
from(bucket: "factory")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "sensor_data")
  |> filter(fn: (r) => r._field == "temperature")
  |> group(columns: ["line"])
  |> mean()
```

### 6.6 임계값 초과 데이터 찾기

```flux
from(bucket: "factory")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "sensor_data")
  |> filter(fn: (r) => r._field == "temperature")
  |> filter(fn: (r) => r._value > 30)  // 30도 초과
```

### 6.7 마지막 값 조회

```flux
from(bucket: "factory")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "sensor_data")
  |> filter(fn: (r) => r._field == "temperature")
  |> last()
```

### 6.8 여러 필드 함께 조회

```flux
from(bucket: "factory")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "sensor_data")
  |> filter(fn: (r) => r._field == "temperature" or r._field == "humidity")
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
```

---

## 7. 데이터 관리

### 7.1 데이터 보존 정책 (Retention)

```bash
# 현재 버킷 정보 확인
curl -X GET "http://localhost:8086/api/v2/buckets" \
  -H "Authorization: Token ming-super-secret-token" | jq
```

웹 UI에서:
1. **Settings** → **Buckets**
2. 버킷 선택 → **Edit**
3. **Delete Data** → Retention Period 설정

### 7.2 데이터 삭제

```bash
# 특정 시간 범위 데이터 삭제
curl -X POST "http://localhost:8086/api/v2/delete?org=ming-org&bucket=factory" \
  -H "Authorization: Token ming-super-secret-token" \
  -H "Content-Type: application/json" \
  -d '{
    "start": "2024-01-01T00:00:00Z",
    "stop": "2024-01-02T00:00:00Z",
    "predicate": "_measurement=\"sensor_data\""
  }'
```

### 7.3 버킷 생성

웹 UI에서:
1. **Load Data** → **Buckets**
2. **Create Bucket**
3. 이름, 보존 기간 설정

```bash
# CLI로 버킷 생성
curl -X POST "http://localhost:8086/api/v2/buckets" \
  -H "Authorization: Token ming-super-secret-token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "new_bucket",
    "orgID": "YOUR_ORG_ID",
    "retentionRules": [{"everySeconds": 604800}]
  }'
```

---

## 8. Node-RED 연동

### 8.1 InfluxDB 노드 설치

Node-RED 팔레트에서:
- `node-red-contrib-influxdb`

### 8.2 InfluxDB 연결 설정

```
Version: 2.0
URL: http://influxdb:8086
Token: ming-super-secret-token
Organization: ming-org
Bucket: factory
```

### 8.3 데이터 쓰기 플로우

```
[MQTT In] → [Function: 데이터 변환] → [InfluxDB Out]
```

**Function 노드:**
```javascript
// MQTT 메시지를 InfluxDB 형식으로 변환
var data = JSON.parse(msg.payload);

msg.payload = [{
    measurement: "sensor_data",
    tags: {
        location: "factory1",
        line: "line1"
    },
    fields: {
        temperature: data.temperature,
        humidity: data.humidity
    }
}];

return msg;
```

### 8.4 데이터 읽기 플로우

```
[Inject] → [InfluxDB In] → [Function: 처리] → [Debug]
```

**InfluxDB In 노드 쿼리:**
```flux
from(bucket: "factory")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "sensor_data")
  |> filter(fn: (r) => r._field == "temperature")
  |> last()
```

---

## 9. 문제 해결

### 9.1 연결 안 됨

```bash
# 1. 컨테이너 상태 확인
docker ps | grep influxdb

# 2. 헬스 체크
curl http://localhost:8086/health

# 3. 로그 확인
docker logs ming-influxdb
```

### 9.2 인증 실패

```bash
# 에러: unauthorized

# 확인사항:
# 1. 토큰 정확한지 확인
# 2. 조직(org) 이름 확인
# 3. 버킷 이름 확인
```

### 9.3 데이터가 안 보임

```flux
// 시간 범위 확대해서 확인
from(bucket: "factory")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "sensor_data")
  |> limit(n: 10)
```

### 9.4 쿼리 성능 최적화

```flux
// 좋은 예: 필터를 먼저
from(bucket: "factory")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "sensor_data")
  |> filter(fn: (r) => r.location == "factory1")

// 나쁜 예: 모든 데이터 가져온 후 필터
from(bucket: "factory")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "sensor_data")
  // 너무 많은 데이터!
```

---

## 📝 핵심 요약

| 개념 | 설명 |
|------|------|
| InfluxDB | 시계열 데이터 전용 데이터베이스 |
| Bucket | 데이터베이스 (데이터 저장소) |
| Measurement | 테이블 (데이터 분류) |
| Tag | 인덱스 (검색용, 문자열) |
| Field | 실제 값 (숫자, 문자열) |
| Flux | 쿼리 언어 |
| Retention | 데이터 보존 기간 |

### 자주 쓰는 Flux 함수

| 함수 | 설명 |
|------|------|
| `from()` | 버킷 선택 |
| `range()` | 시간 범위 |
| `filter()` | 데이터 필터링 |
| `mean()` | 평균 |
| `sum()` | 합계 |
| `max()`, `min()` | 최대/최소 |
| `last()` | 마지막 값 |
| `aggregateWindow()` | 시간 단위 집계 |
| `group()` | 그룹화 |
| `pivot()` | 행/열 변환 |

---

## 다음 단계

- [Node-RED 튜토리얼](./03-nodered-tutorial.md) - 데이터 처리 자동화
- [Grafana 튜토리얼](./04-grafana-tutorial.md) - 대시보드 만들기
