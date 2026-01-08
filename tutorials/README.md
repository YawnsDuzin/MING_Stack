# MING Stack 튜토리얼

> 처음 시작하는 분들을 위한 단계별 학습 가이드

---

## 📚 튜토리얼 목록

| 순서 | 주제 | 설명 | 난이도 |
|------|------|------|--------|
| 1 | [MQTT & Mosquitto](./01-mqtt-mosquitto-tutorial.md) | 메시지 브로커의 기초 | ⭐ |
| 2 | [InfluxDB](./02-influxdb-tutorial.md) | 시계열 데이터베이스 | ⭐⭐ |
| 3 | [Node-RED](./03-nodered-tutorial.md) | 플로우 프로그래밍 | ⭐⭐ |
| 4 | [Grafana](./04-grafana-tutorial.md) | 데이터 시각화 | ⭐⭐ |

---

## 🎯 학습 순서

```
1️⃣ MQTT & Mosquitto
   ↓
   메시지 송수신 이해

2️⃣ InfluxDB
   ↓
   데이터 저장/조회 이해

3️⃣ Node-RED
   ↓
   데이터 처리 자동화

4️⃣ Grafana
   ↓
   대시보드 만들기
```

---

## 🏭 MING Stack 전체 흐름

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   📡 센서/PLC                                                │
│       │                                                     │
│       ▼                                                     │
│   ┌─────────────────┐                                       │
│   │   Mosquitto     │  ← MQTT 브로커 (메시지 중계)          │
│   │   (MQTT)        │                                       │
│   └────────┬────────┘                                       │
│            │                                                │
│            ▼                                                │
│   ┌─────────────────┐                                       │
│   │    Node-RED     │  ← 데이터 처리/변환/자동화            │
│   │   (플로우)      │                                       │
│   └────────┬────────┘                                       │
│            │                                                │
│            ▼                                                │
│   ┌─────────────────┐                                       │
│   │   InfluxDB      │  ← 시계열 데이터 저장                 │
│   │   (데이터베이스) │                                       │
│   └────────┬────────┘                                       │
│            │                                                │
│            ▼                                                │
│   ┌─────────────────┐                                       │
│   │    Grafana      │  ← 실시간 시각화/대시보드             │
│   │   (대시보드)     │                                       │
│   └─────────────────┘                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ⏱️ 예상 학습 시간

| 튜토리얼 | 예상 시간 |
|----------|----------|
| MQTT & Mosquitto | 30분 ~ 1시간 |
| InfluxDB | 30분 ~ 1시간 |
| Node-RED | 1시간 ~ 2시간 |
| Grafana | 1시간 ~ 2시간 |
| **총 학습 시간** | **3시간 ~ 6시간** |

---

## 💡 학습 팁

1. **직접 따라하기**: 예제 코드를 복사/붙여넣기보다 직접 입력하세요
2. **실험하기**: 설정값을 변경해보면서 결과를 확인하세요
3. **에러 두려워하지 않기**: 에러 메시지를 읽고 해결하는 과정이 학습입니다
4. **작은 프로젝트**: 튜토리얼 후 간단한 프로젝트를 직접 만들어보세요

---

## 🔗 추가 자료

### 공식 문서

- [Mosquitto Documentation](https://mosquitto.org/documentation/)
- [InfluxDB Documentation](https://docs.influxdata.com/influxdb/v2/)
- [Node-RED Documentation](https://nodered.org/docs/)
- [Grafana Documentation](https://grafana.com/docs/)

### MING Stack 문서

- [설치 가이드](../docs/01-installation.md)
- [Mosquitto 설정](../docs/02-mosquitto-setup.md)
- [InfluxDB 설정](../docs/03-influxdb-setup.md)
- [Node-RED 설정](../docs/04-nodered-setup.md)
- [Grafana 설정](../docs/05-grafana-setup.md)

---

## ❓ 질문이 있으시면

GitHub Issues에 질문을 올려주세요!
