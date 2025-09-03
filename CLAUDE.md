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
- **백엔드**: 99% (완료 - API, Service Layer, Tests, 아키텍처 개선)
- **프론트엔드**: 60% (기본 구조 + 로그인 + 대시보드 + CCP 로그 관리)
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
- **🆕 레이어별 책임 분리 개선**: 중복 코드 제거, 올바른 아키텍처 적용
- **🆕 상수 관리**: 하드코딩된 값들을 `constants.py`로 분리

**Frontend Infrastructure**  
- React 18+ 프로젝트 구조
- 로그인/로그아웃 기능 (JWT 인증)
- Context API 기반 전역 상태 관리
- 대시보드 페이지 (동적 데이터 연동)
- Axios 기반 API 클라이언트
- **🆕 CCP 로그 관리 기능**: 입력 폼, 목록 조회, 필터링, 페이지네이션
- **🆕 네비게이션 시스템**: Header 메뉴와 라우팅 구조 완성

### ⚠️ Known Issues
- 없음 (모든 핵심 API 정상 작동, 아키텍처 개선 완료)

### 🎯 Next Steps

**단기 목표 (우선순위)**
1. **생산 오더 관리**: 생산 시작/완료 처리 기능
   - 생산 오더 상태 관리 (planned → in_progress → completed)
   - 생산 진행률 추적 및 업데이트 API
   - 프론트엔드 생산 관리 페이지 구현
2. **HACCP 컴플라이언스 리포트**: 상세 분석 및 시각화
   - CCP별 규정 준수율 대시보드
   - 시간대별 트렌드 차트 구현
   - PDF 리포트 생성 기능
3. **실시간 알림 개선**: WebSocket 기반 실시간 알림
   - Django Channels 설정
   - 중요 이탈 발생 시 즉시 알림

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

### 🏗️ Project & Architecture (프로젝트 및 아키텍처)
**📖 언제 보나요?** 프로젝트 전체 구조를 이해하거나, 새로운 아키텍처 패턴을 도입할 때  
**✍️ 언제 기록하나요?** 주요 설계 결정, 기술 스택 변경, 아키텍처 패턴 도입 시

- `docs/PROJECT_ARCHITECTURE.md`: 전체 프로젝트 구조 및 모노레포 가이드
- `docs/ARCHITECTURE_PATTERNS.md`: 코드 아키텍처 패턴 및 설계 원칙  
- `docs/TECH_STACK_DECISIONS.md`: 기술 스택 선택 근거 및 의사결정 과정

### 🔧 Technical Implementation (기술 구현)
**📖 언제 보나요?** 새로운 기능 구현하거나, 기존 코드 수정할 때  
**✍️ 언제 기록하나요?** 복잡한 구현 패턴, 데이터 플로우, API 설계 완료 시

- `docs/SYSTEM_DATA_FLOW.md`: 백엔드/프론트엔드 전체 데이터 플로우 및 Mermaid 문법 가이드
- `backend/docs/SERVICE_LAYER.md`: Service Layer 패턴과 비즈니스 로직 구조
- `backend/docs/API_ROUTING.md`: Django DRF 라우팅 시스템 해설
- `backend/docs/TESTING_GUIDE.md`: 테스트 아키텍처 및 실행 가이드

### 🛠️ Setup & Operations (설정 및 운영)  
**📖 언제 보나요?** 개발 환경 구축하거나, 서버 관리할 때  
**✍️ 언제 기록하나요?** 환경 설정 방법 변경, 새로운 운영 스크립트 추가 시

- `docs/DATABASE_SETUP.md`: 데이터베이스 초기 설정부터 운영까지 완전 가이드
- `docs/SERVER_SCRIPTS.md`: 서버 관리 자동화 스크립트 상세 가이드

### 📝 Development Guide (개발 가이드)
**📖 언제 보나요?** 개발 프로세스 확인하거나, 과거 작업 내용 참고할 때  
**✍️ 언제 기록하나요?** 주요 기능 완성, 새로운 개발 노하우 습득, 베스트 프랙티스 발견 시

- `docs/DEVELOPMENT_LOG.md`: 개발 이력 및 주요 학습 내용
- `docs/DEVELOPMENT_BEST_PRACTICES.md`: 개발 노하우 및 베스트 프랙티스

### 🐛 Problem Solving (문제 해결)
**📖 언제 보나요?** 비슷한 에러나 문제 상황에 직면했을 때  
**✍️ 언제 기록하나요?** 해결하기 어려웠던 버그, 환경 이슈, 호환성 문제 해결 후

- `docs/TAILWINDCSS_TROUBLESHOOTING.md`: TailwindCSS 버전 호환성 이슈 해결 기록

## Development Best Practices

### Commit Message Guidelines

**기본 구조**: WHY → WHAT → HOW → 결과

- **WHY**: 왜 이 작업을 했는지 배경과 문제점 설명
- **WHAT**: 실제 구현한 클래스/메소드명을 구체적으로 나열
- **HOW**: 문제 → 해결책 → **결정 근거** 순으로 기술 (가장 중요)
- **결과**: 테스트 통과, 커버리지 등 정량적 결과

**핵심**: "왜 이 방법을 선택했는가?"에 대한 명확한 설명 포함

📚 **상세한 가이드라인**: `docs/DEVELOPMENT_BEST_PRACTICES.md` 참조

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