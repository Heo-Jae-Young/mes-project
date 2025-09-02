# Server Management Scripts

이 디렉토리에는 HACCP MES 프로젝트의 개발 서버 관리를 위한 자동화 스크립트들이 있습니다.

## 📜 Available Scripts

### restart_servers.sh
전체 개발 환경(백엔드 + 프론트엔드)을 재시작합니다.
```bash
./scripts/restart_servers.sh
```

### stop_servers.sh  
모든 개발 서버를 안전하게 중지합니다.
```bash
./scripts/stop_servers.sh
```

### check_servers.sh
서버 상태를 종합적으로 확인하고 진단합니다.
```bash
./scripts/check_servers.sh
```

## 🚀 Quick Start

```bash
# 개발 시작
./scripts/restart_servers.sh

# 상태 확인  
./scripts/check_servers.sh

# 개발 종료
./scripts/stop_servers.sh
```

## 📚 Documentation

자세한 사용법과 문제 해결 방법은 다음 문서를 참고하세요:
- `../docs/SERVER_SCRIPTS.md` - 스크립트 상세 가이드
- `../CLAUDE.md` - 프로젝트 전체 가이드