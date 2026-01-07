# InfluxDB 설정 가이드

> InfluxDB 2.x 시계열 데이터베이스 설정 및 활용

---

## 1. InfluxDB 2.x 개요

### 1.1 주요 특징

| 특징 | 설명 |
|------|------|
| 시계열 최적화 | 타임스탬프 기반 데이터에 최적화 |
| Flux 쿼리 언어 | 강력한 데이터 처리 언어 |
| 내장 UI | 웹 기반 관리 인터페이스 |
| 태스크 | 자동화된 데이터 처리 |
| 알림 | 조건 기반 알림 기능 |

### 1.2 핵심 개념

- **Organization**: 사용자와 리소스 그룹
- **Bucket**: 데이터 저장소 (보존 정책 포함)
- **Measurement**: 테이블과 유사한 개념
- **Tag**: 인덱싱되는 메타데이터
- **Field**: 실제 측정값
- **Timestamp**: 데이터 포인트의 시간

---

## 2. 초기 설정

### 2.1 웹 UI 접속

```
URL: http://raspberrypi:8086
Username: admin
Password: admin123456 (기본값)
```

### 2.2 환경 변수 설정 (.env)

```bash
INFLUXDB_USERNAME=admin
INFLUXDB_PASSWORD=admin123456
INFLUXDB_ORG=ming-org
INFLUXDB_BUCKET=factory
INFLUXDB_TOKEN=ming-super-secret-token
INFLUXDB_RETENTION=7d
```

---

## 3. Bucket 관리

### 3.1 Bucket 생성 (CLI)

```bash
docker exec ming-influxdb influx bucket create \
    --name sensor_data \
    --org ming-org \
    --retention 30d \
    --token ming-super-secret-token
```

### 3.2 보존 정책별 Bucket

```bash
# Raw 데이터 (7일)
influx bucket create --name factory_raw --retention 7d

# 1분 집계 (30일)
influx bucket create --name factory_1m --retention 30d

# 1시간 집계 (1년)
influx bucket create --name factory_1h --retention 365d

# 1일 집계 (영구)
influx bucket create --name factory_1d --retention 0
```

---

## 4. 데이터 쓰기

### 4.1 Line Protocol 형식

```
<measurement>,<tag_set> <field_set> <timestamp>

# 예시
sensor_data,location=line1,device=temp_001 temperature=25.5,humidity=60.2 1704067200000000000
```

### 4.2 Node-RED에서 쓰기

```javascript
// InfluxDB Out 노드 설정
msg.payload = [{
    measurement: "sensor_data",
    tags: {
        location: "line1",
        device: "plc_001"
    },
    fields: {
        temperature: 25.5,
        humidity: 60.2
    },
    timestamp: new Date()
}];
return msg;
```

### 4.3 HTTP API로 쓰기

```bash
curl -XPOST "http://localhost:8086/api/v2/write?org=ming-org&bucket=factory&precision=s" \
    -H "Authorization: Token ming-super-secret-token" \
    -H "Content-Type: text/plain" \
    --data-raw "sensor_data,location=line1 temperature=25.5"
```

---

## 5. Flux 쿼리

### 5.1 기본 쿼리

```flux
from(bucket: "factory")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "sensor_data")
  |> filter(fn: (r) => r["_field"] == "temperature")
```

### 5.2 집계 쿼리

```flux
from(bucket: "factory")
  |> range(start: -24h)
  |> filter(fn: (r) => r["_measurement"] == "sensor_data")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
  |> yield(name: "hourly_avg")
```

### 5.3 여러 필드 조회

```flux
from(bucket: "factory")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "sensor_data")
  |> filter(fn: (r) => r["_field"] == "temperature" or r["_field"] == "humidity")
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
```

### 5.4 조건 필터링

```flux
from(bucket: "factory")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "sensor_data")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> filter(fn: (r) => r["_value"] > 30)  // 30도 이상만
```

---

## 6. 다운샘플링 태스크

### 6.1 1분 평균 태스크

```flux
option task = {name: "downsample_1m", every: 1m}

from(bucket: "factory")
  |> range(start: -task.every)
  |> filter(fn: (r) => r["_measurement"] == "sensor_data")
  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
  |> to(bucket: "factory_1m", org: "ming-org")
```

### 6.2 1시간 평균 태스크

```flux
option task = {name: "downsample_1h", every: 1h}

from(bucket: "factory_1m")
  |> range(start: -task.every)
  |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
  |> to(bucket: "factory_1h", org: "ming-org")
```

---

## 7. 알림 설정

### 7.1 임계값 체크

```flux
option task = {name: "temp_alert", every: 1m}

data = from(bucket: "factory")
  |> range(start: -5m)
  |> filter(fn: (r) => r["_measurement"] == "sensor_data")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> last()
  |> filter(fn: (r) => r["_value"] > 35)

data
  |> to(bucket: "alerts", org: "ming-org")
```

---

## 8. 백업 및 복구

### 8.1 백업

```bash
docker exec ming-influxdb influx backup /var/lib/influxdb2/backup \
    --org ming-org \
    --token ming-super-secret-token
```

### 8.2 복구

```bash
docker exec ming-influxdb influx restore /var/lib/influxdb2/backup \
    --org ming-org \
    --token ming-super-secret-token
```

---

## 9. 성능 최적화

### 9.1 라즈베리파이 권장 설정

```yaml
# docker-compose.yml
environment:
  - INFLUXD_STORAGE_CACHE_MAX_MEMORY_SIZE=256m
  - INFLUXD_STORAGE_CACHE_SNAPSHOT_MEMORY_SIZE=25m
```

### 9.2 쿼리 최적화 팁

1. 시간 범위를 최소화
2. 필요한 필드만 조회
3. 집계 데이터 활용
4. 태그 인덱스 활용

---

## 참고 자료

- [InfluxDB Documentation](https://docs.influxdata.com/influxdb/v2/)
- [Flux Language Reference](https://docs.influxdata.com/flux/v0/)
