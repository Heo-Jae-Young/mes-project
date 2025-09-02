# Development Best Practices

이 문서는 프로젝트에서 축적된 개발 노하우와 베스트 프랙티스를 정리합니다.

## Commit Message Guidelines

### 자연스러운 커밋/PR 작성법

#### 기본 구조
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

#### 작성 원칙
- **WHY 먼저 설명**: 왜 이 작업을 했는지 배경과 문제점 설명
- **WHAT 구체적으로**: 실제 구현한 클래스/메소드명 나열
- **HOW 경험담**: 삽질했던 부분과 해결 과정 솔직하게 기록
- **결과 요약**: 테스트 통과, 커버리지 등 정량적 결과

#### 금지사항
- 과도한 이모지나 템플릿 형식 피하기
- **Generated with [Claude Code] 같은 자동 생성 문구 사용 금지**
- "구현했다", "작업했다" 같은 당연한 표현 지양

#### 좋은 예시
```
feat: 대시보드 통계 API 구현 및 종합 개발 문서 완성

기존 대시보드는 하드코딩된 더미 데이터("실시간 모니터링 중", "정상 운영 중")만 표시했습니다. 
실제 사용자가 의미 있는 정보를 얻으려면 백엔드에서 계산된 실제 통계 데이터가 필요했습니다.

구현한 내용:
- StatisticsAPIView: HACCP 준수율, 중요 이탈 건수, 진행중 생산 오더 수 계산
- DashboardPage.js: 3개 API 병렬 호출 (Promise.all) 및 동적 렌더링
- 백엔드/프론트엔드 데이터 흐름 다이어그램 작성

구현 과정 삽질:
- API 엔드포인트 라우팅 누락 → core/urls.py에 path 추가 및 __init__.py import 추가
- CCP 로그 데이터 구조 불일치 → 관계된 모델 필드 포함하도록 수정 필요 (향후 작업)

결과: 정적 텍스트에서 동적 데이터로 업그레이드 ("85.42%", "3 건", "2 건")
백엔드 API 테스트 정상 응답, 프론트엔드 렌더링 확인 완료
```

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