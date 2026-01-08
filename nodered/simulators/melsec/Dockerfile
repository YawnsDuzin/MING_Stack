# =============================================================================
# Mitsubishi MELSEC MC Protocol Simulator for MING Stack
# Python 기반 MC 프로토콜 시뮬레이터 (ARM64 호환)
# =============================================================================
#
# MC 프로토콜: 미쓰비시 전기 MELSEC PLC 시리즈 통신 프로토콜
# 지원 프레임: 3E (Binary)
# =============================================================================

FROM python:3.11-slim

# 플랫폼 정보 (ARM64/AMD64 자동 감지)
ARG TARGETPLATFORM
ARG BUILDPLATFORM

WORKDIR /app

# 필수 패키지 설치 (순수 Python, 외부 의존성 없음)
RUN pip install --no-cache-dir --upgrade pip

# 시뮬레이터 스크립트 복사
COPY mc_simulator.py .

# 포트 노출 (MC 프로토콜 기본 포트)
EXPOSE 5000

# 환경변수
ENV MC_PORT=5000
ENV MC_HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

# 시뮬레이터 실행
CMD ["python", "-u", "mc_simulator.py"]
