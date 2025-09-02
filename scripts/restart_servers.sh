#!/bin/bash

echo "-- 서버 재시작 스크립트 시작 --"

# 백엔드 서버 종료 (포트 8000)
echo "백엔드 서버 (포트 8000) 종료 시도..."
PID_BACKEND=$(lsof -t -i :8000)
if [ -n "$PID_BACKEND" ]; then
    kill -9 "$PID_BACKEND"
    echo "백엔드 서버 (PID: $PID_BACKEND) 종료 완료."
else
    echo "백엔드 서버 (포트 8000)가 실행 중이지 않습니다."
fi
sleep 2 # 포트 해제를 위한 대기

# 프론트엔드 서버 종료 (포트 3000)
echo "프론트엔드 서버 (포트 3000) 종료 시도..."
PID_FRONTEND=$(lsof -t -i :3000)
if [ -n "$PID_FRONTEND" ]; then
    kill -9 "$PID_FRONTEND"
    echo "프론트엔드 서버 (PID: $PID_FRONTEND) 종료 완료."
else
    echo "프론트엔드 서버 (포트 3000)가 실행 중이지 않습니다."
fi
sleep 2 # 포트 해제를 위한 대기

echo "-- 서버 재시작 시작 --"

# 백엔드 서버 시작
echo "백엔드 서버 시작 중..."
cd ../backend && source venv/bin/activate && python manage.py runserver &
BACKEND_PID=$!
echo "백엔드 서버 시작 완료 (PID: $BACKEND_PID)"
sleep 3 # 서버 시작 대기

# 프론트엔드 서버 시작
echo "프론트엔드 서버 시작 중..."
cd ../frontend && npm start &
FRONTEND_PID=$!
echo "프론트엔드 서버 시작 완료 (PID: $FRONTEND_PID)"
sleep 3 # 서버 시작 대기

echo "-- 서버 상태 확인 --"
sleep 2

# 백엔드 서버 상태 확인
if curl -s http://localhost:8000/admin/login/ > /dev/null 2>&1; then
    echo "✅ 백엔드 서버 (http://localhost:8000) 정상 작동"
else
    echo "❌ 백엔드 서버 응답 없음"
fi

# 프론트엔드 서버 상태 확인
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ 프론트엔드 서버 (http://localhost:3000) 정상 작동"
else
    echo "❌ 프론트엔드 서버 응답 없음"
fi

echo ""
echo "-- 서버 재시작 스크립트 완료 --"
echo "🌐 브라우저에서 http://localhost:3000 에 접속하여 확인해주세요."
echo "📚 API 문서: http://localhost:8000/api/docs/"
