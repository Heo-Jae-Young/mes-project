# 🧪 Django 프로젝트 테스트 완전 가이드

> **"한 권으로 마스터하는 실무 테스트 작성법"**
> 
> 이 가이드만 따라하면 어떤 Django 프로젝트에서도 체계적인 테스트를 작성할 수 있습니다.
> 초보자도 단계별로 따라할 수 있도록 **실무 중심**으로 구성했습니다.

---

## 📚 **목차 (Table of Contents)**

### 🏃‍♂️ **시작하기 (Quick Start)**
- [1. 5분 만에 테스트 실행해보기](#-1-5분-만에-테스트-실행해보기)
- [2. 나의 첫 번째 테스트 작성하기](#-2-나의-첫-번째-테스트-작성하기)
- [3. 테스트가 왜 중요한가?](#-3-테스트가-왜-중요한가)

### 📖 **테스트 기초 이론**
- [4. 테스트 피라미드와 종류](#-4-테스트-피라미드와-종류)
- [5. Django 테스트 아키텍처](#-5-django-테스트-아키텍처)
- [6. 우리 프로젝트 테스트 전략](#-6-우리-프로젝트-테스트-전략)

### 🔨 **단계별 실습 (Hands-on)**
- [7. Step 1: Model 단위 테스트](#-7-step-1-model-단위-테스트)
- [8. Step 2: Service Layer 테스트](#-8-step-2-service-layer-테스트)
- [9. Step 3: API 통합 테스트](#-9-step-3-api-통합-테스트)
- [10. Step 4: 프론트엔드 테스트](#-10-step-4-프론트엔드-테스트)

### 💡 **고급 테크닉**
- [11. 테스트 데이터 관리 (Fixtures & Factories)](#-11-테스트-데이터-관리-fixtures--factories)
- [12. Mock과 Stub 활용법](#-12-mock과-stub-활용법)
- [13. 성능 테스트와 최적화](#-13-성능-테스트와-최적화)

### 🛠️ **실무 활용**
- [14. 테스트 주도 개발(TDD) 실습](#-14-테스트-주도-개발tdd-실습)
- [15. CI/CD 파이프라인 구축](#-15-cicd-파이프라인-구축)
- [16. 레거시 코드에 테스트 추가하기](#-16-레거시-코드에-테스트-추가하기)

### 📋 **참고 자료**
- [17. 체크리스트 & 템플릿](#-17-체크리스트--템플릿)
- [18. 트러블슈팅 FAQ](#-18-트러블슈팅-faq)
- [19. 추천 도구 & 라이브러리](#-19-추천-도구--라이브러리)

---

## 🏃‍♂️ **1. 5분 만에 테스트 실행해보기**

> **"테스트가 뭔지 몰라도 일단 돌려보자!"**

### 1.1 현재 프로젝트 테스트 상황 확인

```bash
# 1. 백엔드 디렉토리로 이동
cd backend

# 2. 가상환경 활성화
source venv/bin/activate

# 3. 현재 테스트 실행
pytest -v

# 4. 커버리지 포함 실행
pytest --cov=core --cov-report=html
```

### 1.2 결과 해석하기

✅ **성공 예시**:
```
========================= 57 tests collected in 1.56s =========================
========================= 57 passed in 15.23s =========================
```

❌ **실패 예시**:
```
FAILED core/tests/unit/test_models.py::TestUser::test_user_creation - AssertionError
```

### 1.3 커버리지 리포트 확인

```bash
# HTML 리포트 열기 (브라우저에서)
open htmlcov/index.html
```

**현재 우리 프로젝트**: 18% 커버리지 → **목표**: 90%

---

## 🚀 **2. 나의 첫 번째 테스트 작성하기**

> **"Hello, World!를 넘어 실제 비즈니스 로직 테스트하기"**

### 2.1 가장 간단한 Model 테스트

```python
# core/tests/unit/test_my_first_test.py
import pytest
from core.models import User

@pytest.mark.unit
class TestMyFirstTest:
    """나의 첫 번째 테스트 클래스"""
    
    def test_user_creation(self):
        """사용자 생성 테스트 - 가장 기본!"""
        # Given: 사용자 데이터 준비
        user_data = {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@example.com',
            'role': 'operator'
        }
        
        # When: 사용자 생성
        user = User.objects.create_user(**user_data)
        
        # Then: 결과 검증
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.role == 'operator'
        assert user.check_password('testpass123')  # 비밀번호 해시 확인
        
    def test_user_string_representation(self):
        """사용자 모델의 __str__ 메소드 테스트"""
        # Given
        user = User.objects.create_user(
            username='john', 
            password='pass123',
            email='john@example.com'
        )
        
        # When & Then
        assert str(user) == 'john'
```

### 2.2 테스트 실행하고 결과 확인

```bash
# 특정 테스트만 실행
pytest core/tests/unit/test_my_first_test.py -v

# 예상 결과:
# test_user_creation PASSED
# test_user_string_representation PASSED
```

### 2.3 성공! 🎉

**축하합니다!** 첫 번째 테스트를 성공적으로 작성했습니다.

**배운 것들**:
- `pytest.mark.unit`: 테스트 분류
- `Given-When-Then` 패턴
- `assert` 문으로 검증
- Django ORM 테스트 방법

---

## 💡 **3. 테스트가 왜 중요한가?**

### 3.1 실제 우리 프로젝트에서 발견한 버그들

#### 🐛 **Bug Case 1: 데이터베이스 제약조건**
```python
# 문제 상황
employee_id = f'ROLE_PRODUCTION_MANAGER'  # 21자
# 하지만 DB 필드 max_length=20 😱

# 테스트로 미리 발견!
MySQLdb.DataError: (1406, "Data too long for column 'employee_id' at row 1")

# 해결책
employee_id = f'R_{role.upper()}'[:20]  # 20자 제한
```

#### 🐛 **Bug Case 2: 비즈니스 로직 오류**
```python
# 문제: FIFO 원칙 위반
# 가장 오래된 로트가 아닌 최신 로트 사용

# 테스트로 검증
def test_material_consumption_follows_fifo():
    # 여러 로트 생성 (날짜 다르게)
    # 소비 후 가장 오래된 것부터 소비됐는지 확인
    pass
```

### 3.2 테스트의 ROI (Return on Investment)

| 단계 | 버그 발견 비용 | 수정 비용 | 예방 효과 |
|------|---------------|-----------|----------|
| **테스트 작성** | 1시간 | - | ⭐⭐⭐⭐⭐ |
| **개발 중 발견** | 2시간 | 30분 | ⭐⭐⭐⭐ |
| **QA 단계** | 4시간 | 2시간 | ⭐⭐⭐ |
| **운영 환경** | 20시간 | 8시간 + 신뢰도⬇ | ⭐ |

### 3.3 우리 프로젝트에서 테스트가 특히 중요한 이유

1. **HACCP 규정 준수** - 식품 안전은 생명과 직결
2. **재고 정확성** - 잘못된 계산은 비용 손실
3. **추적성(Traceability)** - 법적 요구사항
4. **복잡한 비즈니스 로직** - BOM, FIFO, 원가계산 등

---

## 📖 **4. 테스트 피라미드와 종류**

> **"어떤 테스트를 언제 얼마나 작성해야 할까?"**

### 4.1 테스트 피라미드 🔺

```
        /\
       /  \        E2E (End-to-End)
      /____\       - 적게 작성 (5-10%)
     /      \      - 느리지만 전체 워크플로우 검증
    /        \     
   /__________\    Integration (통합)
  /            \   - 적당히 작성 (20-30%)  
 /              \  - 컴포넌트 간 상호작용 검증
/________________\ 
                   Unit (단위)
                   - 많이 작성 (60-70%)
                   - 빠르고 안정적
```

### 4.2 우리 프로젝트 테스트 종류별 예시

#### 🟢 **Unit Tests (단위 테스트)** - 가장 많이
```python
# ✅ Model 단위 테스트
def test_user_password_validation():
    """사용자 비밀번호 해싱 검증"""
    
# ✅ Service Layer 단위 테스트  
def test_calculate_material_cost():
    """원자재 원가 계산 로직 검증"""
```

#### 🟡 **Integration Tests (통합 테스트)** - 적당히
```python
# ✅ API 통합 테스트
def test_production_order_creation_api():
    """생산 주문 생성 API 전체 플로우"""
    
# ✅ 데이터베이스 통합 테스트
def test_material_consumption_updates_inventory():
    """원자재 소비 시 재고 업데이트 검증"""
```

#### 🔴 **E2E Tests (종단간 테스트)** - 조금만
```python
# ✅ 전체 워크플로우
def test_complete_production_workflow():
    """원자재 입고 → BOM 설정 → 생산 주문 → 완료"""
```

---

## 🏗️ **5. Django 테스트 아키텍처**

### 5.1 우리 프로젝트 테스트 구조

```
backend/core/tests/
├── conftest.py           # 🎯 공통 fixtures
├── helpers/              # 🛠️ 테스트 도우미 함수들
│   ├── user_helpers.py   # 사용자 생성 도우미
│   ├── haccp_helpers.py  # HACCP 데이터 도우미
│   └── ...
├── unit/                 # 🟢 단위 테스트 (많이)
│   ├── test_models.py    # 모델 테스트
│   ├── test_services.py  # 서비스 레이어 테스트
│   └── test_serializers.py
├── integration/          # 🟡 통합 테스트 (적당히)  
│   ├── test_api_endpoints.py
│   └── test_workflows.py
└── e2e/                  # 🔴 E2E 테스트 (조금)
    └── test_production_flow.py
```

### 5.2 테스트 실행 명령어

```bash
# 🟢 단위 테스트만 (빠름 - 개발 중 자주)
pytest -m "unit" -v

# 🟡 통합 테스트만 (중간 속도 - PR 전)  
pytest -m "integration" -v

# 🔴 모든 테스트 (느림 - 배포 전)
pytest -v

# 📊 커버리지 포함
pytest --cov=core --cov-report=html
```

---

## 🎯 **6. 우리 프로젝트 테스트 전략**

### 6.1 현재 상황 분석

```python
# 현재 커버리지 현황 (18% → 목표: 90%)
TOTAL: 3056 lines, 2504 miss, 18.06% coverage

# 🟢 우선순위 1: Model 테스트
- user.py: 93% ✅ (거의 완료)
- haccp.py: 83% ⚠️ (개선 필요)
- bom.py: 87% ⚠️ (개선 필요)

# 🟡 우선순위 2: Service Layer 테스트  
- haccp_service.py: 15% 🔴 (시급)
- production_service.py: 15% 🔴 (시급)
- cost_calculation_service.py: 0% 🔴 (미구현)
```

### 6.2 테스트 작성 순서 (추천)

| 순서 | 테스트 종류 | 예상 시간 | 커버리지 향상 |
|------|------------|----------|--------------|
| **1단계** | Model 테스트 | 2-3시간 | +30% |
| **2단계** | Service Layer | 4-5시간 | +40% |  
| **3단계** | API 통합 | 2-3시간 | +15% |
| **4단계** | 워크플로우 E2E | 2시간 | +5% |

### 6.3 우리 프로젝트만의 특별한 테스트 포인트

#### 🛡️ **HACCP 규정 준수 테스트**
```python
def test_ccp_log_immutability():
    """CCP 로그는 생성 후 수정 불가"""
    
def test_critical_limit_violation_alert():
    """한계 기준 초과 시 자동 알림"""
```

#### 📦 **재고 관리 정확성 테스트**
```python  
def test_fifo_material_consumption():
    """FIFO 원칙에 따른 원자재 소비"""
    
def test_lot_traceability():
    """완전한 로트 추적성 보장"""
```

#### 💰 **원가 계산 정확성 테스트**
```python
def test_bom_cost_calculation():
    """BOM 기반 정확한 원가 계산"""
```

---

## 🔨 **7. Step 1: Model 단위 테스트**

> **"테스트의 기초 중의 기초! 데이터베이스 모델부터 시작하자"**

### 7.1 왜 Model 테스트부터 시작하나?

1. **가장 기초적** - 다른 모든 테스트의 기반
2. **빠른 실행** - 복잡한 로직 없이 단순한 CRUD
3. **높은 ROI** - 적은 노력으로 큰 커버리지 향상
4. **실제 버그 발견** - DB 제약조건, 검증 로직 오류 등

### 7.2 현재 우리 프로젝트 Model 상황

```python
# 커버리지 현황 (개선이 필요한 모델들)
- user.py: 93% ✅ (거의 완료)
- haccp.py: 83% ⚠️ (개선 필요) ← 여기부터 시작!
- bom.py: 87% ⚠️ (개선 필요)
- raw_material.py: 96% ✅
- production.py: 97% ✅
- supplier.py: 95% ✅
- product.py: 96% ✅
```

### 7.3 Model 테스트 작성법 - 실전 가이드

#### **7.3.1 기본 패턴: Given-When-Then**

```python
# core/tests/unit/test_models.py
import pytest
from decimal import Decimal
from django.utils import timezone
from django.core.exceptions import ValidationError

from core.models import CCP, CCPLog, User

@pytest.mark.unit
class TestCCPModel:
    """CCP(Critical Control Point) 모델 테스트"""
    
    def test_ccp_creation_success(self):
        """CCP 생성 - 정상 케이스"""
        # Given: 정상적인 CCP 데이터
        ccp_data = {
            'name': '온도 관리점',
            'description': '냉장 보관 온도 관리',
            'critical_limit_min': Decimal('0.0'),
            'critical_limit_max': Decimal('4.0'),
            'monitoring_procedure': '온도계로 매시간 측정',
            'is_active': True
        }
        
        # When: CCP 생성
        ccp = CCP.objects.create(**ccp_data)
        
        # Then: 생성 결과 검증
        assert ccp.name == '온도 관리점'
        assert ccp.critical_limit_min == Decimal('0.0')
        assert ccp.critical_limit_max == Decimal('4.0')
        assert ccp.is_active is True
        assert ccp.created_at is not None  # 자동 생성 확인
        
    def test_ccp_string_representation(self):
        """CCP __str__ 메소드 테스트"""
        # Given
        ccp = CCP.objects.create(
            name='pH 관리점',
            critical_limit_min=Decimal('6.0'),
            critical_limit_max=Decimal('8.0')
        )
        
        # When & Then
        assert str(ccp) == 'pH 관리점'
```

#### **7.3.2 검증 로직 테스트 (Validation)**

```python
    def test_ccp_critical_limits_validation(self):
        """CCP 한계 기준 검증 - min이 max보다 클 수 없음"""
        # Given: 잘못된 한계 기준 (min > max)
        with pytest.raises(ValidationError):
            # When: 잘못된 데이터로 CCP 생성 시도
            ccp = CCP(
                name='잘못된 관리점',
                critical_limit_min=Decimal('10.0'),  # min이 더 큼!
                critical_limit_max=Decimal('5.0')
            )
            # Then: ValidationError 발생 예상
            ccp.full_clean()  # Django 모델 검증 실행
```

#### **7.3.3 관계형 모델 테스트 (Foreign Key)**

```python
    def test_ccp_log_creation_with_foreign_key(self):
        """CCP 로그 생성 - 외래키 관계 포함"""
        # Given: CCP와 사용자 먼저 생성
        ccp = CCP.objects.create(
            name='온도 관리점',
            critical_limit_min=Decimal('0.0'),
            critical_limit_max=Decimal('4.0')
        )
        user = User.objects.create_user(
            username='operator1',
            password='pass123',
            role='operator'
        )
        
        # When: CCP 로그 생성
        log = CCPLog.objects.create(
            ccp=ccp,
            recorded_by=user,
            measured_value=Decimal('2.5'),
            notes='정상 범위 내'
        )
        
        # Then: 관계 검증
        assert log.ccp == ccp
        assert log.recorded_by == user
        assert log.measured_value == Decimal('2.5')
        assert log.is_within_limits() is True  # 비즈니스 로직 메소드
```

### 7.4 실제 발견된 버그 사례들

#### **Bug Case: DB 필드 길이 제한**
```python
def test_employee_id_max_length_constraint(self):
    """실제 버그: employee_id 20자 제한"""
    # Given: 21자 길이의 role name
    long_role = 'ROLE_PRODUCTION_MANAGER'  # 21자
    
    with pytest.raises(Exception):  # DB 제약조건 위반
        # When: 긴 employee_id로 사용자 생성 시도
        User.objects.create_user(
            username='test',
            password='pass123',
            employee_id=f'{long_role}'  # 20자 초과!
        )
        
def test_employee_id_proper_truncation(self):
    """해결책: 적절한 길이 제한"""
    # Given
    role = 'ROLE_PRODUCTION_MANAGER'
    
    # When: 20자로 제한하여 생성
    user = User.objects.create_user(
        username='test',
        password='pass123',
        employee_id=f'R_{role.upper()}'[:20]  # 해결책!
    )
    
    # Then
    assert len(user.employee_id) <= 20
    assert user.employee_id.startswith('R_ROLE_')
```

### 7.5 지금 당장 해볼 실습

**haccp.py 모델 테스트부터 시작해보겠습니다!**

```bash
# 1. 현재 haccp.py 모델 구조 확인
cat core/models/haccp.py

# 2. 새 테스트 파일 생성
touch core/tests/unit/test_haccp_models.py

# 3. 테스트 작성 후 실행
pytest core/tests/unit/test_haccp_models.py -v
```

**다음 단계**: 실제 `test_haccp_models.py` 파일을 만들어서 시작해볼까요?

---

## 🔧 Backend Testing Architecture

### 테스트 환경 구성

#### 테스트 데이터베이스
- **선택**: MariaDB 단일 환경 (운영 환경과 동일)
- **이유**: 실제 DB 제약조건과 데이터 타입 검증 가능

#### 테스트 구조
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
│   ├── test_models.py           # 모델 테스트
│   ├── test_serializers.py      # 시리얼라이저 테스트
│   ├── test_services.py         # 서비스 레이어 테스트
│   ├── test_repositories.py     # 저장소 패턴 테스트
│   └── test_utils.py            # 유틸리티 테스트
├── integration/                 # 통합 테스트
│   ├── __init__.py
│   ├── test_api_endpoints.py    # API 엔드포인트 테스트
│   ├── test_api_flows.py        # 워크플로우 테스트
│   ├── test_database.py         # 데이터베이스 통합 테스트
│   └── test_services_db.py      # 서비스-DB 통합
├── performance/                 # 성능 테스트
│   ├── __init__.py
│   └── test_query_optimization.py
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

## 🧪 Detailed Test Design Patterns

### 1. Unit Tests (단위 테스트)

#### Service Layer Testing - 핵심 비즈니스 로직

**ProductionService Tests**
```python
# tests/unit/test_production_service.py
class TestProductionService:
    def test_start_production_validates_material_availability(self):
        """생산 시작 시 원자재 가용성 검증"""
        
    def test_consume_materials_follows_fifo_principle(self):
        """원자재 소비 시 FIFO 원칙 준수"""
        
    def test_production_completion_updates_inventory(self):
        """생산 완료 시 재고 업데이트 정확성"""
```

**HACCPService Tests**
```python
# tests/unit/test_haccp_service.py
class TestHACCPService:
    def test_ccp_log_immutability(self):
        """CCP 로그의 불변성 보장"""
        
    def test_critical_limit_violation_alert(self):
        """한계 기준 초과 시 알림 발생"""
```

**BOMService Tests**
```python
# tests/unit/test_bom_service.py
class TestBOMService:
    def test_cost_calculation_accuracy(self):
        """BOM 기반 원가 계산 정확성"""
        
    def test_fifo_based_material_pricing(self):
        """FIFO 기반 원자재 가격 산정"""
```

#### Repository Pattern Testing
```python
# tests/unit/test_repositories.py
class TestMaterialRepository:
    def test_get_expiring_lots_within_days(self):
        """유통기한 임박 로트 조회"""
        
    def test_get_available_materials_for_production(self):
        """생산 가능한 원자재 조회 (품질검사 통과 + 유효기간)"""

class TestProductionRepository:
    def test_get_production_performance_analytics(self):
        """생산 성과 분석 데이터 정확성"""
```

#### Model Testing - 데이터 무결성 및 비즈니스 규칙
```python
# tests/unit/test_models.py
class TestMaterialLotModel:
    def test_lot_number_uniqueness_per_material(self):
        """원자재별 로트번호 유일성"""
        
    def test_cannot_consume_more_than_available(self):
        """가용량 초과 소비 방지"""

class TestProductionOrderModel:
    def test_status_transition_validation(self):
        """생산 주문 상태 전환 규칙 검증"""
        
    def test_haccp_audit_trail_creation(self):
        """HACCP 감사 추적 자동 생성"""
```

### 2. Integration Tests (통합 테스트)

#### API Endpoint Testing
```python
# tests/integration/test_api_endpoints.py
class TestProductionAPI:
    def test_start_production_end_to_end(self):
        """생산 시작 전체 플로우 검증"""
        
    def test_material_consumption_with_lot_tracking(self):
        """원자재 소비 + 로트 추적 통합 테스트"""

class TestHACCPComplianceAPI:
    def test_ccp_monitoring_workflow(self):
        """CCP 모니터링 워크플로우 전체 검증"""
```

#### Database Integration
```python
# tests/integration/test_database_constraints.py
class TestDataIntegrity:
    def test_foreign_key_constraints(self):
        """외래키 제약조건 검증"""
        
    def test_concurrent_inventory_updates(self):
        """동시성 상황에서 재고 업데이트 정확성"""
```

### 3. Performance Tests (성능 테스트)
```python
# tests/performance/test_query_optimization.py
class TestQueryPerformance:
    def test_material_dashboard_query_time(self):
        """원자재 대시보드 쿼리 성능 (< 100ms)"""
        
    def test_production_report_generation_time(self):
        """생산 리포트 생성 시간 (< 3s for 1000 records)"""
```

## ⚛️ Frontend Testing Architecture

### 1. Custom Hook Testing

#### useEntityPage Hook - 가장 중요한 재사용 로직
```javascript
// tests/hooks/useEntityPage.test.js
describe("useEntityPage Hook", () => {
  test("handles CRUD operations correctly", () => {
    // 생성, 수정, 삭제 플로우 검증
  });

  test("manages loading states properly", () => {
    // 로딩 상태 관리 검증
  });

  test("handles API errors gracefully", () => {
    // 에러 상황별 적절한 처리 검증
  });

  test("applies filters and triggers refetch", () => {
    // 필터 적용 및 데이터 재조회 검증
  });

  test("supports services without delete functionality", () => {
    // ProductionPage처럼 삭제 없는 서비스 지원 검증
  });
});
```

#### Service Adapter Testing
```javascript
// tests/utils/createServiceAdapter.test.js
describe("createServiceAdapter", () => {
  test("maps service methods correctly", () => {
    // 서비스 메소드 매핑 검증
  });

  test("handles optional delete method", () => {
    // 선택적 삭제 기능 처리 검증
  });
});
```

### 2. Component Testing

#### Business Logic Components
```javascript
// tests/components/MaterialList.test.js
describe("MaterialList Component", () => {
  test("displays inventory status correctly", () => {
    // 재고 상태 표시 검증
  });

  test("handles expired lots warning", () => {
    // 유통기한 만료 경고 표시 검증
  });

  test("triggers appropriate actions on user interaction", () => {
    // 사용자 상호작용 시 적절한 액션 실행 검증
  });
});

// tests/components/ProductionControls.test.js
describe("ProductionControls Component", () => {
  test("validates material availability before production start", () => {
    // 생산 시작 전 원자재 가용성 검증
  });

  test("displays correct production status", () => {
    // 생산 상태 정확한 표시 검증
  });
});
```

### 3. Page-Level Integration Testing
```javascript
// tests/pages/MaterialsPage.test.js
describe("MaterialsPage Integration", () => {
  test("complete CRUD workflow", () => {
    // 전체 CRUD 워크플로우 검증
  });

  test("filter functionality works end-to-end", () => {
    // 필터링 기능 전체 플로우 검증
  });

  test("error handling displays appropriate messages", () => {
    // 에러 상황별 적절한 메시지 표시 검증
  });
});
```

#### API Integration with MSW
```javascript
// tests/api/materialService.test.js
describe("Material Service Integration", () => {
  test("handles paginated responses correctly", () => {
    // DRF 페이지네이션 응답 처리 검증
  });

  test("manages authentication errors", () => {
    // 인증 에러 처리 검증
  });
});
```

## 🏗️ Advanced Test Infrastructure

### Backend Testing Setup
```python
# conftest.py
@pytest.fixture(scope="session")
def django_db_setup():
    """테스트 데이터베이스 설정"""

@pytest.fixture
def authenticated_client():
    """인증된 클라이언트 픽스처"""

@pytest.fixture
def sample_production_data():
    """생산 테스트 데이터 픽스처"""

@pytest.fixture
def haccp_compliant_setup():
    """HACCP 규정 준수 테스트 환경"""
```

### Frontend Testing Setup
```javascript
// setupTests.js
import "@testing-library/jest-dom";
import { server } from "./mocks/server";

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// Custom render with providers
export const renderWithProviders = (ui, options) => {
  // Router, Context 등을 포함한 커스텀 렌더 함수
};
```

### Test Data Management
```python
# factories.py - 테스트 데이터 팩토리 패턴
class MaterialFactory(factory.django.DjangoModelFactory):
    """원자재 테스트 데이터 팩토리"""

class ProductionOrderFactory(factory.django.DjangoModelFactory):
    """생산 주문 테스트 데이터 팩토리"""

class HACCPLogFactory(factory.django.DjangoModelFactory):
    """HACCP 로그 테스트 데이터 팩토리"""
```

## 🚀 Development Workflow & Execution

### Development Testing Workflow
```bash
# 1. 로컬 개발 시 - 빠른 피드백
pytest tests/unit/ -v                    # 백엔드 단위 테스트
npm test -- --watch                     # 프론트엔드 테스트 watch 모드

# 2. PR 전 - 전체 검증
pytest tests/ --cov=core --cov-report=html  # 백엔드 커버리지 포함
npm test -- --coverage                      # 프론트엔드 커버리지 포함

# 3. CI/CD Pipeline
pytest tests/ --cov=core --cov-fail-under=90   # 90% 커버리지 필수
npm test -- --coverage --watchAll=false       # 빌드 환경 테스트
```

## 📊 Test Metrics & Reporting

### Coverage Reports
- **Backend**: pytest-cov로 HTML 리포트 생성
- **Frontend**: Jest/Vitest 커버리지 리포트  
- **Integration**: API 엔드포인트 커버리지 추적

## 📋 Implementation Roadmap

### Phase 1: Core Testing (Week 1)
- [x] 백엔드 테스트 환경 구축 완료
- [ ] useEntityPage Hook 테스트 작성
- [ ] Service Layer 핵심 로직 테스트
- [ ] 기본 API 엔드포인트 테스트

### Phase 2: Business Logic Testing (Week 2)
- [ ] HACCP 컴플라이언스 로직 테스트
- [ ] BOM 계산 로직 테스트
- [ ] 재고 관리 로직 테스트
- [ ] 권한 시스템 테스트

### Phase 3: Integration & E2E (Week 3)
- [ ] 전체 워크플로우 통합 테스트
- [ ] 프론트엔드 페이지 레벨 테스트
- [ ] API 통합 테스트 (MSW)
- [ ] 성능 테스트 기본 구축

### Phase 4: Advanced Testing (Week 4)
- [ ] 동시성 테스트
- [ ] 보안 테스트
- [ ] 부하 테스트
- [ ] 모니터링 및 알림 테스트

이 테스트 계획은 **경험과 노하우**를 바탕으로, 단순한 기능 검증을 넘어 **비즈니스 요구사항과 도메인 규칙을 정확히 검증**하는 것에 중점을 둡니다.