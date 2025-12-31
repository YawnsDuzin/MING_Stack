# Modbus TCP Simulator for MING Stack
# Python 기반 Modbus 서버 시뮬레이터

FROM python:3.11-slim

WORKDIR /app

# 필수 패키지 설치
RUN pip install --no-cache-dir pymodbus==3.5.4

# 시뮬레이터 스크립트 복사
COPY modbus_simulator.py .

# 포트 노출
EXPOSE 5020

# 시뮬레이터 실행
CMD ["python", "-u", "modbus_simulator.py"]
