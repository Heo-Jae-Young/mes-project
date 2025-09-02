# Server Management Scripts

이 문서는 개발 서버 관리를 위한 자동화 스크립트들의 사용법과 내부 동작을 설명합니다.

## 📜 사용 가능한 스크립트

### 1. restart_servers.sh - 서버 재시작
전체 개발 서버(백엔드 + 프론트엔드)를 재시작하는 스크립트입니다.

```bash
./scripts/restart_servers.sh
```

**동작 과정:**
1. 기존 백엔드 서버 종료 (포트 8000)
2. 기존 프론트엔드 서버 종료 (포트 3000)
3. 백엔드 서버 시작 (Django runserver + venv 활성화)
4. 프론트엔드 서버 시작 (npm start)
5. 서버 응답 상태 확인
6. 유용한 링크 제공

**출력 예시:**
```
-- 서버 재시작 스크립트 시작 --
백엔드 서버 (포트 8000) 종료 시도...
백엔드 서버 (PID: 12345) 종료 완료.
프론트엔드 서버 (포트 3000) 종료 시도...
프론트엔드 서버 (PID: 12346) 종료 완료.

-- 서버 재시작 시작 --
백엔드 서버 시작 중...
백엔드 서버 시작 완료 (PID: 12347)
프론트엔드 서버 시작 중...
프론트엔드 서버 시작 완료 (PID: 12348)

-- 서버 상태 확인 --
✅ 백엔드 서버 (http://localhost:8000) 정상 작동
✅ 프론트엔드 서버 (http://localhost:3000) 정상 작동

-- 서버 재시작 스크립트 완료 --
🌐 브라우저에서 http://localhost:3000 에 접속하여 확인해주세요.
📚 API 문서: http://localhost:8000/api/docs/
```

### 2. stop_servers.sh - 서버 중지
모든 개발 서버를 중지하는 스크립트입니다.

```bash
./scripts/stop_servers.sh
```

**동작 과정:**
1. 백엔드 서버 프로세스 탐지 및 종료
2. 프론트엔드 서버 프로세스 탐지 및 종료
3. 종료 상태 확인

**출력 예시:**
```
-- 서버 중지 스크립트 시작 --
백엔드 서버 (포트 8000) 종료 시도...
✅ 백엔드 서버 (PID: 12347) 종료 완료
프론트엔드 서버 (포트 3000) 종료 시도...
✅ 프론트엔드 서버 (PID: 12348) 종료 완료

-- 서버 중지 스크립트 완료 --
모든 개발 서버가 중지되었습니다.
```

### 3. check_servers.sh - 서버 상태 확인
현재 서버 상태를 종합적으로 확인하는 스크립트입니다.

```bash
./scripts/check_servers.sh
```

**확인 항목:**
1. 포트별 프로세스 실행 상태
2. HTTP 응답 확인
3. JWT 인증 테스트
4. 유용한 링크 제공

**출력 예시:**
```
-- 서버 상태 확인 --
📋 실행 중인 프로세스:
  🖥️  백엔드 서버: PID 12347 (포트 8000)
  🌐 프론트엔드 서버: PID 12348 (포트 3000)

🔍 HTTP 응답 확인:
  ✅ 백엔드 API (http://localhost:8000/api/) 정상 응답
  ✅ 프론트엔드 (http://localhost:3000) 정상 응답

🔐 JWT 인증 테스트:
  ✅ JWT 토큰 발급 정상

-- 상태 확인 완료 --
📚 유용한 링크:
  - 프론트엔드: http://localhost:3000
  - 백엔드 API: http://localhost:8000/api/
  - Swagger UI: http://localhost:8000/api/docs/
  - Django Admin: http://localhost:8000/admin/ (admin/admin123)
```

## 🔧 기술적 세부사항

### 사용된 명령어들

**프로세스 탐지:**
```bash
lsof -t -i :8000  # 포트 8000을 사용하는 프로세스 ID 조회
lsof -t -i :3000  # 포트 3000을 사용하는 프로세스 ID 조회
```

**프로세스 종료:**
```bash
kill -9 $PID     # 강제 종료 (SIGKILL)
```

**백그라운드 실행:**
```bash
command &        # 백그라운드에서 실행
$!              # 마지막 백그라운드 프로세스의 PID
```

**HTTP 응답 확인:**
```bash
curl -s -f http://localhost:8000/api/  # 조용한 모드, 실패 시 에러 코드 반환
```

### 개선된 부분들

**1. 가상환경 활성화**
```bash
# Before: 가상환경 활성화 누락
python manage.py runserver

# After: 가상환경 자동 활성화
source venv/bin/activate && python manage.py runserver
```

**2. 경로 문제 해결**
```bash
# Before: 상대 경로 문제 가능성
cd frontend && npm start

# After: 명확한 경로 이동
cd ../frontend && npm start
```

**3. 프로세스 ID 추적**
```bash
# Before: 프로세스 ID 불명
python manage.py runserver &

# After: PID 추적 및 표시
python manage.py runserver &
BACKEND_PID=$!
echo "백엔드 서버 시작 완료 (PID: $BACKEND_PID)"
```

**4. 상태 확인 강화**
- HTTP 응답 확인
- JWT 토큰 발급 테스트
- 실시간 프로세스 상태 표시

## 🚨 문제 해결

### 일반적인 문제들

**1. 포트 충돌**
```bash
# 문제: 포트가 이미 사용 중
Error: That port is already in use.

# 해결: 수동으로 프로세스 종료
lsof -t -i :8000 | xargs kill -9
lsof -t -i :3000 | xargs kill -9
```

**2. 가상환경 문제**
```bash
# 문제: venv 경로를 찾을 수 없음
source: venv/bin/activate: No such file or directory

# 해결: 가상환경 재생성
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. 권한 문제**
```bash
# 문제: 스크립트 실행 권한 없음
Permission denied: ./restart_servers.sh

# 해결: 실행 권한 부여
chmod +x restart_servers.sh
chmod +x stop_servers.sh
chmod +x check_servers.sh
```

**4. 서버 시작 실패**
```bash
# 문제 확인
./check_servers.sh

# 수동 디버깅
cd backend
source venv/bin/activate
python manage.py check
python manage.py runserver

cd ../frontend
npm install
npm start
```

## 💡 사용 팁

### 개발 워크플로우
```bash
# 1. 개발 시작 시
./scripts/restart_servers.sh

# 2. 개발 중간에 상태 확인
./scripts/check_servers.sh

# 3. 개발 종료 시
./scripts/stop_servers.sh
```

### 디버깅 모드
```bash
# 백엔드 로그 확인
cd backend && source venv/bin/activate && python manage.py runserver

# 프론트엔드 로그 확인  
cd frontend && npm start
```

### 성능 최적화
- 스크립트는 병렬 실행으로 서버 시작 시간 단축
- 적절한 대기 시간으로 안정성 확보
- HTTP 응답 확인으로 실제 작동 여부 검증

이러한 스크립트들을 통해 개발 환경 설정과 관리가 훨씬 편리해집니다!