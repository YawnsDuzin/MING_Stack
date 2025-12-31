#!/bin/bash
# MING Stack 중지 스크립트

echo "=========================================="
echo "  MING Stack - Stopping Services"
echo "=========================================="

cd "$(dirname "$0")/.."

docker compose stop

echo ""
echo "Services stopped. Data is preserved."
echo "Use 'docker compose down' to remove containers."
