# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HACCP 기반 식품 안전 규정 준수 MES (Manufacturing Execution System) SaaS 프로젝트. Django REST Framework와 React를 사용한 풀스택 웹 애플리케이션.

## Technology Stack

**Backend:**
- Django 5.2.5 + Django REST Framework 3.16
- JWT Authentication (djangorestframework-simplejwt)
- MariaDB (Docker container)
- Python 3.12.7
- Testing: pytest-django + pytest-cov

**Frontend:**
- React 18+
- Axios for API communication
- Tailwind CSS
- React Router DOM

**Infrastructure:**
- Docker Compose for development
- Nginx for production (planned)

## Development Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.12.7 (managed via asdf)
- Node.js 18+ and npm

### Quick Start
```bash
# 1. Clone and setup
git clone <repository-url>
cd mes-project

# 2. Start MariaDB
docker-compose up -d db

# 3. Backend setup
cd backend
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Update with actual values

# 4. Database migration and seed data
python manage.py migrate
python manage.py seed_data --clear

# 5. Frontend setup
cd ../frontend
npm install

# 6. Start both servers
./scripts/restart_servers.sh
```

### Detailed Setup Guide
**처음 설정하는 경우 반드시 읽어주세요:**
- `docs/DATABASE_SETUP.md`: 데이터베이스 초기 설정부터 운영까지 상세 가이드
- `docs/SERVER_SCRIPTS.md`: 서버 관리 자동화 스크립트 사용법

### Common Commands
- **데이터베이스 마이그레이션:** `python manage.py migrate`
- **관리자 계정 생성:** `python manage.py createsuperuser`
- **시드 데이터 로드:** `python manage.py seed_data --clear` (admin/admin123 계정 자동 생성)
- **테스트 실행:** `pytest` (pytest-django 사용)
- **개발 서버 실행:** `python manage.py runserver`

## Architecture Overview

### HACCP-Based Design
핵심 설계 원칙은 HACCP 7원칙을 디지털화하는 것:
1. 위해요소 분석 (Hazard Analysis)
2. 중요 관리점 결정 (Critical Control Points)
3. 한계 기준 설정 (Critical Limits)
4. 모니터링 체계 (Monitoring Systems)
5. 개선 조치 (Corrective Actions)
6. 검증 절차 (Verification)
7. 문서화 및 기록 유지 (Documentation)

### Database Models
- **User:** Role-based access control
- **Supplier:** Supplier management
- **RawMaterial:** Raw material catalog
- **MaterialLot:** Lot tracking for traceability
- **FinishedProduct:** Product definitions
- **ProductionOrder:** Manufacturing orders
- **CCP:** Critical Control Points definition
- **CCPLog:** Immutable HACCP monitoring logs

## Current Project Status

### 📊 Overall Progress
- **백엔드**: 98% (완료 - API, Service Layer, Tests)
- **프론트엔드**: 40% (기본 구조 + 로그인 + 대시보드)
- **배포**: 0% (미구현)

### ✅ Completed Features

**Backend Infrastructure**
- Django 5.2.5 + DRF + MariaDB Docker 연동
- JWT 인증 시스템 (`/api/token/`, `/api/token/refresh/`, `/api/token/verify/`)
- HACCP 모델 8개 구현 (User, Supplier, RawMaterial, MaterialLot, FinishedProduct, ProductionOrder, CCP, CCPLog)
- Service Layer 구현 (HaccpService, ProductionService, SupplierService)
- DRF API 구현 (ViewSets + Serializers + 권한 필터링)
- 대시보드 통계 API (`/api/statistics/`)
- HACCP 중요 알림 API (`/api/ccps/critical_alerts/`) 정상 작동
- 체계적인 테스트 아키텍처 (25개 단위 테스트 통과)

**Frontend Infrastructure**
- React 18+ 프로젝트 구조
- 로그인/로그아웃 기능 (JWT 인증)
- Context API 기반 전역 상태 관리
- 대시보드 페이지 (동적 데이터 연동)
- Axios 기반 API 클라이언트

### ⚠️ Known Issues
- 없음 (모든 핵심 API 정상 작동)

### 🎯 Next Steps

**단기 목표 (현재 작업)**
1. **CCP 로그 입력 폼**: 작업자가 중요관리점 데이터를 입력할 수 있는 UI
2. **생산 오더 관리**: 생산 시작/완료 처리 기능
3. **HACCP 컴플라이언스 리포트**: 상세 분석 및 시각화

**중기 목표**
1. **실시간 알림 시스템**: 중요 이탈 발생 시 즉시 알림
2. **모바일 반응형 UI**: 태블릿/모바일 환경 최적화
3. **데이터 시각화**: 차트 및 그래프 라이브러리 연동

**장기 목표**
1. **Docker 컨테이너화**: Django, React, MariaDB
2. **Nginx 설정**: 프로덕션 환경 구성
3. **클라우드 배포**: AWS/DigitalOcean 배포

## Environment Variables

Required `.env` file in backend directory:
```bash
SECRET_KEY="your-django-secret-key"
DEBUG=True
DATABASE_NAME=mes_db
DATABASE_USER=mes_user
DATABASE_PASSWORD=mes_password
DATABASE_HOST=127.0.0.1
DATABASE_PORT=3306
```

## Development Guidelines

- **Security First:** All CCP data must be immutable with audit trails
- **Traceability:** Implement complete forward/backward traceability
- **Compliance:** Follow food industry regulations (HACCP, FDA, etc.)
- **API Design:** RESTful APIs with proper authentication
- **Data Integrity:** Use database transactions for critical operations

## 📚 Documentation

### Backend Documentation
- `backend/docs/backend_data_flow.md`: HTTP 요청부터 데이터베이스까지의 전체 데이터 흐름
- `backend/docs/mermaid_syntax_guide.md`: Mermaid 다이어그램 작성 가이드
- `backend/docs/API_ROUTING.md`: Django DRF 라우팅 시스템 해설
- `backend/docs/SERVICE_LAYER.md`: Service Layer 패턴과 비즈니스 로직 구조
- `backend/docs/TESTING_GUIDE.md`: 테스트 아키텍처 및 실행 가이드

### Frontend Documentation
- `frontend/docs/frontend_data_flow.md`: 프론트엔드 데이터 요청 및 화면 표시 과정

### General Documentation
- `docs/DATABASE_SETUP.md`: 데이터베이스 초기 설정부터 운영까지 완전 가이드
- `docs/SERVER_SCRIPTS.md`: 서버 관리 자동화 스크립트 상세 가이드
- `docs/DEVELOPMENT_LOG.md`: 개발 이력 및 주요 학습 내용
- `docs/ARCHITECTURE_PATTERNS.md`: 코드 아키텍처 패턴 및 설계 원칙
- `docs/DEVELOPMENT_BEST_PRACTICES.md`: 개발 노하우 및 베스트 프랙티스

## Development Best Practices

### Commit Message Guidelines
- **WHY 먼저**: 왜 이 작업을 했는지 배경과 문제점 설명
- **WHAT 구체적으로**: 실제 구현한 클래스/메소드명 나열
- **HOW 경험담**: 삽질했던 부분과 해결 과정 솔직하게 기록
- **결과 요약**: 테스트 통과, 커버리지 등 정량적 결과
- Generated with [Claude Code] 같은 자동 생성 문구 사용 금지

### Code Architecture Patterns
- **Service Layer**: 비즈니스 로직을 service.py에서 처리, view는 얇게 유지
- **Repository Pattern**: 복잡한 쿼리 로직은 별도 repository 클래스로 분리
- **Custom Hooks**: API 호출, 상태 관리 로직을 훅으로 추상화
- **Context + Reducer**: 전역 상태 관리

## Quick Reference

### Server Management

#### 자동화 스크립트 (권장)
```bash
# 서버 재시작 (백엔드 + 프론트엔드)
./scripts/restart_servers.sh

# 서버 중지
./scripts/stop_servers.sh

# 서버 상태 확인
./scripts/check_servers.sh
```

#### 수동 실행
```bash
# 백엔드 단독 실행
cd backend && source venv/bin/activate && python manage.py runserver

# 프론트엔드 단독 실행  
cd frontend && npm start

# 포트 충돌 해결
lsof -t -i :8000 | xargs kill -9  # 백엔드 포트
lsof -t -i :3000 | xargs kill -9  # 프론트엔드 포트
```

### Testing
```bash
# 전체 테스트 실행
pytest -v

# 단위테스트만 실행
pytest -m "unit" -v

# 커버리지 리포트
pytest --cov=core --cov-report=html
```

### Database Management
```bash
# 시드 데이터 로드 (관리자 계정 포함)
python manage.py seed_data --clear

# 완전한 데이터베이스 리셋
docker-compose down -v
docker-compose up -d db
python manage.py migrate

# 데이터베이스 직접 접속
docker exec -it mes-mariadb mysql -u mes_user -p
```

**⚠️ 자세한 데이터베이스 설정 및 문제 해결은 `docs/DATABASE_SETUP.md` 참고**

**관리자 계정**: admin/admin123