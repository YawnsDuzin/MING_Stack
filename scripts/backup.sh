#!/bin/bash
# MING Stack 백업 스크립트

set -e

BACKUP_DIR="${BACKUP_DIR:-./backups}"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="ming-backup-$DATE.tar.gz"

echo "=========================================="
echo "  MING Stack - Backup"
echo "=========================================="

cd "$(dirname "$0")/.."

# 백업 디렉토리 생성
mkdir -p "$BACKUP_DIR"

echo "Stopping services for consistent backup..."
docker compose stop

echo "Creating backup: $BACKUP_FILE"
tar -czvf "$BACKUP_DIR/$BACKUP_FILE" \
    --exclude='*.log' \
    mosquitto/data \
    influxdb/data \
    nodered/data \
    grafana/data \
    .env

echo "Restarting services..."
docker compose start

echo ""
echo "=========================================="
echo "  Backup completed!"
echo "  File: $BACKUP_DIR/$BACKUP_FILE"
echo "  Size: $(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)"
echo "=========================================="
