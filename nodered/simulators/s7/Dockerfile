# Siemens S7 PLC Simulator for MING Stack
# Python 기반 S7 통신 시뮬레이터

FROM python:3.11-slim

WORKDIR /app

# 필수 패키지 설치
RUN pip install --no-cache-dir python-snap7

# 시뮬레이터 스크립트 복사
COPY s7_simulator.py .
COPY run_simulator.sh .

RUN chmod +x run_simulator.sh

# 포트 노출
EXPOSE 102

# 시뮬레이터 실행
CMD ["python", "-u", "s7_simulator.py"]
