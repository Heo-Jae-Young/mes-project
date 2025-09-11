# HACCP MES SaaS Platform

> 🏭 **HACCP 기반 제조 실행 시스템** - 식품 안전 규정 준수를 위한 디지털 MES 플랫폼

[![Live Demo](https://img.shields.io/badge/🚀%20Live%20Demo-Available-brightgreen)](http://52.78.61.106)
[![Backend Coverage](https://img.shields.io/badge/Backend%20Coverage-78%25-green)](backend/htmlcov/index.html)
[![E2E Tests](https://img.shields.io/badge/E2E%20Tests-100%25%20Complete-brightgreen)](#-testing--quality-진행-중)
[![Frontend Tests](https://img.shields.io/badge/Frontend%20Tests-Planned-yellow)](#testing-strategy--plan)
[![Architecture](https://img.shields.io/badge/Architecture-Service%20Layer%20+%20Custom%20Hooks-blue)](#-주요-아키텍처-혁신)

## 🎯 프로젝트 소개

식품 제조업체를 위한 **디지털 HACCP 관리 시스템**으로, HACCP 7원칙을 완전히 디지털화한 제조 실행 관리 플랫폼입니다.

### 🔥 **주요 아키텍처 혁신**

**백엔드 (Django + DRF)**

- 🏗️ **Service Layer 패턴** - 비즈니스 로직과 API 계층 완전 분리
- 📊 **Repository 패턴** - 복잡한 쿼리 로직 추상화
- 🔄 **FIFO 원자재 할당** - 유통기한 기반 선입선출 자동화
- 📈 **실시간 원가 계산** - BOM 기반 FIFO 가격 산정 알고리즘

**프론트엔드 (React)**

- ⚛️ **Custom Hook 패턴** - useEntityPage로 CRUD 로직 40% 코드 감소
- 🔌 **Service Adapter 패턴** - 기존 API와 호환성 보장
- 🎨 **컴포넌트 추상화** - 재사용 가능한 UI 패턴 구축

**배포 인프라 (Docker + AWS)**

- 🐳 **Docker 컨테이너화** - 멀티스테이지 빌드 및 프로덕션 최적화
- 🌐 **Nginx 리버스 프록시** - React/Django 통합 서빙 및 정적 파일 최적화
- 🚀 **AWS EC2 배포** - 완전 자동화된 배포 시스템, 최적화된 deploy.sh 스크립트

### 핵심 기능

**✅ 구현 완료**

- 🔍 **HACCP CCP 로그 관리 시스템** - 실시간 측정값 입력, 검증, 이탈 감지 및 목록 조회
- 📊 **대시보드 통계** - HACCP 준수율, 중요 이탈 건수, 진행중 생산 오더 실시간 표시
- 👥 **역할 기반 인증 시스템** - JWT 기반 Admin, Quality Manager, Operator 권한 제어
- 🗃️ **완전한 데이터 모델링** - User, CCP, CCPLog, ProductionOrder 등 8개 도메인 모델
- ⚙️ **Service Layer 아키텍처** - 비즈니스 로직 분리, 테스트 가능한 구조
- 🏭 **생산 오더 관리 시스템** - 생산 주문 생성/상태 관리/FIFO 원자재 할당/완료 처리
- 📦 **원자재 관리 시스템** - 원자재 입고/재고/유통기한 관리 기능
- 🔍 **고급 로트 관리 시스템** - 로트별 상세 정보/품질검사 상태 변경/사용 이력 추적/비활성화 처리
- 🍔 **제품 관리 시스템** - 완제품 정보 관리, 영양성분/알러지 정보, 버전 제어
- 🔧 **BOM 원가 계산 시스템** - BOM 기반 실시간 제품 원가 계산, FIFO 가격 산정, 상세 내역 분석
- 🏢 **공급업체 관리 시스템** - 공급업체 CRUD, 상세 페이지, 성과 지표, 검색/필터링
- 🎨 **일관된 UI/UX** - LoadingCard 컴포넌트, 통일된 테이블 스타일, 개선된 로딩 경험

- 🧪 **종합 테스트 시스템** - Backend 78% + E2E 100% 커버리지 달성
  - 백엔드 테스트: Models, Services, Serializers (265 tests passed)
  - E2E 테스트: Playwright 기반 실제 브라우저 CRUD 시나리오 검증
  - 통합 테스트: API 및 시리얼라이저 통합 검증

- 🚀 **프로덕션 배포 시스템** - AWS EC2 Docker 기반 완전 자동화
  - Docker Compose 프로덕션 환경 구성
  - Nginx 리버스 프록시 및 정적 파일 최적화  
  - Git 기반 자동 배포 및 완전한 문서화 (docs/AWS_EC2_DEPLOYMENT.md)
  - 실제 배포 검증 완료 (신규 EC2 인스턴스 테스트)

**🚧 개발 중 (우선순위별)**

**🔥 최우선 (Phase 1)**
- 🧪 **Frontend 테스트 시스템** - Custom Hook 및 비즈니스 로직 테스트

**⚡ 단기 목표 (Phase 2)**
- 🔄 **자동 롤백 시스템** - 배포 실패 시 이전 버전 자동 복구
- 🔄 **무중단 배포** - Rolling Update 및 헬스체크
- 🔔 **배포 알림 시스템** - Slack/Discord 연동
- 📊 **배포 모니터링** - 성능 및 상태 추적

**🚀 중장기 목표 (Phase 3)**  
- 📈 **HACCP 컴플라이언스 리포트** - 상세 분석 및 시각화
- 🚨 **실시간 알림 시스템** - WebSocket 기반 중요 이탈 즉시 알림
- 🏗️ **인프라 자동화** - Terraform 기반 IaC

## 🛠 기술 스택

**Backend:**

- Django 5.2.5 + Django REST Framework 3.16
- JWT Authentication (djangorestframework-simplejwt)
- MariaDB (Docker container)
- Python 3.12.7
- Service Layer Architecture
- 265개 단위/통합 테스트 (pytest-django) - 78% 커버리지

**Frontend:**

- React 18+ with React Hook Form + date-fns
- Axios API client with interceptors
- Tailwind CSS with responsive design
- React Router DOM
- Context API for global auth state management

**Infrastructure:**

- Docker Compose for development
- Nginx for production (planned)

## 🚀 빠른 시작

### 개발 환경 설정

#### 사전 요구사항

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
./scripts/local/restart-servers.sh
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

### 🚀 프로덕션 배포

AWS EC2에서 Docker 기반 프로덕션 배포를 위한 완전한 가이드를 제공합니다.

```bash
# 배포 문서 확인
cat docs/AWS_EC2_DEPLOYMENT.md

# 핵심 특징:
# - 실제 배포 경험 기반 완전한 문서화
# - Git 기반 자동 배포 시스템
# - Docker Compose 프로덕션 환경
# - Nginx 리버스 프록시 및 정적 파일 최적화
# - 단계별 상세 가이드 및 문제 해결법
```

**🌐 라이브 데모**: [http://52.78.61.106](http://52.78.61.106)
- 관리자 계정: `admin/admin123`
- 실제 AWS EC2 환경에서 구동 중

#### 🤖 GitHub Actions 자동 배포 (구현 완료)

GitHub Actions를 통한 완전 자동화된 CI/CD 파이프라인이 구축되어 있습니다:

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production
on:
  push:
    branches: [main]
    paths-ignore: ['docs/**', '*.md', '.gitignore']
  pull_request:
    branches: [main]
    paths-ignore: ['docs/**', '*.md', '.gitignore']

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root_password
          MYSQL_DATABASE: test_mes_db
        ports: ['3306:3306']
        options: --health-cmd="mysqladmin ping --silent"
    
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python 3.12.7
      uses: actions/setup-python@v5
    - name: Run backend tests with 70% coverage requirement
      run: pytest --cov=core --cov-fail-under=70
    - name: Build frontend (Node.js 23.7)
      run: cd frontend && npm install && npm run build

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    
    steps:
    - name: Deploy to EC2
      uses: appleboy/ssh-action@v1.0.3
      with:
        host: ${{ secrets.AWS_EC2_HOST }}
        username: ${{ secrets.AWS_EC2_USER }}
        key: ${{ secrets.AWS_EC2_PRIVATE_KEY }}
        timeout: 600s
        script: |
          cd /home/ubuntu/mes-project
          git fetch origin && git reset --hard origin/main
          chmod +x scripts/production/deploy.sh
          ./scripts/production/deploy.sh
```

**✅ 구현 완료된 CI/CD 파이프라인:**
- ✅ **자동 테스트** - PR/Push 시 pytest 실행 (70% 커버리지 요구)
- ✅ **프론트엔드 빌드 검증** - React 빌드 테스트
- ✅ **자동 배포** - main 브랜치 push 시 EC2 자동 배포  
- ✅ **데이터 보전** - 프로덕션 데이터 유지하면서 코드만 업데이트
- ✅ **배포 최적화** - 600초 타임아웃, 스마트 대기 시스템
- ✅ **Skip CI 지원** - `[skip ci]` 커밋 메시지로 배포 건너뛰기
- ⚠️ **롤백 시스템** - 미구현 (배포 실패 시 수동 복구 필요)

#### 🚀 고도화 배포 시스템 (장기 계획)

**Phase 2: 무중단 배포 & 모니터링 (다음 개발 목표)**
```yaml
# 자동 롤백 시스템 (계획)
- name: Deploy with rollback support
  run: |
    PREVIOUS_COMMIT=$(git rev-parse HEAD^)
    # Deploy new version
    if ! ./deploy.sh; then
      echo "Deployment failed, rolling back..."
      git reset --hard $PREVIOUS_COMMIT
      ./deploy.sh
    fi

# 무중단 롤링 배포 (계획)
strategy:
  type: RollingUpdate
  maxUnavailable: 0
  maxSurge: 1

# 헬스체크 기반 자동 롤백 (계획)
healthcheck:
  timeout: 30s
  retries: 3
  rollback_on_failure: true
```

**Phase 3: 엔터프라이즈급 배포**
- 🎯 **환경별 배포**: dev → staging → production
- 🔔 **Slack 알림**: 배포 상태 실시간 알림  
- 📊 **배포 대시보드**: 배포 이력 및 성능 모니터링
- 🛡️ **보안 스캔**: Docker 이미지 취약점 자동 검사
- 🏗️ **IaC (Terraform)**: 인프라도 코드로 관리

## 🎨 주요 구현 화면

### 🔐 로그인 시스템

- JWT 기반 인증 (자동 토큰 갱신)
- 역할별 권한 제어 (Admin, Quality Manager, Operator)

### 📊 대시보드

- **HACCP 준수율**: 실시간 계산된 규정 준수 비율
- **진행중 생산 오더**: 현재 진행 상태의 생산 주문 건수
- **중요 이탈 건수**: 최근 24시간 내 CCP 한계값 이탈 사례

### 📝 CCP 로그 관리

- **실시간 입력**: CCP 선택, 측정값 입력, 단위 설정
- **자동 검증**: 한계값 이탈 여부 자동 판단
- **목록 조회**: 페이지네이션, 권한별 필터링
- **중복 방지**: 1분 내 동일 CCP 중복 입력 차단

### 🏭 생산 오더 관리

- **생산 주문 생성**: react-hook-form 기반 완제품 선택, 수량/일정 입력
- **상태 관리**: planned → in_progress → completed 완전한 라이프사이클
- **FIFO 원자재 할당**: 유통기한 기준 선입선출 자동 재고 할당
- **실시간 제어**: 생산 시작/완료/일시정지/재개 버튼식 제어
- **진행률 추적**: 계획 대비 실제 생산량 시각화

### 🍔 제품 관리

- **제품 카탈로그**: 완제품 생성/조회/수정/삭제 (CRUD)
- **상세 정보 관리**: 기본정보, 사양, 영양성분, 알러지 정보
- **품질 정보**: 보관온도 범위, 유통기한, 포장형태, 중량
- **버전 관리**: 제품 버전별 이력 관리 및 활성화 상태 제어
- **일관성 있는 UI**: 기존 페이지와 동일한 디자인 패턴 적용

## 📖 문서

### 📋 주요 문서 (5개 카테고리)

- **[CLAUDE.md](./CLAUDE.md)** - 📚 **메인 개발 가이드** (개발 환경, 빠른 참조, 커밋 가이드라인)

**🏗️ 프로젝트 & 아키텍처**

- [docs/ARCHITECTURE_PATTERNS.md](./docs/ARCHITECTURE_PATTERNS.md) - 코드 아키텍처 패턴 및 설계 원칙

**🔧 기술 구현**

- [docs/SYSTEM_DATA_FLOW.md](./docs/SYSTEM_DATA_FLOW.md) - 백엔드/프론트엔드 전체 데이터 플로우 가이드
- [backend/docs/SERVICE_LAYER.md](./backend/docs/SERVICE_LAYER.md) - Service Layer 패턴과 비즈니스 로직 구조
- [backend/docs/TESTING_GUIDE.md](./backend/docs/TESTING_GUIDE.md) - 백엔드 테스트 아키텍처 및 실행 가이드
- [e2e_tests/README.md](./e2e_tests/README.md) - E2E 테스트 실행 가이드 (Playwright 브라우저 자동화)

**🛠️ 설정 & 운영**

- [docs/DATABASE_SETUP.md](./docs/DATABASE_SETUP.md) - 데이터베이스 초기 설정부터 운영까지 완전 가이드
- [docs/SERVER_SCRIPTS.md](./docs/SERVER_SCRIPTS.md) - 서버 관리 자동화 스크립트 상세 가이드

**📝 개발 가이드**

- [docs/DEVELOPMENT_BEST_PRACTICES.md](./docs/DEVELOPMENT_BEST_PRACTICES.md) - **커밋 가이드라인** 및 개발 베스트 프랙티스
- [docs/DEVELOPMENT_LOG.md](./docs/DEVELOPMENT_LOG.md) - 개발 이력 및 주요 학습 내용

## 🗂 프로젝트 구조

```
mes-project/
├── scripts/                 # 🆕 서버 관리 자동화 스크립트
│   ├── local/               # 로컬 개발용
│   │   ├── restart-servers.sh # 백엔드+프론트엔드 재시작
│   │   ├── stop-servers.sh    # 모든 서버 중지
│   │   └── check-servers.sh   # 서버 상태 종합 진단
│   └── production/          # 프로덕션 배포용
│       ├── deploy.sh        # AWS EC2 완전 자동화 배포
│       └── init-database.sql # MariaDB 초기화
├── backend/                 # Django 백엔드
│   ├── core/                # HACCP MES 핵심 앱
│   │   ├── models/          # 8개 도메인 모델 (User, CCP, Production 등)
│   │   ├── serializers/     # DRF 직렬화기
│   │   ├── services/        # Service Layer 비즈니스 로직
│   │   ├── views/           # API ViewSets
│   │   └── tests/           # 종합 테스트 시스템 (265 tests, 78% 커버리지)
│   │   │   ├── unit/        # 단위 테스트 (models, services, serializers)
│   │   │   ├── integration/ # 통합 테스트 (API, 시리얼라이저)
│   │   │   └── helpers/     # 테스트 헬퍼 및 픽스처
│   └── docs/                # 백엔드 기술 문서
├── frontend/                # React 프론트엔드
│   ├── src/
│   │   ├── components/      # 재사용 UI 컴포넌트
│   │   │   ├── common/      # 공통 컴포넌트 (LoadingCard, 통일된 UI)
│   │   │   ├── forms/       # 폼 컴포넌트 (CCPLogForm, ProductionOrderForm)
│   │   │   ├── lists/       # 목록 컴포넌트 (CCPLogList, ProductionOrderList)
│   │   │   ├── layout/      # 레이아웃 컴포넌트 (Header)
│   │   │   ├── production/  # 생산 관리 컴포넌트 (ProductionControls)
│   │   │   ├── materials/   # 원자재 관리 컴포넌트 (고급 로트 관리)
│   │   │   ├── products/    # 제품 관리 컴포넌트 (BOM, 원가계산)
│   │   │   └── suppliers/   # 공급업체 관리 컴포넌트
│   │   ├── pages/           # 페이지별 컴포넌트 (완전한 HACCP MES UI)
│   │   ├── hooks/           # 커스텀 훅 (useEntityPage - CRUD 로직 40% 감소)
│   │   ├── services/        # API 서비스 레이어 (도메인별 완전 구현)
│   │   ├── utils/           # 유틸리티 (dateFormatter)
│   │   └── context/         # 전역 상태 관리 (AuthContext)
│   └── docs/                # 프론트엔드 기술 문서
├── e2e_tests/               # E2E 테스트 스위트 (Playwright)
│   ├── crud.spec.js         # CRUD 시나리오 자동화 테스트
│   ├── package.json         # E2E 테스트 전용 의존성
│   ├── README.md            # E2E 테스트 실행 가이드
│   └── screenshots/         # 실패 시 자동 스크린샷
├── docs/                    # 포괄적인 프로젝트 문서화
│   ├── AWS_EC2_DEPLOYMENT.md      # AWS 배포 완전 가이드
│   ├── DATABASE_SETUP.md          # DB 설정 완전 가이드
│   ├── SERVER_SCRIPTS.md          # 자동화 스크립트 가이드
│   ├── PROJECT_ARCHITECTURE.md    # 프로젝트 구조 및 아키텍처
│   └── DEVELOPMENT_BEST_PRACTICES.md # 개발 베스트 프랙티스
├── docker-compose.yml       # MariaDB 개발환경
├── docker-compose.prod.yml  # 프로덕션 배포 환경
├── run-local-prod.sh       # 로컬 프로덕션 테스트
└── CLAUDE.md               # 메인 개발 가이드
```

## 🏗 개발 진행률

### ✅ Backend Development (완료)

- [x] Django 5.2.5 + DRF 환경 구성
- [x] MariaDB Docker 연동 및 설정
- [x] JWT 인증 시스템 (토큰 생성/갱신/검증)
- [x] HACCP 모델 8개 구현 (User, Supplier, CCP, CCPLog 등)
- [x] Service Layer 아키텍처 + 상수 관리 시스템
- [x] REST API 개발 (ViewSets + Serializers + 권한 필터링)
- [x] 대시보드 통계 API (`/api/statistics/`)
- [x] HACCP 중요 알림 API (`/api/ccps/critical_alerts/`)
- [x] **생산 관리 Service Layer**: FIFO 원자재 할당, Decimal 정밀 연산
- [x] **원자재 관리 API**: 입고/재고/유통기한 관리 시스템
- [x] **제품 관리 API**: 완제품 CRUD, 영양성분/알러지 정보 관리
- [x] **BOM 원가 계산 API**: FIFO 기반 실시간 원가 계산, 가격 산출 우선순위 알고리즘
- [x] **종합 테스트 시스템**: 265개 테스트, 78% 커버리지 달성
  - [x] 단위 테스트: Models, Services, Serializers, Authentication
  - [x] 통합 테스트: API 엔드포인트 및 시리얼라이저 검증
  - [x] Mock을 활용한 격리된 테스트 환경 구축
- [x] API 문서화 (Swagger UI)
- [x] 아키텍처 개선: 레이어별 책임 분리, 중복 코드 제거

### ✅ Frontend Development (완료)

- [x] React 18+ 프로젝트 구조
- [x] JWT 기반 로그인/로그아웃 (자동 토큰 갱신)
- [x] Context API 기반 전역 상태 관리
- [x] 대시보드 페이지 (실시간 통계 데이터 연동)
- [x] Axios 기반 API 클라이언트 (인터셉터, 에러 처리)
- [x] CCP 로그 관리 시스템: 입력 폼, 목록 조회, 페이지네이션
- [x] 네비게이션 시스템: Header 메뉴 및 라우팅 구조
- [x] **생산 오더 관리 UI**: 생성 폼, 목록, 상태별 제어 버튼, 진행률 시각화
- [x] **원자재 관리 UI**: 입고/재고 현황/유통기한 알림, 로트별 추적
- [x] **고급 로트 관리 UI**: 로트 상세 모달, 품질검사 상태 변경, 사용 이력 타임라인, 비활성화 처리
- [x] **제품 관리 UI**: 제품 CRUD, 영양성분 입력, 알러지 정보 관리
- [x] **BOM 원가 계산 UI**: 실시간 원가 표시, 상세 내역 모달, 미설정 제품 알림
- [x] **공급업체 관리 UI**: 완전한 CRUD, 상세 페이지, 성과 지표, 검색/필터링
- [x] **useEntityPage 커스텀 훅**: CRUD 로직 40% 코드 감소, 페이지별 일관성
- [x] **react-hook-form + date-fns**: 고급 폼 검증 및 날짜 처리
- [x] **LoadingCard + 통일된 UI**: 일관된 로딩 UI, 테이블 스타일 통합
- [ ] HACCP 컴플라이언스 리포트 (차트/시각화)

### 🧪 Testing & Quality (진행 중)

- [x] **Backend Testing (78% 커버리지)**: 265개 테스트 완료
  - [x] Unit Tests: Models, Services, Serializers 완전 커버리지
  - [x] Integration Tests: API 및 시리얼라이저 통합 검증
  - [x] Mock을 활용한 격리된 테스트 환경
  - [x] pytest-django + pytest-cov 테스트 프레임워크
- [x] **E2E Testing (100% 완료)**: 전체 사용자 시나리오 검증
  - [x] Playwright 기반 브라우저 자동화 테스트
  - [x] 실제 라이브 서버에서 CRUD 시나리오 검증
  - [x] 동적 테스트 데이터 생성으로 중복 방지
  - [x] 검증 실패 감지 및 스크린샷 자동 저장
  - [x] 데코레이터 패턴 기반 깔끔한 로깅 시스템
- [ ] **Frontend Unit Testing (0% 완료)**: 계획 단계
  - [ ] React 컴포넌트 테스트 (React Testing Library)
  - [ ] Custom Hook 테스트 (useEntityPage, useAuth 등)
  - [ ] API 연동 테스트 (Mock Service Worker)
- [ ] **API Testing**: ViewSets 단위 테스트 (CRUD 동작, 권한 검증)

### 🚀 DevOps & Infrastructure (진행 중)

- [x] **Docker 컨테이너화**: Django + React + MariaDB + Nginx 멀티 컨테이너
- [x] **프로덕션 환경 구성**: docker-compose.prod.yml, 멀티스테이지 빌드
- [x] **AWS EC2 배포**: 완전 자동화된 배포 시스템 (scripts/production/deploy.sh)
- [x] **Nginx 리버스 프록시**: React/Django 통합 서빙, 정적 파일 최적화
- [x] **실제 배포 검증**: 신규 EC2 인스턴스에서 처음부터 배포 테스트 완료
- [x] **배포 문서화**: 완전한 단계별 가이드 (docs/AWS_EC2_DEPLOYMENT.md)
- [x] **CI/CD Pipeline**: GitHub Actions 자동 테스트 및 배포 구현 완료
- [ ] **무중단 배포**: Rolling Update, Blue-Green 배포
- [ ] **모니터링**: Slack/Discord 알림, 성능 추적, 로그 관리

### 📋 Advanced Features (계획 중)

- [ ] **HACCP 컴플라이언스 리포트**: CCP별 준수율, 트렌드 분석, PDF/Excel 내보내기
- [ ] **실시간 알림 시스템**: WebSocket 기반 중요 이탈, 유통기한 임박 즉시 알림
- [ ] **MaterialLotUsage 모델**: 완전한 소비 이력 추적 시스템 (누가, 언제, 얼마나, 왜)
- [ ] **BOM 시스템 고도화**: 일괄 등록 (CSV/Excel), 버전 관리, 원가 변동 추이 분석
- [ ] **모바일 반응형**: 태블릿/모바일 최적화, PWA(Progressive Web App) 지원
- [ ] **인프라 자동화**: Terraform IaC, 환경별 배포 (dev → staging → production)

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

# 백엔드 테스트 (78% 커버리지)
pytest -v                      # 전체 테스트 실행 (265 tests)
pytest --cov=core --cov-report=html  # 커버리지 리포트

# E2E 테스트 (End-to-End 브라우저 테스트)
cd e2e_tests                    # E2E 테스트 디렉토리로 이동
npm install                     # Playwright 설치
npm run test:crud              # 브라우저 창에서 실행 (시각적 확인)
npm run test:crud-headless     # 백그라운드 실행 (빠름)

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
