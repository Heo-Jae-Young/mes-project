#!/bin/bash

# MES 서버 설정 업데이트 스크립트
# Usage: ./scripts/update-server.sh [EC2_IP] [--full-rebuild]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
KEY_PATH="$HOME/.ssh/mes-keypair.pem"
DEFAULT_EC2_IP="YOUR_EC2_IP"  # 실제 EC2 인스턴스 IP로 변경 필요

# Parse arguments
EC2_IP=${1:-$DEFAULT_EC2_IP}
FULL_REBUILD=false

if [[ "$2" == "--full-rebuild" ]]; then
    FULL_REBUILD=true
fi

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "필수 조건 확인 중..."
    
    if [[ ! -f "$KEY_PATH" ]]; then
        print_error "SSH key not found at $KEY_PATH"
        exit 1
    fi
    
    print_success "필수 조건 확인 완료"
}

# Upload configuration files
upload_configs() {
    print_status "설정 파일 전송 중..."
    
    # nginx 설정 파일
    scp -i "$KEY_PATH" ./nginx/nginx.conf "ubuntu@$EC2_IP:~/mes-project/nginx/"
    scp -i "$KEY_PATH" ./nginx/conf.d/default.conf "ubuntu@$EC2_IP:~/mes-project/nginx/conf.d/"
    
    # Docker Compose 파일
    scp -i "$KEY_PATH" ./docker-compose.prod.yml "ubuntu@$EC2_IP:~/mes-project/"
    
    # 배포 스크립트
    scp -i "$KEY_PATH" ./scripts/deploy.sh "ubuntu@$EC2_IP:~/mes-project/scripts/"
    chmod +x "ubuntu@$EC2_IP:~/mes-project/scripts/deploy.sh" || true
    
    print_success "설정 파일 전송 완료"
}

# Apply updates on server
apply_updates() {
    print_status "서버에서 업데이트 적용 중..."
    
    if [[ "$FULL_REBUILD" == true ]]; then
        print_warning "전체 재빌드 모드로 실행 중..."
        ssh -i "$KEY_PATH" "ubuntu@$EC2_IP" << 'EOF'
cd mes-project
echo "🔄 전체 서비스 재빌드 중..."
docker compose -f docker-compose.prod.yml --env-file .env.prod down
docker compose -f docker-compose.prod.yml --env-file .env.prod build --no-cache
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d
echo "📊 정적 파일 재수집 중..."
docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T backend python manage.py collectstatic --noinput
echo "✅ 전체 재빌드 완료"
EOF
    else
        print_status "빠른 업데이트 모드로 실행 중..."
        ssh -i "$KEY_PATH" "ubuntu@$EC2_IP" << 'EOF'
cd mes-project
echo "🔄 서비스 재시작 중..."
docker compose -f docker-compose.prod.yml --env-file .env.prod restart nginx
echo "📊 정적 파일 재수집 중..."
docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T backend python manage.py collectstatic --noinput
echo "✅ 빠른 업데이트 완료"
EOF
    fi
}

# Check server status
check_status() {
    print_status "서버 상태 확인 중..."
    
    ssh -i "$KEY_PATH" "ubuntu@$EC2_IP" << 'EOF'
cd mes-project
echo "📊 서비스 상태:"
docker compose -f docker-compose.prod.yml --env-file .env.prod ps
echo ""
echo "🩺 nginx 설정 검증:"
docker compose -f docker-compose.prod.yml exec nginx nginx -t
echo ""
echo "🌐 접속 테스트:"
curl -s -o /dev/null -w "%{http_code}" http://localhost/health
echo " - Health check"
curl -s -o /dev/null -w "%{http_code}" http://localhost/admin/ 
echo " - Admin page"
EOF
    
    print_success "서버 상태 확인 완료"
}

# Display usage information
usage() {
    echo "Usage: $0 [EC2_IP] [--full-rebuild]"
    echo ""
    echo "Options:"
    echo "  EC2_IP         EC2 instance IP address (default: YOUR_EC2_IP)"
    echo "  --full-rebuild Full rebuild all containers (slower but safer)"
    echo ""
    echo "Examples:"
    echo "  $0                           # Quick update to default IP"
    echo "  $0 1.2.3.4                 # Quick update to custom IP"
    echo "  $0 1.2.3.4 --full-rebuild  # Full rebuild to custom IP"
}

# Main execution
main() {
    print_status "🚀 MES 서버 업데이트 시작"
    print_status "대상 서버: $EC2_IP"
    
    if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
        usage
        exit 0
    fi
    
    check_prerequisites
    upload_configs
    apply_updates
    check_status
    
    print_success "🎉 서버 업데이트 완료!"
    print_status "접속 정보:"
    print_status "  - 웹사이트: http://$EC2_IP"
    print_status "  - 관리자: http://$EC2_IP/admin"
    print_status "  - API: http://$EC2_IP/api/"
}

# Run main function
main "$@"