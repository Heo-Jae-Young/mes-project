#!/bin/bash

echo "-- 서버 상태 확인 --"

# 포트별 프로세스 확인
echo "📋 실행 중인 프로세스:"
BACKEND_PID=$(lsof -t -i :8000 2>/dev/null)
FRONTEND_PID=$(lsof -t -i :3000 2>/dev/null)

if [ -n "$BACKEND_PID" ]; then
    echo "  🖥️  백엔드 서버: PID $BACKEND_PID (포트 8000)"
else
    echo "  🖥️  백엔드 서버: 실행 중이지 않음"
fi

if [ -n "$FRONTEND_PID" ]; then
    echo "  🌐 프론트엔드 서버: PID $FRONTEND_PID (포트 3000)"
else
    echo "  🌐 프론트엔드 서버: 실행 중이지 않음"
fi

echo ""
echo "🔍 HTTP 응답 확인:"

# 백엔드 서버 응답 확인 (Django admin 페이지로 확인)
if curl -s -f http://localhost:8000/admin/login/ > /dev/null 2>&1; then
    echo "  ✅ 백엔드 서버 (http://localhost:8000) 정상 응답"
else
    echo "  ❌ 백엔드 서버 응답 없음"
fi

# 프론트엔드 서버 응답 확인
if curl -s -f http://localhost:3000 > /dev/null 2>&1; then
    echo "  ✅ 프론트엔드 (http://localhost:3000) 정상 응답"
else
    echo "  ❌ 프론트엔드 응답 없음"
fi

# JWT 토큰 테스트
echo ""
echo "🔐 JWT 인증 테스트:"
JWT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/token/ \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123"}' 2>/dev/null)

if echo "$JWT_RESPONSE" | grep -q "access"; then
    echo "  ✅ JWT 토큰 발급 정상"
else
    echo "  ❌ JWT 토큰 발급 실패"
fi

echo ""
echo "-- 상태 확인 완료 --"
echo "📚 유용한 링크:"
echo "  - 프론트엔드: http://localhost:3000"
echo "  - 백엔드 API: http://localhost:8000/api/"
echo "  - Swagger UI: http://localhost:8000/api/docs/"
echo "  - Django Admin: http://localhost:8000/admin/ (admin/admin123)"