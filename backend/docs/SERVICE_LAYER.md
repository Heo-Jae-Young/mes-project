# Service Layer Architecture

이 문서는 Django 백엔드의 Service Layer 패턴 구현과 비즈니스 로직 구조를 설명합니다.

## Service Layer 패턴

### 설계 원칙
- **View는 얇게**: HTTP 요청/응답 처리만 담당
- **Service는 두껍게**: 비즈니스 로직의 핵심 구현
- **Model은 단순하게**: 데이터 정의와 기본 유효성 검사만

### 계층 구조
```
HTTP Request → View → Service → Model → Database
                ↓       ↓       ↓
             HTTP    Business  Data
           Handling    Logic   Access
```

## 구현된 서비스 클래스

### 1. HaccpService (`haccp_service.py`)

HACCP 컴플라이언스 관련 비즈니스 로직을 담당합니다.

```python
class HaccpService:
    def validate_ccp_log_creation(self, user, ccp, measure_value):
        """CCP 로그 생성 전 검증"""
        # 권한 검증
        # 시간 제약 검증  
        # 측정값 유효성 검증

    def calculate_compliance_score(self, date_from=None, date_to=None):
        """HACCP 컴플라이언스 점수 계산"""
        # 기간 내 모든 CCP 로그 조회
        # 준수/이탈 비율 계산
        # 가중치 적용 점수 산출

    def get_critical_alerts(self, user=None, hours=24):
        """중요 알림 목록 조회"""
        # 최근 지정 시간 내 이탈 건 조회
        # 사용자 권한별 필터링

    def generate_compliance_report(self, date_from, date_to):
        """컴플라이언스 보고서 생성"""
        # 기간별 통계 집계
        # 트렌드 분석
        # 리포트 데이터 구조화

class HaccpQueryService:
    def get_ccp_logs_for_user(self, user):
        """사용자별 CCP 로그 조회"""
        # 역할별 접근 권한 필터링

    def get_ccps_for_user(self, user):
        """접근 가능한 CCP 목록"""
        # 부서/역할별 CCP 필터링
```

### 2. ProductionService (`production_service.py`)

생산 관리 및 효율성 계산 로직을 담당합니다.

```python
class ProductionService:
    def validate_production_order_creation(self, product, quantity, user):
        """생산 주문 생성 검증"""
        # 원자재 재고 충분성 확인
        # 생산 능력 검증
        # 권한 확인

    def start_production(self, order_id, user):
        """생산 시작 처리"""
        # 원자재 할당 및 예약
        # 상태 변경 (planned → in_progress)
        # 시작 시간 기록

    def complete_production(self, order_id, actual_quantity, user):
        """생산 완료 처리"""
        # 실제 생산량 기록
        # 원자재 소비량 계산
        # 완성품 재고 업데이트
        # 효율성 지표 계산

    def get_production_efficiency(self, order_id):
        """효율성 지표 계산"""
        # 계획 vs 실제 비교
        # 시간 효율성
        # 수율 계산

class ProductionQueryService:
    def get_production_orders_for_user(self, user):
        """역할별 생산 주문 조회"""
        # 권한별 필터링 (관리자: 전체, 작업자: 담당 라인만)

    def get_production_dashboard_data(self, user):
        """대시보드 데이터"""
        # 진행 중인 주문 수
        # 완료율
        # 평균 효율성

class MaterialTraceabilityService:
    def get_material_traceability(self, lot_id):
        """원자재 추적성 조회"""
        # 특정 LOT의 전체 이력 추적

    def get_forward_traceability(self, lot_id):
        """전방 추적성"""
        # 원자재 → 완성품 추적
```

### 3. SupplierService (`supplier_service.py`)

공급업체 관리 및 성과 평가 로직을 담당합니다.

```python
class SupplierService:
    def validate_supplier_creation(self, name, haccp_certified):
        """공급업체 등록 검증"""
        # 중복 이름 확인
        # HACCP 인증 필수 검증

    def evaluate_supplier_performance(self, supplier_id, period_months=12):
        """성과 평가"""
        # 품질 지표 (불량률, 클레임)
        # 배송 지표 (정시 배송률)
        # 가격 경쟁력
        # 종합 점수 산출

    def get_supplier_risk_assessment(self, supplier_id):
        """리스크 평가"""
        # 재무 건전성
        # 인증 상태
        # 과거 이슈 이력
        # 리스크 등급 판정

class SupplierQueryService:
    def get_suppliers_for_user(self, user):
        """역할별 공급업체 조회"""
        # 구매 담당자: 전체, 품질 관리자: 품질 이슈 있는 업체만

    def get_supplier_statistics(self):
        """통계 정보"""
        # 총 공급업체 수
        # HACCP 인증 비율
        # 평균 성과 점수

class SupplierAuditService:
    def schedule_supplier_audit(self, supplier_id, audit_date, auditor):
        """감사 일정 등록"""
        # 감사 계획 생성
        # 알림 발송

    def get_audit_checklist(self, supplier_id):
        """감사 체크리스트"""
        # 표준 감사 항목
        # 업체별 특화 항목
```

## Service Layer 사용 패턴

### ViewSet에서 Service 호출
```python
class CCPLogViewSet(viewsets.ModelViewSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.haccp_service = HaccpService()
        self.haccp_query_service = HaccpQueryService()

    def perform_create(self, serializer):
        # Service Layer 검증 호출
        self.haccp_service.validate_ccp_log_creation(
            user=self.request.user,
            ccp=serializer.validated_data['ccp'],
            measure_value=serializer.validated_data['measure_value']
        )
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        # Service Layer 권한 필터링 사용
        return self.haccp_query_service.get_ccp_logs_for_user(
            self.request.user
        )
```

## 핵심 설계 특징

### 1. HACCP 특화 로직
- **컴플라이언스 점수**: 실시간 준수율 계산
- **중요 이탈 감지**: 임계값 초과 자동 감지
- **감사 추적**: 모든 변경 사항 이력 관리

### 2. 역할 기반 접근 제어
- **admin**: 모든 데이터 접근 가능
- **quality_manager**: 품질 관련 데이터만
- **operator**: 담당 라인/부서 데이터만

### 3. 데이터 무결성 보장
- **트랜잭션 처리**: 복잡한 업무는 atomic 처리
- **검증 로직**: 비즈니스 규칙 엄격 적용
- **예외 처리**: 명확한 에러 메시지

### 4. 추적성 완전 보장
- **Forward Traceability**: 원자재 → 완성품
- **Backward Traceability**: 완성품 → 원자재  
- **LOT 관리**: 배치별 완전 추적

### 5. 성과 지표 자동 계산
- **생산 효율성**: 계획 vs 실제 비교
- **품질 지표**: 불량률, 재작업률
- **공급업체 성과**: 정시 배송률, 품질 수준

## 테스트 커버리지

현재 Service Layer는 **25개 단위 테스트 모두 통과**하며 다음과 같은 시나리오를 검증합니다:

- **정상 케이스**: 올바른 입력값에 대한 정상 처리
- **예외 케이스**: 권한 없음, 잘못된 입력값 등
- **경계 조건**: 최대/최소값, 시간 제약 등
- **비즈니스 규칙**: HACCP 규정, 생산 제약 등

## 향후 확장 계획

### 추가 예정 서비스
- **NotificationService**: 실시간 알림 시스템
- **ReportService**: 다양한 보고서 생성
- **WorkflowService**: 승인/검토 워크플로우
- **IntegrationService**: 외부 시스템 연동