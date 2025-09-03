# Development Best Practices

이 문서는 프로젝트에서 축적된 개발 노하우와 베스트 프랙티스를 정리합니다.

## Commit Message Guidelines

### 📋 기본 구조 (WHY → WHAT → HOW → 결과)

```
feat: [무엇을] 구현 완료

WHY: [왜] 기존 문제점과 구현 동기 설명

WHAT: 
- 클래스명: 구체적인 메소드들 나열
- 파일 경로와 주요 변경사항 포함
- 핵심 기능별 상세 설명

HOW:
문제: [어떤 문제가 있었는지]
해결책: [어떻게 해결했는지] 
결정 근거: [왜 이 방법을 선택했는지]
고려한 대안: [다른 방법도 고려했지만 선택하지 않은 이유]

결과: [테스트 통과율, 커버리지, 성능 개선 등 정량적 결과]
```

### 📝 상세 작성 가이드

#### 1. WHY (배경 및 문제점)
- **기술적 문제**: 성능 이슈, 버그, 아키텍처 문제
- **사용자 요구사항**: 새로운 기능 필요성, UX 개선
- **코드 품질**: 중복 코드, 유지보수성 문제
- **규정 준수**: HACCP 표준, 보안 요구사항

#### 2. WHAT (구체적 구현 내용)
- **파일 경로 포함**: `backend/core/services/haccp_service.py`
- **클래스/메소드명**: `HaccpService.validate_ccp_log_creation()`
- **주요 변경사항**: 추가/수정/삭제된 기능들
- **외부 의존성**: 새로 추가된 패키지나 설정

#### 3. HOW (해결 과정 및 의사결정) - 🔥 가장 중요
이 섹션이 커밋의 핵심가치입니다. 단순히 "어떻게 구현했는지"가 아니라 **"왜 그렇게 구현했는지"**를 설명합니다.

**구조**: 문제 → 해결책 → 결정 근거 → 고려한 대안

**좋은 예시**:
```
HOW:
문제: Serializer와 Model에서 동일한 CCP 한계값 검증 로직이 중복됨 (DRY 원칙 위배)
해결책: Model 레이어에서만 검증 처리하도록 통합, Serializer는 데이터 변환에만 집중
결정 근거: Django의 "fat models, thin views" 원칙에 따라 비즈니스 로직은 Model에서 처리하는 것이 적합. 
데이터 무결성 검증은 데이터베이스와 가장 가까운 레이어에서 수행하는 것이 안전.
고려한 대안: Service Layer에서 처리하는 방법도 고려했으나, 단순 검증 로직이므로 Model이 더 적절.
```

**나쁜 예시**:
```
HOW: Model 레이어에서 검증하도록 수정했습니다.
```

#### 4. 결과 (정량적 성과)
- **테스트**: `pytest 통과 25/25`, `커버리지 95%`
- **성능**: `응답시간 200ms → 50ms`, `메모리 사용량 30% 감소`
- **코드 품질**: `중복 코드 45줄 제거`, `순환 복잡도 8 → 4`
- **기능**: `새로운 API 엔드포인트 3개 추가`

### ❌ 금지사항

1. **자동 생성 문구 금지**
   ```
   ❌ 🤖 Generated with [Claude Code](https://claude.ai/code)
   ```

2. **추상적 표현 금지**
   ```
   ❌ feat: 기능 추가
   ❌ fix: 버그 수정
   ❌ refactor: 코드 개선
   ```

3. **의사결정 근거 누락 금지**
   ```
   ❌ HOW: Service Layer에서 처리하도록 변경
   ✅ HOW: 
   문제: 검증 로직이 여러 곳에 분산됨
   해결책: Service Layer에서 통합 처리
   결정 근거: 비즈니스 로직 중앙화로 유지보수성 향상, 테스트 용이성 증대
   ```

### ✅ 실전 예시

#### 예시 1: 아키텍처 개선
```
refactor: CCP 로그 검증 로직을 Model 레이어로 통합

WHY: CCPLogSerializer.create()와 CCPLog.save()에서 동일한 한계값 검증 로직이 중복되어 
코드 유지보수성이 저하되고, 검증 규칙 변경 시 여러 곳을 수정해야 하는 문제 발생

WHAT:
- backend/core/serializers/haccp_serializers.py: CCPLogCreateSerializer.create() 검증 로직 제거
- backend/core/models/haccp_models.py: CCPLog.save() 메소드에서 통합 검증 처리
- backend/core/constants.py: DUPLICATE_MEASUREMENT_THRESHOLD_MINUTES = 1 상수 추가

HOW:
문제: Serializer와 Model에서 is_within_limits 계산과 중복 측정값 체크가 중복됨 (25줄 중복)
해결책: Django의 레이어 책임에 따라 Model에서만 비즈니스 로직 처리
결정 근거: "fat models, thin views" 원칙 적용. Model은 데이터 무결성 보장, Serializer는 API 데이터 변환에 집중.
향후 다른 방식(API 외)으로 CCP 로그 생성 시에도 동일한 검증 로직이 자동 적용됨.
고려한 대안: Service Layer 패턴도 고려했으나, 단순 필드 검증이므로 Model이 더 적절

결과: 중복 코드 25줄 제거, 테스트 통과율 100% 유지, 검증 로직 단일 책임 구현
```

#### 예시 2: 신규 기능 구현
```
feat: CCP 로그 입력 폼 및 목록 조회 기능 구현

WHY: 기존 대시보드는 CCP 데이터를 조회만 가능했음. HACCP 규정 준수를 위해서는 
작업자가 실시간으로 중요관리점 측정값을 입력하고 이력을 관리할 수 있어야 함

WHAT:
- frontend/src/components/forms/CCPLogForm.js: CCP 선택, 측정값 입력, 유닛 설정 폼
- frontend/src/pages/CCPLogsPage.js: 로그 목록 + 페이지네이션 + 필터링
- frontend/src/services/ccpService.js: API 호출 로직 추상화
- backend/core/views/haccp_views.py: 권한별 필터링 로직 추가

HOW:
문제: 기존에는 백엔드 API만 있고 프론트엔드 UI가 없어서 Postman으로만 테스트 가능
해결책: React Hook Form + Tailwind CSS로 사용자 친화적 UI 구현
결정 근거: Hook Form 선택 이유는 성능(불필요한 리렌더링 방지)과 검증 기능이 뛰어나기 때문.
Tailwind CSS는 기존 컴포넌트들과 일관된 디자인 시스템 유지를 위해 선택.
고려한 대안: Formik도 고려했으나 Hook Form이 더 가볍고 성능이 우수

결과: CCP 로그 생성/조회 완전 구현, 사용자 권한별 필터링 정상 동작, 
프론트엔드-백엔드 통합 테스트 통과
```

### 🎯 커밋 작성 시 자문 체크리스트

1. **미래의 나**가 6개월 후에 이 커밋을 보고 "왜 이렇게 했지?"라고 궁금해하지 않을까?
2. **팀 동료**가 이 변경사항의 맥락을 이해할 수 있을까?
3. **코드 리뷰어**가 어떤 부분을 중점적으로 봐야 하는지 알 수 있을까?
4. **의사결정 근거**가 명확하게 설명되어 있는가?
5. **고려했던 대안**들과 최종 선택 이유가 포함되어 있는가?

이러한 상세한 가이드라인을 통해 코드 히스토리의 품질을 높이고, 프로젝트 지식이 축적되도록 합니다.

## 기술적 문제 해결 노하우

### DB 연결 이슈 해결
```bash
# 문제: Django mysqlclient에서 localhost 사용 시 Unix 소켓 에러
# 해결: Docker 환경에서는 127.0.0.1 사용 (TCP 포트)
DATABASE_HOST=127.0.0.1  # localhost 대신 사용

# mysqlclient 컴파일 에러 해결
sudo apt-get install libmysqlclient-dev
```

### Python 모듈 캐싱 이슈
```bash
# Django 서버에서 Python 파일 수정이 반영되지 않을 때
find . -name "*.pyc" -delete
find . -name "__pycache__" -exec rm -rf {} +
python manage.py runserver --noreload
```

### Docker 관련 이슈
```bash
# 포트 충돌 해결
lsof -t -i :8000 | xargs kill -9
lsof -t -i :3000 | xargs kill -9

# DB 볼륨 완전 초기화
docker-compose down -v
docker volume prune
docker-compose up -d db
```

## 환경 설정 베스트 프랙티스

### 1. 환경 변수 관리
```bash
# .env.example 템플릿 제공
SECRET_KEY="your-django-secret-key-here"
DEBUG=True
DATABASE_NAME=mes_db
DATABASE_USER=mes_user
DATABASE_PASSWORD=mes_password
DATABASE_HOST=127.0.0.1
DATABASE_PORT=3306

# 절대 하드코딩 금지
❌ SECRET_KEY = "hardcoded-secret-key"
✅ SECRET_KEY = os.getenv('SECRET_KEY')
```

### 2. Docker 설정
```yaml
# docker-compose.yml 최신 문법 (version 필드 제거)
services:
  db:
    image: mariadb:10.6
    environment:
      MYSQL_ROOT_PASSWORD: root123
    # 나머지 설정...
```

### 3. 의존성 관리
```bash
# requirements.txt 정확한 버전 명시
Django==5.2.5
djangorestframework==3.16.0
djangorestframework-simplejwt==5.3.1

# 개발/프로덕션 분리
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 테스트, 린팅 등
```

## 테스트 작성 베스트 프랙티스

### 1. 테스트 메소드 명명 규칙
```python
def test_[동작]_[조건]_[예상결과](self):
    # 예시
    def test_create_user_with_valid_data_returns_success(self):
    def test_login_with_invalid_password_raises_authentication_error(self):
    def test_calculate_compliance_score_with_empty_logs_returns_zero(self):
```

### 2. Given-When-Then 구조
```python
def test_calculate_compliance_score_returns_correct_percentage(self):
    # Given: 테스트 데이터 준비
    user = create_test_user(role='quality_manager')
    ccp = create_test_ccp()
    create_compliant_logs(ccp, count=8)
    create_non_compliant_logs(ccp, count=2)
    
    # When: 실제 동작 실행
    service = HaccpService()
    result = service.calculate_compliance_score()
    
    # Then: 결과 검증
    assert result['compliance_score'] == 80.0
    assert result['total_logs'] == 10
```

### 3. 예외 상황 테스트
```python
def test_create_ccp_log_without_permission_raises_error(self):
    # 권한 없는 사용자로 CCP 로그 생성 시도
    user = create_test_user(role='operator')
    
    with pytest.raises(PermissionDenied):
        service.validate_ccp_log_creation(user, ccp, value)
```

## 코드 품질 관리

### 1. 린팅 및 포맷팅
```bash
# Black (코드 포맷터)
black backend/

# Flake8 (린터)
flake8 backend/ --max-line-length=88

# isort (import 정렬)
isort backend/
```

### 2. 코드 리뷰 체크리스트
- [ ] 비즈니스 로직이 Service Layer에 있는가?
- [ ] SQL Injection 취약점은 없는가?
- [ ] 민감한 정보 (SECRET_KEY, 비밀번호)가 하드코딩되지 않았는가?
- [ ] 테스트 케이스가 충분한가? (정상/예외 케이스)
- [ ] 변수명과 함수명이 명확한가?
- [ ] 불필요한 주석이나 디버그 코드는 없는가?

### 3. 성능 최적화
```python
# N+1 쿼리 방지
❌ for log in ccp_logs:
    print(log.ccp.name)  # 매번 DB 쿼리

✅ ccp_logs = CCPLog.objects.select_related('ccp')
    for log in ccp_logs:
        print(log.ccp.name)  # 한 번의 쿼리

# 불필요한 필드 제외
❌ logs = CCPLog.objects.all()

✅ logs = CCPLog.objects.only('id', 'measure_value', 'created_at')
```

## API 설계 베스트 프랙티스

### 1. RESTful URL 설계
```python
# 좋은 예시
GET  /api/production-orders/         # 목록 조회
POST /api/production-orders/         # 생성
GET  /api/production-orders/123/     # 상세 조회
PUT  /api/production-orders/123/     # 전체 수정
PATCH /api/production-orders/123/    # 부분 수정

# 커스텀 액션
POST /api/production-orders/123/start/    # 생산 시작
POST /api/production-orders/123/complete/ # 생산 완료
```

### 2. 에러 응답 표준화
```python
# 일관된 에러 응답 형식
{
    "error": "VALIDATION_ERROR",
    "message": "입력값이 유효하지 않습니다.",
    "details": {
        "measure_value": ["이 값은 0보다 커야 합니다."]
    },
    "timestamp": "2025-09-02T10:30:00Z"
}
```

### 3. 페이징 표준화
```python
{
    "count": 150,
    "next": "http://api.example.com/logs/?page=3",
    "previous": "http://api.example.com/logs/?page=1", 
    "results": [...]
}
```

## 보안 베스트 프랙티스

### 1. 인증/인가
```python
# 모든 API 엔드포인트에 인증 필수
permission_classes = [IsAuthenticated]

# 세밀한 권한 제어
class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user or request.user.role == 'admin'
```

### 2. 입력값 검증
```python
# Serializer 레벨 검증
class CCPLogCreateSerializer(serializers.ModelSerializer):
    def validate_measure_value(self, value):
        if value <= 0:
            raise serializers.ValidationError("측정값은 0보다 커야 합니다.")
        return value

# Service Layer 비즈니스 검증
def validate_ccp_log_creation(self, user, ccp, measure_value):
    if not user.has_perm('core.add_ccplog'):
        raise PermissionDenied("CCP 로그 생성 권한이 없습니다.")
```

### 3. SQL Injection 방지
```python
# Django ORM 사용 (자동 이스케이프)
✅ User.objects.filter(username=username)

# Raw SQL 사용 시 파라미터 바인딩
✅ cursor.execute("SELECT * FROM users WHERE username = %s", [username])

# 문자열 포맷팅 절대 금지
❌ cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
```

## 프론트엔드 베스트 프랙티스

### 1. 컴포넌트 설계
```jsx
// 단일 책임 원칙
const SummaryCard = ({ title, value, icon, color }) => {
    return (
        <div className={`bg-white shadow rounded-lg ${color}`}>
            <div className="flex items-center">
                <div className="flex-shrink-0">{icon}</div>
                <div className="ml-5 w-0 flex-1">
                    <dl>
                        <dt className="text-sm font-medium text-gray-500">
                            {title}
                        </dt>
                        <dd className="text-lg font-medium text-gray-900">
                            {value}
                        </dd>
                    </dl>
                </div>
            </div>
        </div>
    );
};
```

### 2. 에러 처리
```jsx
// 일관된 에러 처리
const fetchDashboardData = async () => {
    try {
        setLoading(true);
        const response = await apiClient.get('/api/statistics/');
        setStats(response.data);
    } catch (error) {
        toast.error('데이터를 불러오는 중 오류가 발생했습니다.');
        console.error('Dashboard data fetch error:', error);
    } finally {
        setLoading(false);
    }
};
```

### 3. 성능 최적화
```jsx
// 불필요한 리렌더링 방지
const ExpensiveComponent = React.memo(({ data }) => {
    return <div>{/* expensive rendering */}</div>;
});

// 지연 로딩
const LazyComponent = React.lazy(() => import('./LazyComponent'));

// useCallback으로 함수 메모이제이션
const handleSubmit = useCallback((data) => {
    // submit logic
}, [dependency]);
```

이러한 베스트 프랙티스를 통해 코드 품질을 높이고 유지보수성을 향상시킬 수 있습니다.