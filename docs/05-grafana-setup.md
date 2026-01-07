# Grafana 설정 가이드

> Grafana 대시보드 및 알림 설정

---

## 1. Grafana 개요

Grafana는 메트릭 데이터 시각화 및 모니터링을 위한 오픈소스 플랫폼입니다.

### 1.1 주요 기능

| 기능 | 설명 |
|------|------|
| 대시보드 | 다양한 시각화 패널 |
| 알림 | 조건 기반 알림 |
| 데이터소스 | 다양한 DB 연동 |
| 플러그인 | 기능 확장 |

---

## 2. 접속 정보

```
URL: http://raspberrypi:3000
Username: admin
Password: admin123 (기본값)
```

---

## 3. 데이터소스 설정

### 3.1 InfluxDB 연결 (자동 프로비저닝됨)

MING Stack은 자동으로 InfluxDB 데이터소스를 구성합니다.

수동 설정 시:
```
Type: InfluxDB
Query Language: Flux
URL: http://influxdb:8086
Organization: ming-org
Token: ming-super-secret-token
Default Bucket: factory
```

### 3.2 데이터소스 테스트

Configuration → Data Sources → InfluxDB → Save & Test

---

## 4. 대시보드 생성

### 4.1 새 대시보드 만들기

1. + 버튼 → Dashboard
2. Add visualization
3. 데이터소스 선택
4. 쿼리 작성
5. Save dashboard

### 4.2 Flux 쿼리 예시

```flux
from(bucket: "factory")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "sensor_data")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
```

---

## 5. 패널 유형

### 5.1 Stat (통계)

현재 값 표시에 적합

```flux
from(bucket: "factory")
  |> range(start: -5m)
  |> filter(fn: (r) => r["_measurement"] == "sensor_data")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> last()
```

### 5.2 Time Series (시계열)

트렌드 표시에 적합

### 5.3 Gauge (게이지)

범위 내 값 표시에 적합

### 5.4 Table (테이블)

상세 데이터 표시에 적합

### 5.5 Heatmap (히트맵)

분포 표시에 적합

---

## 6. 변수 (Variables)

### 6.1 변수 생성

Dashboard Settings → Variables → New variable

```
Name: location
Type: Query
Data source: InfluxDB
Query:
  import "influxdata/influxdb/schema"
  schema.tagValues(bucket: "factory", tag: "location")
```

### 6.2 쿼리에서 변수 사용

```flux
from(bucket: "factory")
  |> range(start: v.timeRangeStart)
  |> filter(fn: (r) => r["location"] == "${location}")
```

---

## 7. 알림 설정

### 7.1 알림 규칙 생성

Alerting → Alert rules → New alert rule

### 7.2 알림 조건 예시

```
Rule name: High Temperature Alert
Condition: WHEN last() OF query(A) IS ABOVE 35
Evaluate: Every 1m for 5m
```

### 7.3 알림 채널 설정

#### Email
```
Type: Email
Addresses: admin@example.com
```

#### Telegram
```
Type: Telegram
Bot API Token: <your_bot_token>
Chat ID: <your_chat_id>
```

#### Webhook
```
Type: Webhook
URL: http://your-webhook-endpoint
```

---

## 8. 프로비저닝

### 8.1 데이터소스 프로비저닝

`grafana/provisioning/datasources/influxdb.yml`:

```yaml
apiVersion: 1
datasources:
  - name: InfluxDB
    type: influxdb
    access: proxy
    url: http://influxdb:8086
    jsonData:
      version: Flux
      organization: ming-org
      defaultBucket: factory
    secureJsonData:
      token: ming-super-secret-token
    isDefault: true
```

### 8.2 대시보드 프로비저닝

`grafana/provisioning/dashboards/dashboards.yml`:

```yaml
apiVersion: 1
providers:
  - name: 'MING Stack Dashboards'
    folder: 'MING Stack'
    type: file
    options:
      path: /var/lib/grafana/dashboards
```

---

## 9. 대시보드 내보내기/가져오기

### 9.1 내보내기

Dashboard → Share → Export → Save to file

### 9.2 가져오기

+ → Import → Upload JSON file

---

## 10. 성능 최적화

### 10.1 쿼리 최적화

- 시간 범위 최소화
- 적절한 집계 간격 사용
- 불필요한 필드 제외

### 10.2 대시보드 최적화

- 패널 수 최소화
- 자동 새로고침 간격 적절히 설정 (5초 이상)
- 캐싱 활용

---

## 11. 유용한 대시보드

### 11.1 공장 개요 대시보드

포함 패널:
- 온도/습도 현황 (Stat)
- 모터 속도 (Gauge)
- 센서 트렌드 (Time Series)
- 알람 히스토리 (Table)

### 11.2 설비 상세 대시보드

포함 패널:
- 실시간 데이터
- 가동률
- 에러 이력
- 성능 지표

---

## 참고 자료

- [Grafana Documentation](https://grafana.com/docs/grafana/latest/)
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/)
