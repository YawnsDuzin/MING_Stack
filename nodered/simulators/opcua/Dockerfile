# OPC-UA Server Simulator for MING Stack
# Python 기반 OPC-UA 서버 시뮬레이터

FROM python:3.11-slim

WORKDIR /app

# 필수 패키지 설치
RUN pip install --no-cache-dir \
    asyncua==1.0.4 \
    cryptography>=3.1

# 시뮬레이터 스크립트 복사
COPY opcua_simulator.py .

# 포트 노출
EXPOSE 4840

# 시뮬레이터 실행
CMD ["python", "-u", "opcua_simulator.py"]
