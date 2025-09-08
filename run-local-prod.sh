#!/bin/bash

# 로컬 프로덕션 테스트 실행 스크립트

echo "🚀 로컬 프로덕션 환경 테스트 시작"

# 환경 변수 설정
export SECRET_KEY="django-insecure-local-test-key-only-for-development-purposes-do-not-use-in-real-production"
export DEBUG="False"
export ALLOWED_HOSTS="localhost,127.0.0.1,frontend,backend"
export CORS_ALLOWED_ORIGINS="http://localhost,http://127.0.0.1"
export DB_NAME="mes_local_test_db"
export DB_USER="mes_local_user"
export DB_PASSWORD="mes_local_password_123"
export DB_ROOT_PASSWORD="mes_root_password_123"
export REACT_APP_API_URL="http://localhost/api"

echo "✅ 환경 변수 설정 완료"

# 이전 컨테이너 정리
echo "🧹 이전 컨테이너 정리 중..."
docker compose -f docker-compose.prod.yml down -v

# DB만 먼저 실행
echo "🗄️  데이터베이스 실행 중..."
docker compose -f docker-compose.prod.yml up db -d

# DB 준비 대기
echo "⏳ 데이터베이스 준비 대기 중..."
sleep 15

# 백엔드 실행
echo "🔧 백엔드 실행 중..."
docker compose -f docker-compose.prod.yml up backend -d

# 백엔드 준비 대기
echo "⏳ 백엔드 준비 대기 중..."
sleep 10

echo "✅ 로컬 프로덕션 환경 실행 완료!"
echo "📊 서비스 상태:"
docker compose -f docker-compose.prod.yml ps

echo ""
echo "🌐 접속 정보:"
echo "  - 백엔드 API: http://localhost:8000"
echo "  - 관리자: http://localhost:8000/admin"
echo ""
echo "🧪 테스트 명령어:"
echo "  curl http://localhost:8000/api/"
echo "  curl http://localhost:8000/health"