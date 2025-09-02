#!/bin/bash

echo "-- 서버 중지 스크립트 시작 --"

# 백엔드 서버 종료 (포트 8000)
echo "백엔드 서버 (포트 8000) 종료 시도..."
PID_BACKEND=$(lsof -t -i :8000)
if [ -n "$PID_BACKEND" ]; then
    kill -9 "$PID_BACKEND"
    echo "✅ 백엔드 서버 (PID: $PID_BACKEND) 종료 완료"
else
    echo "ℹ️  백엔드 서버 (포트 8000)가 실행 중이지 않습니다."
fi

# 프론트엔드 서버 종료 (포트 3000)
echo "프론트엔드 서버 (포트 3000) 종료 시도..."
PID_FRONTEND=$(lsof -t -i :3000)
if [ -n "$PID_FRONTEND" ]; then
    kill -9 "$PID_FRONTEND"
    echo "✅ 프론트엔드 서버 (PID: $PID_FRONTEND) 종료 완료"
else
    echo "ℹ️  프론트엔드 서버 (포트 3000)가 실행 중이지 않습니다."
fi

echo ""
echo "-- 서버 중지 스크립트 완료 --"
echo "모든 개발 서버가 중지되었습니다."