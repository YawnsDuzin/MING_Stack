#!/bin/bash
# =============================================================================
# MING Stack systemd 서비스 설치 스크립트
# =============================================================================

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "============================================================"
echo "  MING Stack systemd 서비스 설치"
echo "============================================================"
echo ""

# 현재 디렉토리
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 현재 사용자
CURRENT_USER=$(whoami)

# 루트 권한 확인
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}오류: 이 스크립트는 root 권한이 필요합니다.${NC}"
    echo "sudo ./scripts/install-service.sh 로 실행하세요."
    exit 1
fi

# 서비스 파일 경로
SERVICE_FILE="$SCRIPT_DIR/ming-stack.service"
TARGET_FILE="/etc/systemd/system/ming-stack.service"

if [ ! -f "$SERVICE_FILE" ]; then
    echo -e "${RED}오류: 서비스 파일을 찾을 수 없습니다: $SERVICE_FILE${NC}"
    exit 1
fi

# 사용자 입력
echo -e "${YELLOW}설정을 확인합니다:${NC}"
echo ""

# 프로젝트 디렉토리
read -p "프로젝트 디렉토리 [$PROJECT_DIR]: " INPUT_DIR
PROJECT_DIR=${INPUT_DIR:-$PROJECT_DIR}

# 실행 사용자
read -p "실행 사용자 [$CURRENT_USER]: " INPUT_USER
RUN_USER=${INPUT_USER:-$CURRENT_USER}

echo ""
echo "설정:"
echo "  프로젝트 디렉토리: $PROJECT_DIR"
echo "  실행 사용자: $RUN_USER"
echo ""

read -p "계속하시겠습니까? (y/n): " CONFIRM
if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
    echo "취소되었습니다."
    exit 0
fi

# 서비스 파일 복사 및 수정
echo ""
echo "서비스 파일 설치 중..."

# 임시 파일 생성
TEMP_FILE=$(mktemp)

# sed로 경로와 사용자 수정
sed -e "s|WorkingDirectory=.*|WorkingDirectory=$PROJECT_DIR|g" \
    -e "s|User=.*|User=$RUN_USER|g" \
    -e "s|EnvironmentFile=.*|EnvironmentFile=-$PROJECT_DIR/.env|g" \
    "$SERVICE_FILE" > "$TEMP_FILE"

# 서비스 파일 복사
cp "$TEMP_FILE" "$TARGET_FILE"
rm "$TEMP_FILE"

# 권한 설정
chmod 644 "$TARGET_FILE"

echo -e "${GREEN}✓ 서비스 파일 설치 완료: $TARGET_FILE${NC}"

# systemd 재로드
echo "systemd 데몬 재로드 중..."
systemctl daemon-reload
echo -e "${GREEN}✓ systemd 데몬 재로드 완료${NC}"

# 서비스 활성화
echo "서비스 활성화 중..."
systemctl enable ming-stack
echo -e "${GREEN}✓ 서비스 활성화 완료${NC}"

# 완료 메시지
echo ""
echo "============================================================"
echo -e "${GREEN}  설치 완료!${NC}"
echo "============================================================"
echo ""
echo "사용 가능한 명령:"
echo "  sudo systemctl start ming-stack    # 시작"
echo "  sudo systemctl stop ming-stack     # 중지"
echo "  sudo systemctl restart ming-stack  # 재시작"
echo "  sudo systemctl status ming-stack   # 상태 확인"
echo "  sudo journalctl -u ming-stack -f   # 로그 확인"
echo ""
echo "서비스를 지금 시작하시겠습니까?"
read -p "(y/n): " START_NOW

if [[ "$START_NOW" == "y" || "$START_NOW" == "Y" ]]; then
    echo ""
    echo "서비스 시작 중..."
    systemctl start ming-stack
    sleep 3
    systemctl status ming-stack --no-pager
fi

echo ""
echo "설치가 완료되었습니다."
