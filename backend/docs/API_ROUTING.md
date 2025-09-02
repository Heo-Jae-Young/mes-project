# Django DRF API 라우팅 시스템

## 🛣️ REST 경로 → 함수 연결 흐름

### 전체 라우팅 구조
```
HTTP 요청: GET /api/ccps/123/monitoring_logs/
     ↓
1. mes_backend/urls.py: path('api/', include('core.urls'))
     ↓
2. core/urls.py: router.register(r'ccps', CCPViewSet)
     ↓  
3. DRF Router: 자동 URL 생성
     ↓
4. CCPViewSet.monitoring_logs() 메소드 실행
```

## 📍 URL 패턴 매칭 과정

### 1단계: 메인 URL 매칭
```python
# mes_backend/urls.py
urlpatterns = [
    path('api/', include('core.urls')),  # /api/ 제거 후 core.urls로 전달
]
```

### 2단계: DRF Router가 ViewSet 매칭
```python
# core/urls.py  
router = DefaultRouter()
router.register(r'ccps', CCPViewSet, basename='ccp')  # ccps/ → CCPViewSet
```

### 3단계: DRF 자동 URL 생성
```python
# ViewSet의 @action 데코레이터 기반
@action(detail=True, methods=['get'])   # detail=True → {id} 필요
def monitoring_logs(self, request, pk=None):
    # URL: GET /api/ccps/{id}/monitoring_logs/
    
@action(detail=False, methods=['get'])  # detail=False → {id} 없음  
def critical_alerts(self, request):
    # URL: GET /api/ccps/critical_alerts/
```

## 🎯 DRF ViewSet 메소드 타입

### 기본 CRUD 메소드 (자동 매핑)
| HTTP 메소드 | URL 패턴 | ViewSet 메소드 | 설명 |
|-------------|----------|----------------|------|
| GET | `/api/ccps/` | `list()` | 전체 목록 조회 |
| POST | `/api/ccps/` | `create()` | 새 항목 생성 |
| GET | `/api/ccps/{id}/` | `retrieve()` | 개별 항목 조회 |
| PUT | `/api/ccps/{id}/` | `update()` | 전체 수정 |
| PATCH | `/api/ccps/{id}/` | `partial_update()` | 부분 수정 |
| DELETE | `/api/ccps/{id}/` | `destroy()` | 삭제 |

### 커스텀 액션 메소드
| 데코레이터 | URL 패턴 | 예시 |
|------------|----------|------|
| `@action(detail=True)` | `/api/ccps/{id}/action_name/` | 특정 CCP의 상세 정보 |
| `@action(detail=False)` | `/api/ccps/action_name/` | CCP 전체 관련 작업 |

## 🔧 실제 프로젝트 예시

### CCPViewSet의 URL 매핑
```python
class CCPViewSet(viewsets.ModelViewSet):
    # 기본 CRUD
    # GET /api/ccps/ → list()
    # POST /api/ccps/ → create() 
    # GET /api/ccps/123/ → retrieve(pk=123)
    
    # 커스텀 액션들
    @action(detail=True, methods=['get'])
    def monitoring_logs(self, request, pk=None):
        # GET /api/ccps/123/monitoring_logs/
        ccp = self.get_object()  # pk=123으로 CCP 조회
        
    @action(detail=True, methods=['get']) 
    def compliance_report(self, request, pk=None):
        # GET /api/ccps/123/compliance_report/
        
    @action(detail=False, methods=['get'])
    def critical_alerts(self, request):
        # GET /api/ccps/critical_alerts/
        
    @action(detail=False, methods=['get'])
    def types(self, request):
        # GET /api/ccps/types/
```

## 🛠️ 개발 도구

### URL 패턴 확인 방법
```bash
# Django shell에서 URL 패턴 확인
python manage.py shell
>>> from core.urls import router
>>> for url in router.urls:
...     print(f"{url.pattern} → {url.name}")

# 또는 django-extensions 사용
pip install django-extensions
python manage.py show_urls | grep ccp
```

### Swagger UI에서 확인
- `http://localhost:8000/api/docs/`
- 모든 생성된 엔드포인트와 매개변수 확인 가능

## 💡 개발 팁

### 1. Action 네이밍 규칙
```python
# ✅ 좋은 예
@action(detail=True, methods=['get'])
def monitoring_logs(self, request, pk=None):  # snake_case
    # URL: /api/ccps/123/monitoring-logs/ (자동으로 kebab-case 변환)

# ❌ 피할 것  
@action(detail=True, methods=['get'])
def monitoringLogs(self, request, pk=None):  # camelCase는 피하기
```

### 2. 매개변수 처리
```python
@action(detail=True, methods=['get'])
def monitoring_logs(self, request, pk=None):
    # URL에서 추출: /api/ccps/123/monitoring_logs/?days=30&status=critical
    ccp = self.get_object()  # pk=123 사용
    days = int(request.query_params.get('days', '30'))  # Query parameter
    status = request.query_params.get('status')  # Query parameter
```

### 3. HTTP 메소드 매핑
```python
@action(detail=True, methods=['get', 'post'])
def monitoring_logs(self, request, pk=None):
    if request.method == 'GET':
        # 로그 조회 로직
    elif request.method == 'POST': 
        # 새 로그 추가 로직
```

## 🚨 주의사항

### URL 충돌 방지
```python
# ❌ 충돌 발생
router.register(r'ccps', CCPViewSet)
router.register(r'ccp-logs', CCPLogViewSet)  # 이미 ccps/{id}/logs/ 패턴과 충돌 가능

# ✅ 명확한 구분
router.register(r'ccps', CCPViewSet)  
router.register(r'ccp-logs', CCPLogViewSet)  # 완전히 다른 리소스로 처리
```

### 권한 처리
```python
@action(detail=True, methods=['get'])
def sensitive_data(self, request, pk=None):
    # ViewSet의 permission_classes가 자동 적용됨
    # 추가 권한 체크가 필요한 경우
    if request.user.role not in ['admin']:
        raise PermissionDenied()
```