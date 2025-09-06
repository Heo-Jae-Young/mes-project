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

**계획된 모델:**
- **MaterialLotUsage:** 로트별 상세 소비 이력 (언제, 누가, 얼마나, 왜, 어떤 생산오더에서)

## Current Project Status

### 📊 Overall Progress

- **백엔드**: 95% (핵심 API + 생산 관리 + 원자재 관리 + 제품 관리 완료)
- **프론트엔드**: 98% (인증 + 대시보드 + CCP 로그 + 생산 관리 + 원자재 관리 + 제품 관리 + 공급업체 관리 완료)
- **배포**: 0% (미구현)

### 🏗️ Technical Infrastructure

**Backend Stack**

- Django 5.2.5 + Django REST Framework 3.16
- MariaDB (Docker container)
- JWT Authentication (djangorestframework-simplejwt)
- Service Layer Architecture Pattern
- Repository Pattern for complex queries
- pytest-django + pytest-cov testing framework

**Frontend Stack**

- React 18+ with modern hooks
- Axios API client with JWT interceptors
- Context API for global state management
- Tailwind CSS for styling
- date-fns for date handling
- react-hook-form for form validation
- @heroicons/react for icons

**Data Models (HACCP-based)**

- User (role-based access control)
- Supplier, RawMaterial, MaterialLot (supply chain)
- FinishedProduct, ProductionOrder (manufacturing)
- CCP, CCPLog (HACCP compliance)

### ✅ Implemented Features

**Authentication & Authorization**

- JWT 기반 로그인/로그아웃 (`/api/token/`, `/api/token/refresh/`, `/api/token/verify/`)
- 역할별 권한 제어 (admin, quality_manager, operator)
- 보호된 라우트 및 API 엔드포인트

**Dashboard & Analytics**

- 실시간 대시보드 (`/dashboard`)
- 통계 API (`/api/statistics/`)
- HACCP 중요 알림 (`/api/ccps/critical_alerts/`)

**HACCP Compliance Management**

- CCP(Critical Control Point) 정의 및 관리
- CCP 로그 입력/조회/필터링 (`/ccp-logs`)
- 한계 기준 초과 시 자동 알림
- 완전한 CRUD 및 페이지네이션

**Production Order Management**

- 생산 주문 생성/조회/수정 (`/production`)
- 상태 관리: planned → in_progress → completed
- 생산 시작/완료/일시정지/재개 처리
- 원자재 가용성 검증 및 FIFO 할당 (Service Layer 패턴)
- 실시간 진행률 시각화 및 필터링/검색
- 완제품 선택 드롭다운 및 폼 유효성 검증

**Raw Material Management**

- 원자재 카탈로그 CRUD (`/materials`)
- 로트별 입고/재고/소비 추적 시스템
- 백엔드 집계 기반 실시간 재고 현황 표시
- 품질검사 결과 기반 자동 상태 관리
- 유통기한 임박 알림 및 재고 부족 모니터링
- FIFO 원칙 기반 재고 소비 처리
- 완전한 추적성 (lot-to-lot traceability)

**Advanced Lot Management System** ✅

- 로트별 상세 정보 조회 모달 (로트 번호 클릭)
- 품질검사 상태 변경 기능 (pending → pass/fail)
- 사용 이력 및 추적성 타임라인 시각화
- 로트 비활성화/폐기 처리 (expired/rejected)
- 단가 정보 및 현재 가치 계산 표시
- HACCP 추적성 정보 완전 표시

**Product Management**

- 완제품 카탈로그 CRUD (`/products`)
- 제품 정보 관리: 기본정보, 사양, 영양성분, 알러지 정보
- 제품 버전 관리 및 활성화 상태 제어
- 보관 조건 설정 (온도 범위, 유통기한)
- 포장 형태 및 중량 정보 관리
- 기존 UI 패턴과 일관성 있는 디자인 (blue 색상 스키마)

**BOM (Bill of Materials) Management**

- 제품별 원자재 소요량 정의 및 관리 (`/api/bom/`)
- 제품 관리 페이지에서 통합 BOM 설정 UI
- BOM 기반 생산 시 자동 원자재 소요량 계산
- FIFO 방식 원자재 할당 및 품질검사 합격품만 사용
- BOM CRUD: 생성, 조회, 수정, 삭제 및 실시간 유효성 검증
- 생산 주문 생성 시 BOM 설정 여부 자동 검증

**Product Cost Calculation System**

- BOM 기반 제품 원가 자동 계산 (`/api/products/{id}/cost/`)
- FIFO 원칙 기반 실시간 원자재 가격 산정
- 가격 산출 우선순위: 현재재고 → 최근30일평균 → 전체평균
- 제품 목록에서 실시간 예상 원가 표시 (색상 코딩)
- 원가 상세 내역 모달: 원자재별 분해, 가격 산출 방식, 경고사항
- BOM 미설정 제품 알림 및 필터링 기능
- 완전한 HACCP 추적성을 통한 정확한 원가 계산

**Supplier Management System** ✅

- 완전한 공급업체 관리 UI (`/suppliers`)
- 공급업체 등록/조회/수정/삭제 기능 (CRUD)
- 공급업체 상세 페이지 (성과 요약, 원자재 목록, 편집 기능)
- 검색 및 상태별 필터링 (활성/비활성/정지)
- 공급업체별 성과 지표 (품질 합격률, 납기 준수율)
- 일관된 UI/UX 패턴 및 반응형 디자인

**Enhanced User Experience** ✅

- 개선된 대시보드 로딩 (전체 로딩 → 개별 위젯별 로딩)
- LoadingCard 컴포넌트 도입으로 일관된 로딩 UI
- 모든 테이블 스타일 통일 (일관된 테두리, 배경, 그림자)
- BOM 알림 UX 개선 (검색과 독립적인 전역 알림)

### ⚠️ Current Limitations

- **BOM 고급 기능 미구현**: BOM 일괄 등록, 버전 관리 등
- **실시간 알림 시스템**: WebSocket 기반 즉시 알림 미구현

### 📋 Planned Features

**최우선 (현재 작업)**

1. **MaterialLotUsage 모델 및 상세 소비 이력 시스템** 📝
   - MaterialLot 소비 기록을 별도 테이블로 완전 추적
   - 하이브리드 접근법: MaterialLot.quantity_current + MaterialLotUsage 이력
   - 누가, 언제, 얼마나, 왜, 어떤 생산오더에서 소비했는지 완전 기록
   - HACCP 감사 추적 (audit trail) 완벽 지원
   - 비동기 로깅으로 성능 최적화

2. **HACCP 컴플라이언스 리포트** 📊
   - CCP별 규정 준수율 대시보드 (chart.js 활용)
   - 시간대별 트렌드 차트 및 분석
   - PDF/Excel 리포트 내보내기

**중기 목표**

3. **BOM 시스템 고도화** 🔧
   - BOM 일괄 등록 기능 (CSV/Excel)
   - BOM 버전 관리 및 이력 추적
   - 원가 변동 추이 분석

4. **실시간 알림 시스템** 🔔
   - WebSocket 기반 실시간 알림 (Django Channels)
   - 중요 이탈/유통기한 임박 등 즉시 알림

5. **모바일 반응형 UI** 📱
   - 태블릿/모바일 환경 최적화
   - PWA(Progressive Web App) 지원

**장기 목표**

6. **배포 및 운영** 🚀
   - Docker 컨테이너화 (Django, React, MariaDB)
   - Nginx 프로덕션 환경 구성
   - 클라우드 배포 (AWS/DigitalOcean)

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

**자동 생성 문구 금지**

```
❌ 🤖 Generated with [Claude Code](https://claude.ai/code)
```

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
