# HACCP MES SaaS Platform

HACCP 기반 식품 안전 규정 준수를 위한 제조 실행 시스템(MES) SaaS 플랫폼

## 🎯 프로젝트 개요

식품 제조업체를 위한 디지털 HACCP 관리 시스템으로, HACCP 7원칙을 디지털화한 제조 실행 관리 플랫폼입니다.

### 핵심 기능 (구현 완료 ✅)
- 🔍 **HACCP 중요관리점(CCP) 모니터링** - 실시간 측정값 기록 및 이탈 감지
- 📊 **생산 관리 및 추적** - 생산 주문, 원자재 할당, 효율성 계산
- 🏭 **완전한 추적성(Traceability)** - 원자재 LOT부터 완제품까지 양방향 추적
- 👥 **역할 기반 접근 제어** - Admin, Quality Manager, Operator 권한 시스템
- 📋 **컴플라이언스 보고서** - HACCP 준수율 자동 계산 및 보고서 생성
- 🚨 **중요 알림 시스템** - CCP 이탈 시 즉시 알림 및 대응 조치

## 🛠 기술 스택

**Backend:**
- Django 5.2.5 + Django REST Framework 3.16
- JWT Authentication (djangorestframework-simplejwt)
- MariaDB (Docker container)
- Python 3.12.7
- Service Layer Architecture
- 25개 단위 테스트 (pytest-django)

**Frontend:**
- React 18+ (구현 완료)
- Axios for API communication
- Tailwind CSS
- React Router DOM
- Context API for state management

**Infrastructure:**
- Docker Compose for development
- Nginx for production (planned)

## 🚀 빠른 시작

### 사전 요구사항
- Docker & Docker Compose
- Python 3.12.7 (managed via asdf)
- Node.js 23.7.0 (managed via asdf)
- npm (included with Node.js)

### 🎬 자동화 스크립트 (권장)

```bash
# 1. 레포지토리 클론
git clone [repository-url]
cd mes-project

# 2. 환경 변수 설정
cp backend/.env.example backend/.env
# .env 파일의 DATABASE_HOST, SECRET_KEY 등을 실제 값으로 수정

# 3. 전체 환경 자동 시작 (MariaDB + Django + React)
./scripts/restart_servers.sh
```

### 📝 수동 설치 (문제 해결 시)

```bash
# 1. MariaDB 시작
docker-compose up -d db

# 2. 백엔드 설정
cd backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data --clear  # 샘플 데이터 + admin 계정

# 3. 프론트엔드 설정
cd ../frontend
npm install

# 4. 서버 실행
cd ../backend && python manage.py runserver &
cd ../frontend && npm start
```

### 🔗 접속 정보
- **프론트엔드**: http://localhost:3000
- **백엔드 API**: http://localhost:8000/api/
- **Swagger UI**: http://localhost:8000/api/docs/
- **Django Admin**: http://localhost:8000/admin/ (admin/admin123)

## 📖 문서

### 주요 문서
- [CLAUDE.md](./CLAUDE.md) - 프로젝트 메인 가이드 (개발 환경, Quick Reference)
- [docs/DATABASE_SETUP.md](./docs/DATABASE_SETUP.md) - 데이터베이스 초기 설정부터 운영까지 완전 가이드
- [docs/SERVER_SCRIPTS.md](./docs/SERVER_SCRIPTS.md) - 서버 관리 자동화 스크립트 상세 가이드

### 기술 문서
- [backend/docs/SERVICE_LAYER.md](./backend/docs/SERVICE_LAYER.md) - Service Layer 패턴과 비즈니스 로직 구조
- [backend/docs/TESTING_GUIDE.md](./backend/docs/TESTING_GUIDE.md) - 테스트 아키텍처 및 실행 가이드
- [docs/ARCHITECTURE_PATTERNS.md](./docs/ARCHITECTURE_PATTERNS.md) - 코드 아키텍처 패턴 및 설계 원칙

### 개발 문서
- [docs/DEVELOPMENT_BEST_PRACTICES.md](./docs/DEVELOPMENT_BEST_PRACTICES.md) - 개발 노하우 및 베스트 프랙티스
- [docs/DEVELOPMENT_LOG.md](./docs/DEVELOPMENT_LOG.md) - 개발 이력 및 주요 학습 내용

## 🗂 프로젝트 구조

```
mes-project/
├── scripts/                 # 🆕 서버 관리 자동화 스크립트
│   ├── restart_servers.sh   # 전체 환경 재시작
│   ├── stop_servers.sh      # 모든 서버 중지
│   └── check_servers.sh     # 서버 상태 종합 진단
├── backend/                 # Django 백엔드 (완료)
│   ├── core/                # HACCP MES 핵심 앱
│   │   ├── models/          # 8개 도메인 모델 (User, CCP, Production 등)
│   │   ├── serializers/     # DRF 직렬화기
│   │   ├── services/        # Service Layer 비즈니스 로직
│   │   ├── views/           # API ViewSets
│   │   └── tests/           # 25개 단위 테스트
│   └── docs/                # 백엔드 기술 문서
├── frontend/                # React 프론트엔드 (기본 완료)
│   ├── src/
│   │   ├── components/      # 재사용 UI 컴포넌트
│   │   ├── pages/           # 페이지별 컴포넌트 (Login, Dashboard)
│   │   ├── services/        # API 클라이언트 (Axios)
│   │   └── context/         # 전역 상태 관리
│   └── docs/                # 프론트엔드 기술 문서
├── docs/                    # 프로젝트 일반 문서
│   ├── DATABASE_SETUP.md    # DB 설정 완전 가이드
│   └── SERVER_SCRIPTS.md    # 자동화 스크립트 가이드
├── docker-compose.yml       # MariaDB 개발환경
└── CLAUDE.md               # 메인 개발 가이드
```

## 🏗 개발 진행률

### ✅ Backend (98% 완료)
- [x] Django 5.2.5 + DRF 환경 구성
- [x] MariaDB Docker 연동 및 설정
- [x] JWT 인증 시스템 (`/api/token/`)
- [x] HACCP 모델 8개 구현 (User, Supplier, CCP, CCPLog 등)
- [x] Service Layer 아키텍처 구현
- [x] REST API 개발 (ViewSets + Serializers)
- [x] 대시보드 통계 API (`/api/statistics/`)
- [x] HACCP 중요 알림 API (`/api/ccps/critical_alerts/`)
- [x] 25개 단위 테스트 작성 및 통과
- [x] API 문서화 (Swagger UI)

### ✅ Frontend (40% 완료)
- [x] React 18+ 프로젝트 구조
- [x] 로그인/로그아웃 기능 (JWT 인증)
- [x] Context API 기반 전역 상태 관리
- [x] 대시보드 페이지 (동적 데이터 연동)
- [x] Axios 기반 API 클라이언트
- [ ] CCP 로그 입력 폼
- [ ] 생산 오더 관리 UI
- [ ] HACCP 컴플라이언스 리포트

### ❌ Infrastructure (0% 완료)
- [ ] Docker 컨테이너화
- [ ] Nginx 프로덕션 환경
- [ ] 클라우드 배포 (AWS/DigitalOcean)

## 📋 주요 명령어

### 🚀 자동화 스크립트 (권장)
```bash
./scripts/restart_servers.sh    # 전체 환경 재시작
./scripts/check_servers.sh      # 서버 상태 확인
./scripts/stop_servers.sh       # 모든 서버 중지
```

### 🛠 개발 명령어
```bash
# 데이터베이스
python manage.py migrate         # 마이그레이션 적용
python manage.py seed_data --clear  # 샘플 데이터 + 관리자 계정 생성
python manage.py check          # 설정 검증

# 테스트
pytest -v                      # 전체 테스트 실행
pytest --cov=core --cov-report=html  # 커버리지 리포트

# Docker
docker-compose up -d db         # MariaDB만 실행
docker-compose ps              # 컨테이너 상태 확인
docker exec -it mes-mariadb mysql -u mes_user -p  # DB 직접 접속
```

## 🤝 기여 방법

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 문의

프로젝트 관련 문의사항이 있으시면 Issue를 생성해 주세요.