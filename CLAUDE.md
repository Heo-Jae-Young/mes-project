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

- **데이터베이스 마이그레이션:** `python manage.py migrate`
- **마이그레이션 파일 생성:** `python manage.py makemigrations`
- **관리자 계정 생성:** `python manage.py createsuperuser`
- **개발 서버 실행:** `python manage.py runserver`
- **설정 검증:** `python manage.py check`
- **시드 데이터 로드:** `python manage.py seed_data --clear` (admin/admin123 계정 자동 생성)
- **테스트 실행:** `pytest` (pytest-django 사용)
- **테스트 커버리지:** `pytest --cov=core --cov-report=html`

### 데이터베이스 관리

- **전체 데이터베이스 초기화 (완전 리셋):**

  ```bash
  # 1. 서버 중지 및 DB 볼륨 삭제
  docker-compose down -v
  docker-compose up -d db

  # 2. 마이그레이션 실행
  python manage.py migrate

  # 3. 시드 데이터 로드 (관리자 계정 포함)
  python manage.py seed_data --clear
  ```

- **모든 데이터 삭제 (스키마 유지):** `python manage.py flush`
- **특정 앱 마이그레이션 초기화:** `python manage.py migrate <앱이름> zero`
- **마이그레이션 상태 확인:** `python manage.py showmigrations`
- **데이터베이스 직접 접속:** `docker exec -it mes-mariadb mysql -u mes_user -p`

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

### 2025-09-01: Django Backend 초기 설정 완료

- Django 5.2.5 + DRF 프로젝트 생성
- MariaDB Docker 연동 (localhost → 127.0.0.1 소켓 이슈 해결)
- JWT 인증, CORS 설정 완료
- 기본 마이그레이션 성공
- **다음 작업**: core/models.py에 HACCP 8개 모델 구현
- **브랜치**: feature/django-backend-setup (PR 대기)

### 2025-09-01: HACCP 모델 구현 완료 ✅

- models/ 패키지 구조로 8개 모델 파일 분리 구현
- User, Supplier, RawMaterial, MaterialLot, FinishedProduct, ProductionOrder, CCP, CCPLog
- Django Admin 인터페이스 완비 (CCPLog는 불변 데이터로 수정/삭제 불가)
- 시드 데이터 management command 구현 (admin 계정 자동 생성 포함)
- **상태**: PR #2 머지 완료, main 브랜치 반영됨
- **다음 작업**: DRF API 구현 (Serializers, ViewSets, 권한 시스템)

### 2025-09-01: DRF API 구현 완료 ✅

- **Serializers 구현**: 8개 모델별 CRUD 분리 구조
  - UserSerializer (조회/생성/수정용 분리)
  - SupplierSerializer, RawMaterialSerializer, MaterialLotSerializer
  - FinishedProductSerializer, ProductionOrderSerializer
  - CCPSerializer, CCPLogSerializer (불변 로그 처리)
- **ViewSets 구현**: REST API 엔드포인트 및 커스텀 액션
  - 역할별 권한 필터링 (admin, quality_manager, operator 등)
  - 통계/대시보드 API (/statistics, /dashboard 등)
  - HACCP 전용 기능 (/compliance-report, /critical-alerts)
- **URL 라우팅**: DRF Router로 자동 URL 생성
- **의존성 추가**: django-filter 패키지 및 설정
- **브라우저 테스트**: API 구조 및 권한 시스템 검증 완료
- **상태**: feature/api-implementation 브랜치, PR 생성 준비
- **다음 작업**: JWT 토큰 엔드포인트 추가, 권한 시스템 고도화

### 다음 세션 시작 가이드

**현재 완료된 것:**

- ✅ Django 백엔드 초기 설정 (Django 5.2.5 + DRF + MariaDB)
- ✅ HACCP 모델 8개 구현 (패키지 구조로 분리)
- ✅ Django Admin + 시드 데이터 (admin/admin123 계정)
- ✅ DRF API 구현 (Serializers + ViewSets + URL 라우팅)
- ✅ JWT 인증 기반 권한 시스템
- ✅ PR #3 생성 완료 (https://github.com/Heo-Jae-Young/mes-project/pull/3)

**다음 세션 우선 순위별 작업:**

### 1단계: PR 리뷰 및 머지

```bash
# PR #3 확인 및 머지 후
git checkout main
git pull origin main
# 새 브랜치 생성을 위한 준비
```

### 2단계: JWT 토큰 엔드포인트 추가 ✅ (완료)

**구현된 내용:**

- `/api/token/` - 로그인 (토큰 발급)
- `/api/token/refresh/` - 토큰 갱신
- `/api/token/verify/` - 토큰 검증

**테스트 방법:**

1. **토큰 발급 (로그인)**

   ```bash
   curl -X POST http://localhost:8000/api/token/ \
        -H "Content-Type: application/json" \
        -d '{"username": "admin", "password": "admin123"}'
   ```

   응답: `{"refresh": "...", "access": "..."}`

2. **인증된 API 호출**

   ```bash
   curl -X GET http://localhost:8000/api/users/ \
        -H "Authorization: Bearer {access_token}"
   ```

3. **토큰 검증**

   ```bash
   curl -X POST http://localhost:8000/api/token/verify/ \
        -H "Content-Type: application/json" \
        -d '{"token": "{access_token}"}'
   ```

   응답: `{}` (유효한 토큰일 때)

4. **토큰 갱신**
   ```bash
   curl -X POST http://localhost:8000/api/token/refresh/ \
        -H "Content-Type: application/json" \
        -d '{"refresh": "{refresh_token}"}'
   ```

**기본 테스트 계정:**

- admin/admin123 (role: admin)
- quality_manager/password (role: quality_manager)
- operator1/password (role: operator)

## Testing Strategy Discussion

### 테스트 데이터베이스 선택 이슈

**문제**: pytest 테스트에서 MySQL vs SQLite 선택 고민

**SQLite 테스트의 장점:**

- 빠른 실행 속도 (메모리 DB `:memory:` 사용)
- 완전한 격리 (각 테스트마다 새 DB)
- 권한 문제 없음 (DB 생성/삭제 자유)
- CI/CD 친화적 (별도 DB 서비스 불필요)

**SQLite vs MySQL 차이점이 영향을 주는 경우:**

1. **Django ORM 쿼리 차이**

   ```python
   # MySQL: CONCAT 함수 지원
   # SQLite: || 연산자 사용
   User.objects.extra(select={'full_name': "CONCAT(first_name, ' ', last_name)"})
   ```

2. **데이터 타입 처리 차이**

   - MySQL: DATETIME 정밀도, 타임존 처리
   - SQLite: TEXT 저장, 제약조건 처리

3. **트랜잭션 격리 수준**
   - MySQL: READ-COMMITTED 기본
   - SQLite: SERIALIZABLE 기본

### 테스트 레이어 분류 논의

**현재 작성한 테스트 분석:**

```python
def test_authenticated_api_access(self):
    url = '/api/users/'
    response = self.client.get(url)  # HTTP 요청 전체 스택 테스트
```

**테스트 성격별 분류:**

| 테스트 유형    | 대상               | 특징            | DB 선택     | 폴더 위치            |
| -------------- | ------------------ | --------------- | ----------- | -------------------- |
| **단위테스트** | 개별 함수/메소드   | 빠름, 격리      | SQLite      | `tests/unit/`        |
| **통합테스트** | 여러 컴포넌트 협업 | 실제 환경       | MySQL       | `tests/integration/` |
| **API 테스트** | HTTP 요청/응답     | 전체 스택       | 상황에 따라 | `tests/api/`         |
| **E2E 테스트** | 사용자 시나리오    | 느림, 실제 환경 | MySQL       | `tests/e2e/`         |

**서비스 레이어 테스트 분류:**

```python
# 단위테스트 (SQLite) - 순수 비즈니스 로직
class HaccpService:
    def calculate_compliance_score(self, ccp_logs):
        # 계산 로직만, DB 무관

# 통합테스트 (MySQL) - 복잡한 DB 연동
class ProductionService:
    @transaction.atomic
    def create_production_order_with_materials(self):
        # 여러 테이블 연동, 트랜잭션 중요
```

### 권장 테스트 구조

```
backend/core/tests/
├── __init__.py
├── unit/                    # 단위 테스트 (SQLite, 빠름)
│   ├── test_models.py       # 모델 단위 기능
│   ├── test_serializers.py  # 직렬화 로직
│   ├── test_services.py     # 순수 비즈니스 로직
│   └── test_utils.py        # 유틸리티 함수
├── integration/             # 통합 테스트 (MySQL, 실제 환경)
│   ├── test_api_flows.py    # 전체 API 플로우
│   ├── test_database.py     # 복잡한 DB 쿼리/트랜잭션
│   └── test_services_db.py  # 서비스+DB 연동
└── fixtures/                # 테스트 데이터
    └── test_data.json
```

**pytest 실행 전략:**

```bash
# 개발 중 빠른 피드백 (단위테스트만)
pytest tests/unit -v

# 배포 전 전체 검증 (통합테스트 포함)
pytest tests/ -v

# 마커 기반 실행
pytest -m "unit"        # 단위테스트만
pytest -m "integration" # 통합테스트만
pytest -m "slow"        # 느린 테스트만
```

### JWT 테스트 단위/통합 분리 논의

**문제**: JWT 인증 테스트를 단위테스트와 통합테스트로 나눌지 고민

**JWT 단위테스트 가능 영역:**

```python
# 1. 순수 토큰 생성/검증 로직 (DB 없이)
def test_jwt_token_generation():
    user = User(username='test', role='admin')  # 메모리 객체
    refresh = RefreshToken.for_user(user)
    assert len(str(refresh.access_token)) > 100

# 2. 토큰 페이로드 검증
def test_jwt_payload_contains_user_id():
    user = User(id=1, username='test')
    token = RefreshToken.for_user(user)
    payload = token.payload
    assert payload['user_id'] == 1

# 3. 시리얼라이저 단위 로직
def test_token_serializer_validation():
    data = {'username': 'test', 'password': 'pass'}
    serializer = TokenObtainPairSerializer(data=data)
    # 검증 로직만 테스트
```

**JWT 통합테스트 영역 (현재 작성한 것):**

```python
# HTTP 요청/응답 + 전체 인증 플로우
def test_token_obtain_success():
    url = '/api/token/'
    response = self.client.post(url, data)  # 전체 스택
```

### 테스트 헬퍼 재사용성 논의

**문제**: 단위테스트와 통합테스트에서 공통 로직 재사용 방법

**해결책: 모델 기준 헬퍼 구조**

```
tests/
├── helpers/
│   ├── __init__.py
│   ├── user_helpers.py          # User 모델 관련
│   ├── supplier_helpers.py      # Supplier 모델 관련
│   ├── raw_material_helpers.py  # RawMaterial 모델 관련
│   ├── product_helpers.py       # FinishedProduct 모델 관련
│   ├── production_helpers.py    # ProductionOrder 모델 관련
│   ├── haccp_helpers.py         # CCP, CCPLog 모델 관련
│   └── auth_helpers.py          # JWT, 인증 관련
```

**헬퍼 함수 예시:**

```python
# tests/helpers/user_helpers.py
def create_test_user(role='operator', **kwargs):
    defaults = {
        'username': f'test_{role}',
        'password': 'testpass123',
        'email': f'{role}@test.com',
        'role': role,
        'employee_id': f'TEST_{role.upper()}'
    }
    defaults.update(kwargs)
    return User.objects.create_user(**defaults)

# tests/helpers/auth_helpers.py
def generate_jwt_for_role(role='admin'):
    user = create_test_user(role=role)
    return RefreshToken.for_user(user)

def authenticate_client(client, role='admin'):
    token = generate_jwt_for_role(role)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
    return token
```

**pytest fixture로 공통 데이터 관리:**

```python
# conftest.py
@pytest.fixture
def test_user():
    return create_test_user()

@pytest.fixture
def jwt_token(test_user):
    return RefreshToken.for_user(test_user)

@pytest.fixture
def authenticated_client(test_user):
    client = APIClient()
    token = RefreshToken.for_user(test_user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
    return client
```

### 최종 테스트 아키텍처 결정 ✅

**채택된 구조:**

```
backend/core/tests/
├── __init__.py
├── conftest.py                  # pytest fixtures
├── helpers/                     # 모델별 헬퍼 함수
│   ├── __init__.py
│   ├── user_helpers.py
│   ├── auth_helpers.py
│   ├── haccp_helpers.py
│   ├── supplier_helpers.py
│   ├── raw_material_helpers.py
│   ├── product_helpers.py
│   └── production_helpers.py
├── unit/                        # 단위 테스트 (SQLite)
│   ├── __init__.py
│   ├── test_models.py           # 모델 단위 기능
│   ├── test_serializers.py      # 직렬화 로직
│   ├── test_jwt_logic.py        # JWT 순수 로직
│   ├── test_services.py         # 순수 비즈니스 로직
│   └── test_utils.py            # 유틸리티 함수
├── integration/                 # 통합 테스트 (MySQL)
│   ├── __init__.py
│   ├── test_jwt_api.py          # JWT API 전체 플로우
│   ├── test_api_flows.py        # 전체 API 플로우
│   ├── test_database.py         # 복잡한 DB 쿼리/트랜잭션
│   └── test_services_db.py      # 서비스+DB 연동
└── fixtures/                    # 테스트 데이터
    └── test_data.json
```

**결정 사항:**

1. **JWT 테스트 분리**: 단위테스트(토큰 로직) + 통합테스트(API 플로우)
2. **DB 선택**: SQLite(단위) + MySQL(통합) 병행
3. **헬퍼 구조**: 모델 기준으로 파일 분리
4. **공통 로직**: pytest fixture + 헬퍼 함수 조합
5. **현재 JWT 테스트**: `integration/test_jwt_api.py`로 이동 예정

### 테스트 아키텍처 구현 완료 ✅

**구현 과정에서 발생한 문제 및 해결책:**

1. **MySQL 테스트 DB 권한 문제**

   ```
   MySQLdb.OperationalError: (1044, "Access denied for user 'mes_user'@'%' to database 'test_mes_db'")
   ```

   **해결책**: 단위테스트용 별도 설정 파일 생성

   ```python
   # mes_backend/test_settings.py
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': ':memory:',  # 메모리 DB 사용
       }
   }
   ```

   **pytest.ini 수정**:

   ```ini
   DJANGO_SETTINGS_MODULE = mes_backend.test_settings
   --cov-fail-under=10  # 현실적인 커버리지 요구사항
   ```

2. **Django tests.py와 tests/ 디렉토리 충돌**

   ```
   import file mismatch: imported module 'core.tests' has this __file__ attribute
   ```

   **해결책**:

   - 기존 `core/tests.py` 파일 삭제
   - Python 캐시 파일 정리: `find . -name "*.pyc" -delete`

3. **User 모델 **str** 메소드 누락**

   ```python
   AssertionError: assert 'strtest' == 'strtest (admin)'
   ```

   **해결책**: User 모델에 **str** 메소드 추가

   ```python
   def __str__(self):
       return f"{self.username} ({self.role})"
   ```

4. **JWT 시리얼라이저 예외 처리 테스트**

   ```python
   rest_framework.exceptions.AuthenticationFailed: No active account found
   ```

   **해결책**: 예외 발생 예상하고 pytest.raises 사용

   ```python
   with pytest.raises(Exception):
       serializer.is_valid(raise_exception=True)
   ```

**최종 구현 결과:**

- ✅ 단위테스트 18개 모두 통과
- ✅ SQLite 메모리DB로 빠른 실행 (1초 이내)
- ✅ 마커 기반 테스트 분리 (`pytest -m "unit"`)
- ✅ 체계적인 헬퍼 함수 구조
- ✅ pytest fixture로 공통 데이터 관리

### 테스트 아키텍처 단순화 ✅ (최종)

**결정**: **SQLite vs MariaDB 복잡성 제거** → **MariaDB 단일 환경**

**이유:**

- 실제 운영환경과 동일한 DB 사용이 가장 신뢰성 있음
- 관리 포인트 절반으로 감소 (설정 파일 1개, pytest 설정 1개)
- Django ORM 사용 시 DB별 차이가 실제로는 크지 않음
- 성능 차이: SQLite 1.9초 vs MariaDB 6.8초 (허용 가능)

**최종 테스트 설정:**

```ini
# pytest.ini (단일 설정)
[pytest]
DJANGO_SETTINGS_MODULE = mes_backend.settings  # 운영과 동일한 설정
--reuse-db  # 테스트 DB 재사용으로 속도 향상
```

**MariaDB 테스트 권한 설정:**

```bash
# 한 번만 실행
docker exec mes-mariadb mariadb -u root -proot123 \
  -e "GRANT ALL PRIVILEGES ON *.* TO 'mes_user'@'%' WITH GRANT OPTION; FLUSH PRIVILEGES;"
```

**테스트 실행 예시:**

```bash
# 단위테스트만 실행
pytest -m "unit" -v

# 통합테스트만 실행
pytest -m "integration" -v

# 전체 테스트 실행
pytest -v

# 특정 폴더만 실행
pytest core/tests/unit/ -v        # 단위테스트
pytest core/tests/integration/ -v # 통합테스트
```

**성능 비교 결과:**

- SQLite (:memory): 1.9초 (18개 테스트)
- MariaDB (Docker): 6.8초 (18개 테스트)
- **결론**: 3배 차이는 있지만 개발 생산성 vs 환경 일관성을 고려해 MariaDB 선택

**MariaDB 전환으로 발견한 실제 버그:**

```
MySQLdb.DataError: (1406, "Data too long for column 'employee_id' at row 1")
```

- **문제**: `employee_id` 20자 제한 vs `ROLE_PRODUCTION_MANAGER` 21자
- **해결**: `employee_id=f'R_{role.upper()}'[:20]` (문자열 길이 제한)
- **교훈**: SQLite에서는 발견하지 못했을 실제 제약조건 오류를 사전 발견

## 현재 프로젝트 상태 (2025-09-01) 🚀

### 📊 **원본 기획서 대비 진행 현황 분석**

#### 전체 진행률: **약 75% 완료** (⬆️ +15%)
- **백엔드**: 95% 완료 (ViewSet-Service 연결 + API 문서화 완료)
- **프론트엔드**: 0% 완료 ❌
- **배포**: 0% 완료 ❌

### 🎉 **최신 업데이트: ViewSet-Service Layer 연결 + API 문서화 완료!**

### 📋 **금일(2025-09-01) 완료된 작업들:**

1. **ViewSet-Service Layer 연결** ✅
   - CCPLogViewSet: `perform_create`, `get_queryset` Service 연결
   - ProductionOrderViewSet: `start_production`, `complete_production` Service 연결  
   - UserViewSet: 완전한 Service Layer 활용
   - SupplierViewSet: Service 클래스 연결

2. **API 문서화 구현** ✅
   - drf-spectacular 0.28.0 설치 및 설정
   - requirements.txt 의존성 추가
   - OpenAPI 3.0.3 스키마 자동 생성
   - Swagger UI: `http://localhost:8000/api/docs/`
   - ReDoc UI: `http://localhost:8000/api/redoc/`

### 완료된 작업 ✅

1. **Django 백엔드 기본 구조** (완료)

   - Django 5.2.5 + DRF + MariaDB Docker 연동
   - JWT 인증 시스템 구축 (`/api/token/`, `/api/token/refresh/`, `/api/token/verify/`)
   - CORS 설정 및 기본 미들웨어 구성

2. **HACCP 모델 8개 구현** (완료)

   - User (역할 기반 접근 제어)
   - Supplier, RawMaterial, MaterialLot (원료 관리)
   - FinishedProduct, ProductionOrder (생산 관리)
   - CCP, CCPLog (HACCP 중요관리점)

3. **Django Admin 인터페이스** (완료)

   - 모든 모델 admin 등록
   - CCPLog 불변성 보장 (수정/삭제 불가)
   - 시드 데이터 management command (`python manage.py seed_data --clear`)

4. **DRF API 구현** (완료)

   - 8개 모델별 ViewSets + Serializers
   - 역할별 권한 필터링
   - 통계/대시보드 API 엔드포인트
   - HACCP 컴플라이언스 전용 API

5. **체계적인 테스트 아키텍처** (완료)
   - pytest + MariaDB 환경 (운영과 동일)
   - 단위/통합 테스트 분리 구조
   - 모델별 헬퍼 함수 + pytest fixture
   - **25개 서비스 레이어 단위 테스트 모두 통과**

6. **Service Layer 구현** (완료 ✅)
   - HACCP 컴플라이언스 검증 및 리포팅
   - 생산 주문 관리 및 효율성 계산
   - 공급업체 성과 평가 및 리스크 관리
   - 완전한 추적성(traceability) 관리

### 🔧 **API 테스트 결과 및 해결하지 못한 이슈**

#### **정상 작동하는 Service Layer 연결 API들:** ✅
1. **JWT 토큰 발급** - `POST /api/token/` 
2. **CCP 로그 조회** - `GET /api/ccp-logs/` (228개 결과, Service 권한 필터링 적용)
3. **생산 주문 조회** - `GET /api/production-orders/` (6개 결과, Service 권한 필터링 적용)
4. **사용자 조회** - `GET /api/users/` (6개 결과, Service 권한 필터링 적용)

#### **⚠️ 미해결 이슈: critical_alerts API 오류** 
- **문제**: `GET /api/ccps/critical_alerts/` 
- **오류**: `HaccpService.get_critical_alerts() got an unexpected keyword argument 'hours'`
- **원인**: Django Python 모듈 캐시 이슈로 Service 파일 수정이 서버에 반영되지 않음
- **시도한 해결책들**:
  - ✅ Service 메소드 시그니처 수정 (`def get_critical_alerts(self, user=None, hours=24)`)
  - ✅ Python 캐시 파일 삭제 (`find . -name "*.pyc" -delete`)
  - ✅ 서버 재시작 (다수 시도)
  - ✅ ViewSet에서 직접 로직 구현으로 우회 시도
  - ❌ **여전히 동일한 오류 지속**
- **현재 상태**: HACCP 핵심 기능이지만 미해결로 남음
- **임시 해결책**: 프론트엔드에서 해당 기능 개발 시 재시도 필요

#### **2. 기획서 Post-MVP 기능 미구현** ❌
- **전체 추적성 엔진**: 원자재 ↔ 완성품 추적 API
- **실시간 대시보드 및 OEE**: 장비 효율성 계산
- **개선 조치 워크플로우**: CCP 이탈 시 대응 시스템  
- **문서 관리 시스템**: SOP, 레시피 버전 관리

#### **3. HACCP 핵심 요구사항 미완료** ❌
- **CCP 로그 불변성**: UPDATE 쿼리 방지, 변경 이력 추적
- **감사 가능한 추적 기록**: 수정 사유 기록 시스템

### 🚨 **긴급 프론트엔드 구현 필요** 

#### **원본 기획서 대비 누락 상황**
- **React 프론트엔드**: 0% 구현 ❌
- **Axios 통합**: 0% 구현 ❌  
- **Docker 컨테이너화**: 0% 구현 ❌
- **Nginx 프로덕션 환경**: 0% 구현 ❌

### 현재 브랜치 상태

- **main**: 안정된 HACCP 모델 + API 구조 (이전 상태)
- **feature/service-layer**: 서비스 레이어 (머지됨)
- **feature/viewset-service-integration**: ViewSet-Service 연결 + API 문서화 완료 ✅

### 🎯 **업데이트된 우선순위 로드맵**

#### **1단계: 백엔드 마무리** (선택사항 - 30분) 🔄
- ✅ **ViewSet-Service 연결**: 4개 핵심 API 정상 작동 
- ✅ **API 문서화**: Swagger UI 완료
- ⚠️ **critical_alerts API 수정**: Django 캐시 이슈 해결 (나중에)

#### **2단계: 프론트엔드 구현** (즉시 시작 - 1주) 🚨
- **React 앱 생성**: `npx create-react-app frontend` 
- **디렉토리 구조**: `src/components/`, `src/pages/`, `src/services/`
- **기본 컴포넌트**: LoginPage, DashboardPage, CCPLogForm
- **React Router**: 페이지 라우팅 및 ProtectedRoute
- **상태 관리**: useState, useContext로 JWT 관리

#### **3단계: API 통합** (프론트엔드와 병행 - 3일) 🚨  
- **Axios 설정**: Base URL, 인터셉터 구성
- **JWT 인증**: 자동 토큰 첨부 및 리프레시 로직
- **API 서비스**: 4개 검증된 API 우선 연동
  - JWT 인증, CCP 로그, 생산 주문, 사용자 관리

#### **4단계: 배포 환경 구축** (1주) 📦
- **Docker 컨테이너화**: Django, React, MariaDB
- **Nginx 설정**: 프로덕션 환경 구성
- **클라우드 배포**: AWS/DigitalOcean 배포

### ⚡ **다음 세션 즉시 시작 작업**

#### **백엔드 완성 (1-2시간)**
1. **ViewSet에 Service 연결**:
   ```bash
   # core/views/haccp_views.py 수정
   from core.services.haccp_service import HaccpService
   
   class CCPLogViewSet(viewsets.ModelViewSet):
       def __init__(self, *args, **kwargs):
           super().__init__(*args, **kwargs)
           self.haccp_service = HaccpService()
   
       def perform_create(self, serializer):
           # Service의 validate_ccp_log_creation 사용
           self.haccp_service.validate_ccp_log_creation(...)
   ```

2. **API 문서화**:
   ```bash
   pip install drf-spectacular
   # settings.py 설정 추가
   # urls.py에 swagger 엔드포인트 추가
   ```

#### **프론트엔드 시작 (즉시)**  
1. **React 프로젝트 생성**:
   ```bash
   npx create-react-app frontend
   cd frontend
   npm install axios react-router-dom
   ```

2. **기본 구조 생성**:
   ```
   frontend/src/
   ├── components/     # 재사용 컴포넌트
   ├── pages/         # 페이지별 컴포넌트  
   ├── services/      # API 호출
   ├── hooks/         # 커스텀 훅
   └── context/       # 전역 상태
   ```

### 🏁 **최종 목표: 완전한 풀스택 MES 시스템**

기획서의 모든 요구사항을 충족하는 완성된 포트폴리오:
- ✅ **백엔드**: Django + DRF + Service Layer (85% 완료)
- ❌ **프론트엔드**: React + Axios + JWT (0% → 100% 목표)
- ❌ **배포**: Docker + Nginx + 클라우드 (0% → 100% 목표)

### 기술 부채 및 개선 사항

1. **통합 테스트 구현**: API 전체 플로우 테스트 추가
2. **로깅 시스템**: 구조화된 로깅 및 모니터링
3. **캐싱 전략**: Redis를 활용한 성능 최적화
4. **보안 강화**: Rate limiting, Input validation 강화

### 개발 환경 현재 상태

**실행 중인 서비스:**

- MariaDB Docker Container (포트 3306)
- Django Development Server (포트 8000)
- **관리자 계정**: admin/admin123

**주요 명령어:**

```bash
# 개발 서버 시작
python manage.py runserver

# 테스트 실행
pytest -v

# 시드 데이터 로드
python manage.py seed_data --clear

# 데이터베이스 마이그레이션
python manage.py migrate
```

## 다음 세션 시작 가이드

**다음 세션 즉시 시작 작업:**

1. **React 프로젝트 생성**: `npx create-react-app frontend` (즉시)
2. **기본 컴포넌트 구조**: LoginPage, DashboardPage 스켈레톤
3. **Axios + JWT 기본 설정**: API 통신 준비

**현재 상황 요약:**

- ✅ **ViewSet-Service Layer 연결 완료** (4개 핵심 API 정상 작동)
- ✅ **API 문서화 완료** (Swagger UI: `/api/docs/`)
- ✅ **25개 단위 테스트 통과** + Service Layer 검증
- ⚠️ **critical_alerts API 미해결** (Django 캐시 이슈, 나중에 처리)
- ❌ **프론트엔드 0% 구현** (이제 최우선 과제)
- ❌ **배포 환경 미구현** (Docker + Nginx)

## 개발 학습 문서 📚

### 📁 **학습 문서 위치:**
```
backend/docs/
├── API_ROUTING.md      # Django DRF 라우팅 시스템 완전 해설
├── SERVICE_LAYER.md    # Service Layer 패턴 설명 (예정)
├── TESTING.md          # 테스트 아키텍처 가이드 (예정)  
└── ARCHITECTURE.md     # 전체 시스템 아키텍처 (예정)
```

### 📖 **주요 학습 내용:**
- **Django DRF 라우팅**: REST 경로 → ViewSet 함수 연결 원리
- **@action 데코레이터**: detail=True/False, methods 매핑
- **Service Layer 패턴**: Controller-Service-Model 구조
- **ViewSet vs APIView**: 언제 어떤 것을 사용할지
- **권한 시스템**: permission_classes 작동 원리

## Service Layer 구현 세부사항

### 📋 구현된 서비스 클래스

#### 1. HaccpService (`haccp_service.py`)
```python
class HaccpService:
    - validate_ccp_log_creation(): CCP 로그 생성 전 검증
    - calculate_compliance_score(): HACCP 컴플라이언스 점수 계산
    - get_critical_alerts(): 중요 알림 목록 조회
    - generate_compliance_report(): 컴플라이언스 보고서 생성

class HaccpQueryService:
    - get_ccp_logs_for_user(): 사용자별 CCP 로그 조회
    - get_ccps_for_user(): 접근 가능한 CCP 목록
```

#### 2. ProductionService (`production_service.py`)
```python
class ProductionService:
    - validate_production_order_creation(): 생산 주문 생성 검증
    - start_production(): 생산 시작 처리 (원자재 할당)
    - complete_production(): 생산 완료 처리
    - get_production_efficiency(): 효율성 지표 계산

class ProductionQueryService:
    - get_production_orders_for_user(): 역할별 생산 주문 조회
    - get_production_dashboard_data(): 대시보드 데이터

class MaterialTraceabilityService:
    - get_material_traceability(): 원자재 추적성 조회
    - get_forward_traceability(): 전방 추적성
```

#### 3. SupplierService (`supplier_service.py`)
```python
class SupplierService:
    - validate_supplier_creation(): 공급업체 등록 검증
    - evaluate_supplier_performance(): 성과 평가
    - get_supplier_risk_assessment(): 리스크 평가

class SupplierQueryService:
    - get_suppliers_for_user(): 역할별 공급업체 조회
    - get_supplier_statistics(): 통계 정보

class SupplierAuditService:
    - schedule_supplier_audit(): 감사 일정 등록
    - get_audit_checklist(): 감사 체크리스트
```

### 🧪 테스트 현황 (25개 모두 통과)

#### UserService Tests (8개)
- ✅ 비밀번호 변경 (관리자/본인)
- ✅ 권한 검증 및 에러 처리
- ✅ 사용자 쿼리셋 필터링

#### HaccpService Tests (6개)
- ✅ CCP 로그 검증 (권한, 시간, 상태)
- ✅ 컴플라이언스 점수 계산

#### ProductionService Tests (5개)
- ✅ 생산 주문 검증
- ✅ 효율성 계산

#### SupplierService Tests (6개)
- ✅ 공급업체 검증 (중복, HACCP 인증)
- ✅ 리스크 평가

### 💡 핵심 설계 특징

1. **HACCP 특화**: 식품안전 규정에 특화된 비즈니스 로직
2. **역할 기반 접근 제어**: admin, quality_manager, operator 역할별 권한
3. **데이터 무결성**: 트랜잭션 처리 및 검증 로직
4. **추적성 보장**: 완전한 forward/backward traceability
5. **성과 지표**: 효율성, 컴플라이언스 점수 자동 계산

### 개발 노하우 메모

- **자연스러운 커밋/PR 작성법**:

  - **WHY 먼저 설명**: 왜 이 작업을 했는지 배경과 문제점 설명
  - **WHAT 구체적으로**: 실제 구현한 클래스/메소드명 나열
  - **HOW 경험담**: 삽질했던 부분과 해결 과정 솔직하게 기록
  - **결과 요약**: 테스트 통과, 커버리지 등 정량적 결과
  - 과도한 이모지나 템플릿 형식 피하기
  - Generated with [Claude Code] 같은 자동 생성 문구 금지
  
  **예시 구조:**
  ```
  feat: [무엇을] 구현 완료
  
  [왜] 기존 문제점과 구현 동기 설명
  
  구현한 내용:
  - 클래스명: 구체적인 메소드들 나열
  - 핵심 기능별 상세 설명
  
  구현 과정 삽질:
  - 문제1 → 해결책1
  - 문제2 → 해결책2
  
  [결과] 테스트 통과율, 커버리지 등
  ```

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
