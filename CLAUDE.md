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

**Frontend:** (Planned)
- React 18+ 
- Axios for API communication

**Infrastructure:**
- Docker Compose for development
- Nginx for production (planned)

## Development Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.12.7 (managed via asdf)

### Quick Start
```bash
# 1. Start MariaDB
docker-compose up -d db

# 2. Backend setup
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 3. Environment setup
cp .env.example .env  # Update with actual values

# 4. Database migration
python manage.py migrate

# 5. Run development server
python manage.py runserver
```

### Common Commands
- **Database migration:** `python manage.py migrate`
- **Create migrations:** `python manage.py makemigrations`
- **Create superuser:** `python manage.py createsuperuser`
- **Run server:** `python manage.py runserver`
- **Check configuration:** `python manage.py check`

## Architecture Notes

### HACCP-Based Design
핵심 설계 원칙은 HACCP 7원칙을 디지털화하는 것:
1. 위해요소 분석 (Hazard Analysis)
2. 중요 관리점 결정 (Critical Control Points)
3. 한계 기준 설정 (Critical Limits)
4. 모니터링 체계 (Monitoring Systems)
5. 개선 조치 (Corrective Actions)
6. 검증 절차 (Verification)
7. 문서화 및 기록 유지 (Documentation)

### Database Models (Planned)
- **User:** Role-based access control
- **Supplier:** Supplier management
- **RawMaterial:** Raw material catalog
- **MaterialLot:** Lot tracking for traceability
- **FinishedProduct:** Product definitions
- **ProductionOrder:** Manufacturing orders
- **CCP:** Critical Control Points definition
- **CCPLog:** Immutable HACCP monitoring logs

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

## Development Log

### 2024-09-01: Django Backend 초기 설정 완료
- Django 5.2.5 + DRF 프로젝트 생성
- MariaDB Docker 연동 (localhost → 127.0.0.1 소켓 이슈 해결)
- JWT 인증, CORS 설정 완료
- 기본 마이그레이션 성공
- **다음 작업**: core/models.py에 HACCP 8개 모델 구현
- **브랜치**: feature/django-backend-setup (PR 대기)

### 개발 노하우 메모
- **자연스러운 커밋/PR 작성법**:
  - 삽질했던 부분 언급 (localhost 소켓 문제 등)
  - 과도한 이모지나 템플릿 형식 피하기
  - 개인적 경험과 해결 과정 포함
  - "완료", "예정" 같은 간단한 표현 사용

- **DB 연결 이슈 해결**:
  - Django mysqlclient에서 localhost는 Unix 소켓 시도
  - Docker 환경에서는 127.0.0.1 사용 (TCP 포트)
  - mysqlclient 컴파일 위해 libmysqlclient-dev 설치 필요

- **환경 설정 베스트 프랙티스**:
  - .env.example 템플릿 제공
  - SECRET_KEY는 절대 하드코딩 금지
  - docker-compose.yml 최신 문법 (version 필드 제거)

## Code Architecture & Design Patterns

### Backend (Django) 패턴
- **Repository Pattern**: 복잡한 쿼리 로직은 별도 repository 클래스로 분리
- **Service Layer**: 비즈니스 로직을 service.py에서 처리, view는 얇게 유지
- **Serializer 분리**: CRUD 별로 다른 serializer 사용 (CreateSerializer, UpdateSerializer)
- **Custom Manager**: 자주 사용하는 쿼리는 커스텀 매니저로 캡슐화
- **Permission 클래스**: 역할별 권한은 커스텀 permission 클래스로 구현

### Frontend (React) 패턴 (예정)
- **Custom Hooks**: API 호출, 상태 관리 로직을 훅으로 추상화
- **Compound Component**: 복잡한 UI 컴포넌트는 여러 하위 컴포넌트로 구성
- **Container/Presenter**: 로직과 UI 분리
- **Context + Reducer**: 전역 상태 관리 (Redux 대신)
- **Error Boundary**: 컴포넌트별 에러 처리

### 폴더 구조
```
backend/core/
├── models.py          # Django 모델
├── serializers/       # API 직렬화
│   ├── user_serializers.py
│   └── haccp_serializers.py
├── services/          # 비즈니스 로직
│   ├── haccp_service.py
│   └── traceability_service.py
├── views/            # API 뷰
├── permissions/      # 커스텀 권한
└── repositories/     # 데이터 접근 계층

frontend/src/
├── components/       # 재사용 가능한 UI
├── pages/           # 페이지 컴포넌트
├── hooks/           # 커스텀 훅
├── services/        # API 호출
├── context/         # 전역 상태
└── utils/           # 헬퍼 함수
```

### HACCP 특화 패턴
- **Immutable Log Pattern**: CCP 로그는 수정 불가, 새 레코드로만 이력 관리
- **Audit Trail**: 모든 중요 데이터 변경 시 자동 감사 로그 생성
- **Chain of Responsibility**: HACCP 검증 단계를 체인 패턴으로 구현