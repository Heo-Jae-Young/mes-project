# Testing Guide

이 문서는 백엔드 테스트 아키텍처와 실행 가이드를 제공합니다.

## 테스트 환경 구성

### 테스트 데이터베이스
- **선택**: MariaDB 단일 환경 (운영 환경과 동일)
- **이유**: 실제 DB 제약조건과 데이터 타입 검증 가능

### 테스트 구조
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
├── unit/                        # 단위 테스트
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_serializers.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/                 # 통합 테스트 (예정)
│   ├── __init__.py
│   ├── test_api_flows.py
│   ├── test_database.py
│   └── test_services_db.py
└── fixtures/                    # 테스트 데이터
    └── test_data.json
```

## 테스트 실행 방법

### 기본 실행
```bash
# 전체 테스트 실행
pytest -v

# 단위테스트만 실행
pytest -m "unit" -v

# 통합테스트만 실행 (예정)
pytest -m "integration" -v

# 특정 폴더만 실행
pytest core/tests/unit/ -v

# 커버리지 리포트
pytest --cov=core --cov-report=html
```

### MariaDB 테스트 권한 설정
```bash
# 한 번만 실행 (테스트 DB 생성 권한 부여)
docker exec mes-mariadb mariadb -u root -proot123 \
  -e "GRANT ALL PRIVILEGES ON *.* TO 'mes_user'@'%' WITH GRANT OPTION; FLUSH PRIVILEGES;"
```

## 현재 테스트 현황

### 단위 테스트 (25개 모두 통과)

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

## 테스트 헬퍼 함수

### 공통 헬퍼 활용
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
def authenticate_client(client, role='admin'):
    token = generate_jwt_for_role(role)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
    return token
```

### pytest fixture 활용
```python
# conftest.py
@pytest.fixture
def test_user():
    return create_test_user()

@pytest.fixture
def authenticated_client(test_user):
    client = APIClient()
    token = RefreshToken.for_user(test_user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
    return client
```

## 테스트 모범 사례

### 테스트 설계 원칙
1. **단위 테스트**: 순수 비즈니스 로직 검증
2. **통합 테스트**: 여러 컴포넌트 간 상호작용 검증
3. **격리**: 각 테스트는 독립적으로 실행 가능
4. **반복 가능**: 동일한 조건에서 동일한 결과

### 테스트 작성 가이드
- 테스트 메소드명은 `test_동작_조건_예상결과` 패턴 사용
- Given-When-Then 구조로 테스트 작성
- 예외 상황도 반드시 테스트
- Mock 사용 최소화 (실제 DB 사용)

## 성능 최적화

### 테스트 DB 재사용
```ini
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = mes_backend.settings
--reuse-db  # 테스트 DB 재사용으로 속도 향상
```

### 실행 시간 최적화
- MariaDB (Docker): 6.8초 (25개 테스트)
- 병렬 실행: `pytest -n auto` (pytest-xdist 설치 필요)

## 발견된 실제 버그 사례

### employee_id 필드 길이 제한
```python
# 문제: employee_id 20자 제한 vs ROLE_PRODUCTION_MANAGER 21자
MySQLdb.DataError: (1406, "Data too long for column 'employee_id' at row 1")

# 해결: 문자열 길이 제한
employee_id=f'R_{role.upper()}'[:20]
```

**교훈**: SQLite에서는 발견하지 못했을 실제 제약조건 오류를 MariaDB에서 사전 발견