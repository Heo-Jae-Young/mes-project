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