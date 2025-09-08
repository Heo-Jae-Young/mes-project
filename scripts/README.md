# Server Management Scripts

이 디렉토리에는 HACCP MES 프로젝트의 서버 관리를 위한 자동화 스크립트들이 있습니다.

## 📁 Directory Structure

```
scripts/
├── local/          # 로컬 개발 환경용 스크립트
├── production/     # 프로덕션 배포용 스크립트  
└── README.md       # 이 파일
```

## 🛠️ Local Development Scripts (`./local/`)

로컬 개발 환경에서 Django + React 서버 관리:

### restart-servers.sh
전체 개발 환경(백엔드 + 프론트엔드)을 재시작합니다.
```bash
./scripts/local/restart-servers.sh
```

### stop-servers.sh  
모든 개발 서버를 안전하게 중지합니다.
```bash
./scripts/local/stop-servers.sh
```

### check-servers.sh
서버 상태를 종합적으로 확인하고 진단합니다.
```bash
./scripts/local/check-servers.sh
```

## 🚀 Production Deployment Scripts (`./production/`)

AWS EC2 프로덕션 환경 배포 및 관리:

### deploy.sh
전체 프로덕션 시스템을 자동 배포합니다.
```bash
./scripts/production/deploy.sh [--ssl] [--backup]
```

### update-server.sh
설정 변경사항을 서버에 수동으로 적용합니다.
```bash
./scripts/production/update-server.sh [EC2_IP] [--full-rebuild]
```

### init-database.sql
MariaDB 프로덕션 초기화 SQL 스크립트입니다.

## 🚀 Quick Start

### 로컬 개발
```bash
# 개발 시작
./scripts/local/restart-servers.sh

# 상태 확인  
./scripts/local/check-servers.sh

# 개발 종료
./scripts/local/stop-servers.sh
```

### 프로덕션 배포
```bash
# 전체 배포
./scripts/production/deploy.sh

# 설정만 업데이트
./scripts/production/update-server.sh YOUR_EC2_IP
```

## 📚 Documentation

자세한 사용법과 문제 해결 방법은 다음 문서를 참고하세요:
- `../docs/SERVER_SCRIPTS.md` - 스크립트 상세 가이드
- `../CLAUDE.md` - 프로젝트 전체 가이드