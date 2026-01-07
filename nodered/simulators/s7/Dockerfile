# =============================================================================
# Siemens S7 PLC Simulator for MING Stack
# Python 기반 S7 통신 시뮬레이터 (ARM64 호환)
# =============================================================================
#
# 참고: 이 시뮬레이터는 snap7 라이브러리 없이 순수 Python으로 구현되어
#       ARM64 (라즈베리파이) 환경에서도 정상 동작합니다.
# =============================================================================

FROM python:3.11-slim

# 플랫폼 정보 (ARM64/AMD64 자동 감지)
ARG TARGETPLATFORM
ARG BUILDPLATFORM

WORKDIR /app

# 필수 패키지만 설치 (snap7 제외 - ARM64 미지원)
# 순수 Python TCP 기반 S7 프로토콜 시뮬레이션
RUN pip install --no-cache-dir --upgrade pip

# 시뮬레이터 스크립트 복사
COPY s7_simulator.py .

# 포트 노출 (1102 사용 - non-privileged)
EXPOSE 1102

# 환경변수
ENV S7_PORT=1102
ENV PYTHONUNBUFFERED=1

# 시뮬레이터 실행
CMD ["python", "-u", "s7_simulator.py"]
