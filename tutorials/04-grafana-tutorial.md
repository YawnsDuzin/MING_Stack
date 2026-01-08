# Grafana 완전 정복 튜토리얼

> 처음 시작하는 분들을 위한 데이터 시각화 기초부터 실전까지

---

## 📚 목차

1. [Grafana란 무엇인가?](#1-grafana란-무엇인가)
2. [Grafana 시작하기](#2-grafana-시작하기)
3. [데이터소스 연결](#3-데이터소스-연결)
4. [첫 번째 대시보드](#4-첫-번째-대시보드)
5. [패널 유형 마스터](#5-패널-유형-마스터)
6. [쿼리 작성하기](#6-쿼리-작성하기)
7. [알림 설정](#7-알림-설정)
8. [실전 대시보드](#8-실전-대시보드)
9. [문제 해결](#9-문제-해결)

---

## 1. Grafana란 무엇인가?

### 1.1 쉬운 설명

**Grafana**는 **데이터를 그림으로 보여주는 도구**입니다.

```
일상 비유:
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   📊 엑셀 차트 vs Grafana                                │
│                                                         │
│   엑셀: 데이터 직접 입력 → 차트                          │
│   Grafana: DB 연결 → 실시간 차트 자동 갱신               │
│                                                         │
│   마치 자동으로 업데이트되는 TV 뉴스 그래프!             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Grafana로 만들 수 있는 것

```
┌─────────────────────────────────────────────────────────┐
│                    대시보드 예시                         │
├──────────────────────┬──────────────────────────────────┤
│                      │                                  │
│   📈 실시간 온도     │   🔢 현재값                      │
│   ┌────────────┐    │   ┌──────────┐                   │
│   │    /\  /\  │    │   │   25.5   │°C                 │
│   │   /  \/  \ │    │   └──────────┘                   │
│   └────────────┘    │                                  │
│                      │   ⚡ 상태 표시                    │
│   📊 일일 생산량     │   ┌──────────┐                   │
│   ┌────────────┐    │   │  정상 ✓  │                   │
│   │ ▓▓▓▓░░░░░░ │    │   └──────────┘                   │
│   └────────────┘    │                                  │
│                      │                                  │
└──────────────────────┴──────────────────────────────────┘
```

### 1.3 왜 Grafana를 사용할까?

| 장점 | 설명 |
|------|------|
| 실시간 | 데이터가 자동으로 갱신됨 |
| 다양한 차트 | 20+ 시각화 유형 |
| 알림 | 조건 충족 시 알림 발송 |
| 공유 | URL로 대시보드 공유 |
| 무료 | 오픈소스 (무료) |

---

## 2. Grafana 시작하기

### 2.1 접속하기

```
URL: http://라즈베리파이IP:3000

첫 로그인:
사용자: admin
비밀번호: admin123 (기본값)
```

### 2.2 화면 구성

```
┌─────────────────────────────────────────────────────────┐
│  ☰ Grafana                              🔔  👤 admin   │
├────────────────────────────────────────────────────────┤
│                                                         │
│  ← 사이드 메뉴                                          │
│                                                         │
│  🏠 Home                                                │
│  📊 Dashboards    ← 대시보드 목록                       │
│  🔌 Connections   ← 데이터소스 연결                     │
│  🔔 Alerting      ← 알림 설정                           │
│  ⚙️ Administration← 관리자 설정                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2.3 중요 용어

| 용어 | 설명 |
|------|------|
| 대시보드 | 여러 패널을 모아놓은 화면 |
| 패널 | 하나의 차트/그래프 |
| 데이터소스 | 데이터를 가져오는 곳 (InfluxDB 등) |
| 쿼리 | 데이터를 요청하는 질문 |

---

## 3. 데이터소스 연결

### 3.1 InfluxDB 연결하기

1. **☰** → **Connections** → **Data sources**
2. **Add data source** 클릭
3. **InfluxDB** 선택
4. 설정 입력:

```
Query Language: Flux

HTTP:
  URL: http://influxdb:8086

Auth:
  (모두 체크 해제)

InfluxDB Details:
  Organization: ming-org
  Token: ming-super-secret-token
  Default Bucket: factory
```

5. **Save & Test** 클릭
6. "datasource is working" 확인!

### 3.2 연결 테스트

데이터소스 설정 하단에서:
```
✓ datasource is working. 1 buckets found
```

### 3.3 문제 해결

```
❌ "error" 표시되면:

1. URL 확인: http://influxdb:8086 (Docker 내부)
             또는 http://localhost:8086
2. Token 확인: 복사/붙여넣기 시 공백 주의
3. Organization 확인: ming-org (대소문자 구분)
```

---

## 4. 첫 번째 대시보드

### 4.1 대시보드 생성

1. **☰** → **Dashboards**
2. **New** → **New Dashboard**
3. **Add visualization** 클릭

### 4.2 첫 번째 패널 만들기

1. 데이터소스: **InfluxDB** 선택
2. 쿼리 입력:

```flux
from(bucket: "factory")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "sensor_data")
  |> filter(fn: (r) => r._field == "temperature")
```

3. 오른쪽 상단 **Run query** 클릭
4. 그래프가 나타남!
5. **Apply** 클릭

### 4.3 패널 설정

오른쪽 사이드바에서:

```
Panel options:
  Title: 온도 모니터링

Tooltip:
  Mode: All

Legend:
  Visibility: On
  Mode: List

Graph styles:
  Line width: 2
  Fill opacity: 10
```

### 4.4 대시보드 저장

1. 오른쪽 상단 **💾** (저장) 클릭
2. 이름: "공장 모니터링"
3. **Save** 클릭

---

## 5. 패널 유형 마스터

### 5.1 Time series (시계열)

**용도:** 시간에 따른 변화 표시

```
┌────────────────────────────────────┐
│ 온도 변화                          │
│     ╱╲    ╱╲                       │
│    ╱  ╲  ╱  ╲   ╱╲                 │
│   ╱    ╲╱    ╲ ╱  ╲                │
│──╱────────────╳────╲───           │
│  10:00  11:00  12:00  13:00        │
└────────────────────────────────────┘
```

**설정:**
```
Visualization: Time series
```

### 5.2 Stat (단일 값)

**용도:** 현재 값 크게 표시

```
┌────────────────┐
│                │
│     25.5°C     │
│                │
│    ▲ +2.3°C    │
└────────────────┘
```

**쿼리:**
```flux
from(bucket: "factory")
  |> range(start: -5m)
  |> filter(fn: (r) => r._field == "temperature")
  |> last()
```

**설정:**
```
Visualization: Stat
Value options:
  Show: Calculate
  Calculation: Last
```

### 5.3 Gauge (게이지)

**용도:** 범위 내 현재 위치

```
┌────────────────────────┐
│                        │
│      ◜──────◝         │
│    ╱    │     ╲        │
│   ╱     │      ╲       │
│  ╱      ▼       ╲      │
│ 0      50       100    │
│                        │
│       52.5%            │
└────────────────────────┘
```

**설정:**
```
Visualization: Gauge
Standard options:
  Min: 0
  Max: 100
Thresholds:
  0-50: Green
  50-80: Yellow
  80-100: Red
```

### 5.4 Bar chart (막대 그래프)

**용도:** 비교 표시

```
┌────────────────────────────────┐
│ 라인별 생산량                   │
│                                │
│ Line1 ████████████  120        │
│ Line2 ██████████    100        │
│ Line3 ██████        60         │
│                                │
└────────────────────────────────┘
```

### 5.5 Pie chart (원형 차트)

**용도:** 비율 표시

```
┌────────────────────┐
│                    │
│      ╱╲           │
│    ╱ A  ╲         │
│   ╱      ╲        │
│  ────────         │
│   ╲  B  ╱         │
│    ╲  ╱           │
│                    │
│  A: 60%  B: 40%   │
└────────────────────┘
```

### 5.6 Table (테이블)

**용도:** 데이터 목록

```
┌──────────────────────────────────┐
│ 시간         온도    습도         │
├──────────────────────────────────┤
│ 10:00:00    25.5    60.0         │
│ 10:01:00    25.7    59.8         │
│ 10:02:00    25.3    60.2         │
└──────────────────────────────────┘
```

### 5.7 State timeline

**용도:** 상태 변화 이력

```
┌──────────────────────────────────┐
│ 장비 상태                        │
│                                  │
│ ███████████░░░░░████████████    │
│  운전     정지      운전         │
│ 08:00   10:00   12:00   14:00   │
└──────────────────────────────────┘
```

---

## 6. 쿼리 작성하기

### 6.1 기본 쿼리

```flux
// 최근 1시간 온도 데이터
from(bucket: "factory")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "sensor_data")
  |> filter(fn: (r) => r._field == "temperature")
```

### 6.2 여러 필드 함께

```flux
// 온도와 습도 함께
from(bucket: "factory")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "sensor_data")
  |> filter(fn: (r) => r._field == "temperature" or r._field == "humidity")
```

### 6.3 집계 쿼리

```flux
// 5분 평균
from(bucket: "factory")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "sensor_data")
  |> filter(fn: (r) => r._field == "temperature")
  |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
```

### 6.4 그룹별 비교

```flux
// 라인별 온도
from(bucket: "factory")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "sensor_data")
  |> filter(fn: (r) => r._field == "temperature")
  |> group(columns: ["line"])
```

### 6.5 마지막 값 (Stat용)

```flux
from(bucket: "factory")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "sensor_data")
  |> filter(fn: (r) => r._field == "temperature")
  |> last()
```

### 6.6 시간 범위 변수 사용

Grafana의 시간 선택기를 쿼리에 적용:

```flux
from(bucket: "factory")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "sensor_data")
  |> filter(fn: (r) => r._field == "temperature")
```

---

## 7. 알림 설정

### 7.1 알림 규칙 생성

1. **☰** → **Alerting** → **Alert rules**
2. **New alert rule** 클릭

### 7.2 알림 조건 설정

```
섹션 1: 이름
  Rule name: 고온 경고

섹션 2: 쿼리
  A - InfluxDB 쿼리:
  from(bucket: "factory")
    |> range(start: -5m)
    |> filter(fn: (r) => r._field == "temperature")
    |> mean()

  B - 조건:
    WHEN last() OF A IS ABOVE 30

섹션 3: 폴더
  Folder: 선택 또는 생성

섹션 4: 평가
  Evaluate every: 1m
  For: 5m
```

### 7.3 알림 연락처 설정

1. **☰** → **Alerting** → **Contact points**
2. **Add contact point**

**이메일 설정:**
```
Name: 이메일 알림
Type: Email
Addresses: your-email@example.com
```

**Slack 설정:**
```
Name: Slack 알림
Type: Slack
Webhook URL: https://hooks.slack.com/services/xxx
```

### 7.4 알림 정책 설정

1. **☰** → **Alerting** → **Notification policies**
2. **Edit default policy**
3. Contact point 선택

---

## 8. 실전 대시보드

### 8.1 공장 모니터링 대시보드

```
┌─────────────────────────────────────────────────────────┐
│  🏭 공장 모니터링 대시보드                    ⟳ 5s      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │   🌡️ 온도    │ │   💧 습도    │ │   ⚡ 상태   │       │
│  │   25.5°C    │ │   60.0%     │ │   정상 ✓    │       │
│  │   ▲ +1.2    │ │   ▼ -2.0    │ │             │       │
│  └─────────────┘ └─────────────┘ └─────────────┘       │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │ 📈 온도 추이 (24시간)                              │ │
│  │     ╱╲    ╱╲                                      │ │
│  │    ╱  ╲  ╱  ╲   ╱╲                                │ │
│  │   ╱    ╲╱    ╲ ╱  ╲                               │ │
│  │──╱────────────╳────╲───────────────              │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  ┌─────────────────────┐ ┌─────────────────────────┐   │
│  │ �icing 라인별 온도    │ │ 📊 시간대별 생산량       │   │
│  │ Line1 ████ 25°C    │ │     ▓▓▓▓░░░░            │   │
│  │ Line2 ███  23°C    │ │  08  10  12  14  16     │   │
│  │ Line3 █████ 27°C   │ │                         │   │
│  └─────────────────────┘ └─────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 8.2 Row 1: 현재 상태 (Stat 패널)

**패널 1: 현재 온도**
```flux
from(bucket: "factory")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "sensor_data")
  |> filter(fn: (r) => r._field == "temperature")
  |> last()
```

설정:
```
Title: 🌡️ 현재 온도
Unit: Celsius (°C)
Thresholds:
  - 0: green
  - 28: yellow
  - 35: red
```

**패널 2: 현재 습도**
```flux
from(bucket: "factory")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "sensor_data")
  |> filter(fn: (r) => r._field == "humidity")
  |> last()
```

### 8.3 Row 2: 시계열 그래프

**패널: 온도 추이**
```flux
from(bucket: "factory")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "sensor_data")
  |> filter(fn: (r) => r._field == "temperature")
  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
```

설정:
```
Title: 📈 온도 추이
Legend: On
Line width: 2
Fill opacity: 10
```

### 8.4 Row 3: 비교 차트

**패널: 라인별 온도 비교 (Bar Chart)**
```flux
from(bucket: "factory")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "sensor_data")
  |> filter(fn: (r) => r._field == "temperature")
  |> group(columns: ["line"])
  |> mean()
```

### 8.5 변수 설정

1. 대시보드 설정 (⚙️) → **Variables**
2. **Add variable**

```
Name: line
Type: Query
Data source: InfluxDB

Query:
import "influxdata/influxdb/schema"
schema.tagValues(bucket: "factory", tag: "line")
```

**쿼리에서 변수 사용:**
```flux
from(bucket: "factory")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "sensor_data")
  |> filter(fn: (r) => r.line == "${line}")
  |> filter(fn: (r) => r._field == "temperature")
```

### 8.6 자동 새로고침 설정

대시보드 오른쪽 상단:
```
🔄 Refresh: 5s, 10s, 30s, 1m, 5m, 15m, 30m, 1h
```

### 8.7 대시보드 공유

1. 오른쪽 상단 **공유** 버튼
2. **Link** 탭에서 URL 복사
3. **Snapshot**: 현재 상태 스냅샷 저장

---

## 9. 문제 해결

### 9.1 데이터가 안 보임

```
1. 데이터소스 연결 확인
   - Data sources → Test

2. 쿼리 확인
   - Query Inspector 열기 (패널 편집 → Query Inspector)
   - 에러 메시지 확인

3. 시간 범위 확인
   - 오른쪽 상단 시간 선택기
   - "Last 1 hour" 등으로 변경

4. 데이터 존재 확인
   - InfluxDB UI에서 직접 쿼리 실행
```

### 9.2 쿼리 에러

```
에러: "error parsing query"

확인:
1. Flux 문법 확인 (|> 파이프 연산자)
2. 따옴표 확인 (큰따옴표 사용)
3. 버킷/필드 이름 철자 확인
```

### 9.3 패널이 느림

```
최적화 방법:
1. 시간 범위 줄이기
2. aggregateWindow 사용하여 데이터 양 줄이기
3. 불필요한 필드 제외
```

### 9.4 알림이 안 옴

```
확인:
1. Contact point 테스트
2. Alert rule 상태 확인 (Firing인지)
3. Notification policy 확인
```

---

## 📝 핵심 요약

| 개념 | 설명 |
|------|------|
| 대시보드 | 패널들의 모음 |
| 패널 | 하나의 시각화 (차트) |
| 데이터소스 | 데이터를 가져오는 연결 |
| 쿼리 | 데이터 요청 |
| 변수 | 동적 필터링 |
| 알림 | 조건 충족 시 알림 |

### 자주 쓰는 패널 유형

| 패널 | 용도 |
|------|------|
| Time series | 시간에 따른 변화 |
| Stat | 현재 값 크게 |
| Gauge | 범위 내 위치 |
| Bar chart | 비교 |
| Table | 데이터 목록 |
| State timeline | 상태 변화 이력 |

### 유용한 단축키

| 키 | 동작 |
|---|------|
| `d` | 대시보드 설정 |
| `e` | 패널 편집 |
| `v` | 패널 보기 모드 |
| `Esc` | 편집 닫기 |
| `Ctrl+S` | 저장 |

---

## 🎉 축하합니다!

MING Stack의 4가지 핵심 기술을 모두 배웠습니다!

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   센서 → [Mosquitto] → [Node-RED] → [InfluxDB]         │
│                              │                          │
│                              ▼                          │
│                        [Grafana] → 📊 대시보드          │
│                              │                          │
│                              ▼                          │
│                         🔔 알림                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

이제 실제 프로젝트를 만들어 보세요! 🚀
