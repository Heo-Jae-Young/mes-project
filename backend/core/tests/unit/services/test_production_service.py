import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.exceptions import ValidationError, PermissionDenied

from core.services.production_service import (
    ProductionService, 
    ProductionQueryService, 
    MaterialTraceabilityService
)
from core.models import (
    ProductionOrder, FinishedProduct, MaterialLot, 
    RawMaterial, Supplier, CCPLog, BOM
)

User = get_user_model()


@pytest.mark.unit
@pytest.mark.django_db
class TestProductionService:
    """Production Service 단위 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.production_service = ProductionService()
        self.current_time = timezone.now()
        
        # Test Users
        self.admin_user = User.objects.create_user(
            username='admin_prod',
            password='test123',
            role='admin'
        )
        self.production_manager = User.objects.create_user(
            username='prod_manager',
            password='test123',
            role='production_manager'
        )
        self.quality_manager = User.objects.create_user(
            username='quality_prod',
            password='test123',
            role='quality_manager'
        )
        self.operator = User.objects.create_user(
            username='operator_prod',
            password='test123',
            role='operator'
        )
        self.viewer = User.objects.create_user(
            username='viewer_prod',
            password='test123',
            role='viewer'
        )
        
        # Test Supplier
        self.test_supplier = Supplier.objects.create(
            name='테스트 공급업체',
            code='SUP-001',
            contact_person='담당자',
            email='supplier@test.com',
            phone='010-1234-5678',
            address='테스트 주소',
            status='active',
            created_by=self.admin_user
        )
        
        # Test Raw Material
        self.test_material = RawMaterial.objects.create(
            name='테스트 원자재',
            code='MAT-001',
            category='ingredient',
            description='테스트용 원자재',
            unit='kg',
            supplier=self.test_supplier,
            is_active=True,
            created_by=self.admin_user
        )
        
        # Test Material Lot with sufficient stock
        self.test_lot = MaterialLot.objects.create(
            raw_material=self.test_material,
            supplier=self.test_supplier,
            lot_number='LOT-001',
            quantity_received=Decimal('50.0'),
            quantity_current=Decimal('50.0'),
            unit_price=Decimal('1000.00'),
            received_date=self.current_time.date(),
            expiry_date=self.current_time.date() + timedelta(days=30),
            quality_test_passed=True,
            status='in_storage',
            created_by=self.admin_user
        )
        
        # Test Product
        self.test_product = FinishedProduct.objects.create(
            code='PROD-001',
            name='테스트 제품',
            description='테스트용 완제품',
            version='1.0',
            shelf_life_days=30,
            net_weight=Decimal('1.000'),
            packaging_type='박스',
            is_active=True,
            created_by=self.admin_user
        )
        
        # Test BOM
        self.test_bom = BOM.objects.create(
            finished_product=self.test_product,
            raw_material=self.test_material,
            quantity_per_unit=Decimal('2.0'),  # 제품 1개당 원자재 2kg 필요
            is_active=True,
            created_by=self.admin_user
        )

    def test_validate_production_order_creation_success(self):
        """정상적인 생산 주문 생성 검증 테스트"""
        order_data = {
            'planned_start_date': self.current_time + timedelta(hours=1),
            'planned_end_date': self.current_time + timedelta(hours=9)
        }
        
        # 예외가 발생하지 않아야 함
        self.production_service.validate_production_order_creation(
            order_data=order_data,
            user=self.production_manager
        )

    def test_validate_production_order_creation_permission_denied(self):
        """권한 없는 사용자의 생산 주문 생성 시도 테스트"""
        order_data = {
            'planned_start_date': self.current_time + timedelta(hours=1),
            'planned_end_date': self.current_time + timedelta(hours=9)
        }
        
        with pytest.raises(PermissionDenied, match='생산 주문 생성 권한이 없습니다'):
            self.production_service.validate_production_order_creation(
                order_data=order_data,
                user=self.viewer
            )

    def test_validate_production_order_creation_invalid_dates(self):
        """잘못된 날짜 설정 검증 테스트"""
        # 종료 시간이 시작 시간보다 이른 경우
        order_data = {
            'planned_start_date': self.current_time + timedelta(hours=9),
            'planned_end_date': self.current_time + timedelta(hours=1)
        }
        
        with pytest.raises(ValidationError, match='계획 종료 시간은 시작 시간보다 늦어야 합니다'):
            self.production_service.validate_production_order_creation(
                order_data=order_data,
                user=self.production_manager
            )

    def test_validate_production_order_creation_past_time(self):
        """과거 시간 설정 검증 테스트"""
        order_data = {
            'planned_start_date': self.current_time - timedelta(hours=1),
            'planned_end_date': self.current_time + timedelta(hours=8)
        }
        
        with pytest.raises(ValidationError, match='계획 시작 시간은 현재 시간 이후여야 합니다'):
            self.production_service.validate_production_order_creation(
                order_data=order_data,
                user=self.production_manager
            )

    def test_start_production_success(self):
        """정상적인 생산 시작 테스트"""
        # Test Production Order
        production_order = ProductionOrder.objects.create(
            order_number='ORD-001',
            finished_product=self.test_product,
            planned_quantity=Decimal('10'),  # 10개 생산 (원자재 20kg 필요)
            planned_start_date=self.current_time,
            planned_end_date=self.current_time + timedelta(hours=8),
            status='planned',
            priority='normal',
            created_by=self.admin_user
        )
        
        result = self.production_service.start_production(
            production_order=production_order,
            user=self.operator
        )
        
        # 생산 주문 상태 확인
        assert result.status == 'in_progress'
        assert result.actual_start_date is not None
        assert result.assigned_operator == self.operator
        
        # 원자재 재고 차감 확인
        self.test_lot.refresh_from_db()
        assert self.test_lot.quantity_current == Decimal('30.0')  # 50 - 20 = 30

    def test_start_production_permission_denied(self):
        """권한 없는 사용자의 생산 시작 시도 테스트"""
        production_order = ProductionOrder.objects.create(
            order_number='ORD-002',
            finished_product=self.test_product,
            planned_quantity=Decimal('5'),
            planned_start_date=self.current_time,
            planned_end_date=self.current_time + timedelta(hours=8),
            status='planned',
            priority='normal',
            created_by=self.admin_user
        )
        
        with pytest.raises(PermissionDenied, match='생산 시작 권한이 없습니다'):
            self.production_service.start_production(
                production_order=production_order,
                user=self.viewer
            )

    def test_start_production_invalid_status(self):
        """잘못된 상태의 생산 주문 시작 시도 테스트"""
        production_order = ProductionOrder.objects.create(
            order_number='ORD-003',
            finished_product=self.test_product,
            planned_quantity=Decimal('5'),
            planned_start_date=self.current_time,
            planned_end_date=self.current_time + timedelta(hours=8),
            status='completed',  # 이미 완료된 주문
            priority='normal',
            created_by=self.admin_user
        )
        
        with pytest.raises(ValidationError, match='계획 상태의 주문만 시작할 수 있습니다'):
            self.production_service.start_production(
                production_order=production_order,
                user=self.operator
            )

    def test_start_production_insufficient_materials(self):
        """원자재 부족 시 생산 시작 실패 테스트"""
        # 재고를 부족하게 설정
        self.test_lot.quantity_current = Decimal('5.0')
        self.test_lot.save()
        
        production_order = ProductionOrder.objects.create(
            order_number='ORD-004',
            finished_product=self.test_product,
            planned_quantity=Decimal('10'),  # 20kg 필요하지만 5kg만 있음
            planned_start_date=self.current_time,
            planned_end_date=self.current_time + timedelta(hours=8),
            status='planned',
            priority='normal',
            created_by=self.admin_user
        )
        
        with pytest.raises(ValidationError, match='원자재 부족'):
            self.production_service.start_production(
                production_order=production_order,
                user=self.operator
            )

    def test_complete_production_success(self):
        """정상적인 생산 완료 테스트"""
        production_order = ProductionOrder.objects.create(
            order_number='ORD-005',
            finished_product=self.test_product,
            planned_quantity=Decimal('10'),
            planned_start_date=self.current_time - timedelta(hours=8),
            planned_end_date=self.current_time,
            status='in_progress',
            actual_start_date=self.current_time - timedelta(hours=8),
            priority='normal',
            created_by=self.admin_user
        )
        
        result = self.production_service.complete_production(
            production_order=production_order,
            produced_quantity=Decimal('9'),  # 계획 대비 90% 생산
            user=self.operator,
            completion_notes='정상 완료'
        )
        
        assert result.status == 'completed'
        assert result.produced_quantity == Decimal('9')
        assert result.actual_end_date is not None
        assert '정상 완료' in result.notes

    def test_complete_production_permission_denied(self):
        """권한 없는 사용자의 생산 완료 시도 테스트"""
        production_order = ProductionOrder.objects.create(
            order_number='ORD-006',
            finished_product=self.test_product,
            planned_quantity=Decimal('10'),
            planned_start_date=self.current_time - timedelta(hours=8),
            planned_end_date=self.current_time,
            status='in_progress',
            priority='normal',
            created_by=self.admin_user
        )
        
        with pytest.raises(PermissionDenied, match='생산 완료 권한이 없습니다'):
            self.production_service.complete_production(
                production_order=production_order,
                produced_quantity=Decimal('9'),
                user=self.viewer
            )

    def test_complete_production_invalid_quantity(self):
        """잘못된 생산량으로 완료 시도 테스트"""
        production_order = ProductionOrder.objects.create(
            order_number='ORD-007',
            finished_product=self.test_product,
            planned_quantity=Decimal('10'),
            planned_start_date=self.current_time - timedelta(hours=8),
            planned_end_date=self.current_time,
            status='in_progress',
            priority='normal',
            created_by=self.admin_user
        )
        
        # 계획 수량의 10% 이상 초과 시도
        with pytest.raises(ValidationError, match='계획 수량을 10% 이상 초과할 수 없습니다'):
            self.production_service.complete_production(
                production_order=production_order,
                produced_quantity=Decimal('12'),  # 120% 생산
                user=self.operator
            )

    def test_get_production_efficiency_success(self):
        """생산 효율성 계산 테스트"""
        production_order = ProductionOrder.objects.create(
            order_number='ORD-008',
            finished_product=self.test_product,
            planned_quantity=Decimal('10'),
            produced_quantity=Decimal('9'),  # 90% 수량 효율성
            planned_start_date=self.current_time - timedelta(hours=8),
            planned_end_date=self.current_time,
            actual_start_date=self.current_time - timedelta(hours=8),
            actual_end_date=self.current_time - timedelta(hours=2),  # 6시간만 소요 (시간 효율성 133%)
            status='completed',
            priority='normal',
            created_by=self.admin_user
        )
        
        result = self.production_service.get_production_efficiency(production_order)
        
        assert result is not None
        assert result['quantity_efficiency'] == 90.0  # 9/10 * 100
        assert result['time_efficiency'] == 133.33  # 8/6 * 100 (반올림)
        assert result['haccp_compliance'] == 100.0  # CCP 로그 없으므로 100%
        assert 'overall_efficiency' in result

    def test_get_production_efficiency_incomplete_order(self):
        """미완료 주문의 효율성 조회 테스트"""
        production_order = ProductionOrder.objects.create(
            order_number='ORD-009',
            finished_product=self.test_product,
            planned_quantity=Decimal('10'),
            planned_start_date=self.current_time,
            planned_end_date=self.current_time + timedelta(hours=8),
            status='planned',
            priority='normal',
            created_by=self.admin_user
        )
        
        result = self.production_service.get_production_efficiency(production_order)
        
        assert result is None

    def test_calculate_required_materials_success(self):
        """BOM 기반 원자재 소요량 계산 테스트"""
        production_order = ProductionOrder.objects.create(
            order_number='ORD-010',
            finished_product=self.test_product,
            planned_quantity=Decimal('5'),  # 5개 생산 계획
            planned_start_date=self.current_time,
            planned_end_date=self.current_time + timedelta(hours=8),
            status='planned',
            priority='normal',
            created_by=self.admin_user
        )
        
        result = self.production_service._calculate_required_materials(production_order)
        
        # 5개 * 2kg/개 = 10kg 필요
        assert result['MAT-001'] == Decimal('10.0')

    def test_calculate_required_materials_no_bom(self):
        """BOM이 없는 제품의 소요량 계산 테스트"""
        # BOM이 없는 새로운 제품 생성
        product_without_bom = FinishedProduct.objects.create(
            code='PROD-NO-BOM',
            name='BOM 없는 제품',
            description='BOM 설정 안된 제품',
            version='1.0',
            shelf_life_days=30,
            net_weight=Decimal('1.000'),
            packaging_type='박스',
            is_active=True,
            created_by=self.admin_user
        )
        
        production_order = ProductionOrder.objects.create(
            order_number='ORD-011',
            finished_product=product_without_bom,
            planned_quantity=Decimal('5'),
            planned_start_date=self.current_time,
            planned_end_date=self.current_time + timedelta(hours=8),
            status='planned',
            priority='normal',
            created_by=self.admin_user
        )
        
        with pytest.raises(ValidationError, match='BOM이 설정되지 않았습니다'):
            self.production_service._calculate_required_materials(production_order)

    def test_get_available_material_quantity(self):
        """가용 원자재 수량 조회 테스트"""
        # 추가 로트 생성 (품질 검사 미통과)
        MaterialLot.objects.create(
            raw_material=self.test_material,
            supplier=self.test_supplier,
            lot_number='LOT-002',
            quantity_received=Decimal('30.0'),
            quantity_current=Decimal('30.0'),
            unit_price=Decimal('1000.00'),
            received_date=self.current_time.date(),
            expiry_date=self.current_time.date() + timedelta(days=30),
            quality_test_passed=False,  # 품질 검사 미통과
            status='in_storage',
            created_by=self.admin_user
        )
        
        result = self.production_service._get_available_material_quantity('MAT-001')
        
        # 품질 검사 통과한 로트만 계산되어야 함 (50kg)
        assert result == Decimal('50.0')

    def test_allocate_materials_fifo(self):
        """FIFO 방식 원자재 할당 테스트"""
        # 두 번째 로트 생성 (더 늦은 날짜)
        second_lot = MaterialLot.objects.create(
            raw_material=self.test_material,
            supplier=self.test_supplier,
            lot_number='LOT-003',
            quantity_received=Decimal('30.0'),
            quantity_current=Decimal('30.0'),
            unit_price=Decimal('1000.00'),
            received_date=self.current_time.date() + timedelta(days=1),  # 하루 늦음
            expiry_date=self.current_time.date() + timedelta(days=31),
            quality_test_passed=True,
            status='in_storage',
            created_by=self.admin_user
        )
        
        production_order = ProductionOrder.objects.create(
            order_number='ORD-012',
            finished_product=self.test_product,
            planned_quantity=Decimal('30'),  # 60kg 필요 (첫 번째 로트를 모두 소모하고 두 번째 로트에서 10kg)
            planned_start_date=self.current_time,
            planned_end_date=self.current_time + timedelta(hours=8),
            status='planned',
            priority='normal',
            created_by=self.admin_user
        )
        
        self.production_service._allocate_materials('MAT-001', Decimal('60.0'), production_order)
        
        # 첫 번째 로트는 모두 소모
        self.test_lot.refresh_from_db()
        assert self.test_lot.quantity_current == Decimal('0.0')
        assert self.test_lot.status == 'used'
        
        # 두 번째 로트에서 10kg 소모
        second_lot.refresh_from_db()
        assert second_lot.quantity_current == Decimal('20.0')
        assert second_lot.status == 'in_storage'  # 아직 남아있음


@pytest.mark.unit
@pytest.mark.django_db
class TestProductionQueryService:
    """Production Query Service 단위 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.query_service = ProductionQueryService()
        
        # Test Users
        self.admin_user = User.objects.create_user(
            username='admin_query_prod',
            password='test123',
            role='admin'
        )
        self.production_manager = User.objects.create_user(
            username='prod_manager_query',
            password='test123',
            role='production_manager'
        )
        self.operator = User.objects.create_user(
            username='operator_query_prod',
            password='test123',
            role='operator'
        )
        self.viewer = User.objects.create_user(
            username='viewer_query_prod',
            password='test123',
            role='viewer'
        )
        
        # Test Product
        self.test_product = FinishedProduct.objects.create(
            code='PROD-QUERY',
            name='쿼리 테스트 제품',
            description='쿼리용 완제품',
            version='1.0',
            shelf_life_days=30,
            net_weight=Decimal('1.000'),
            packaging_type='박스',
            is_active=True,
            created_by=self.admin_user
        )

    def test_get_production_orders_for_operator(self):
        """운영자 역할의 생산 주문 조회 테스트"""
        # 운영자에게 배정된 주문
        operator_order = ProductionOrder.objects.create(
            order_number='ORD-OP-001',
            finished_product=self.test_product,
            planned_quantity=Decimal('10'),
            planned_start_date=timezone.now(),
            planned_end_date=timezone.now() + timedelta(hours=8),
            status='planned',
            priority='normal',
            assigned_operator=self.operator,
            created_by=self.admin_user
        )
        
        # 다른 운영자에게 배정된 주문
        other_operator = User.objects.create_user(
            username='other_operator_prod',
            password='test123',
            role='operator'
        )
        
        ProductionOrder.objects.create(
            order_number='ORD-OP-002',
            finished_product=self.test_product,
            planned_quantity=Decimal('5'),
            planned_start_date=timezone.now(),
            planned_end_date=timezone.now() + timedelta(hours=8),
            status='planned',
            priority='normal',
            assigned_operator=other_operator,
            created_by=self.admin_user
        )
        
        result = self.query_service.get_production_orders_for_user(user=self.operator)
        
        assert result.count() == 1
        assert result.first() == operator_order

    def test_get_production_orders_for_admin(self):
        """관리자 역할의 생산 주문 조회 테스트 (모든 주문 접근 가능)"""
        ProductionOrder.objects.create(
            order_number='ORD-ADMIN-001',
            finished_product=self.test_product,
            planned_quantity=Decimal('10'),
            planned_start_date=timezone.now(),
            planned_end_date=timezone.now() + timedelta(hours=8),
            status='planned',
            priority='normal',
            created_by=self.admin_user
        )
        
        ProductionOrder.objects.create(
            order_number='ORD-ADMIN-002',
            finished_product=self.test_product,
            planned_quantity=Decimal('5'),
            planned_start_date=timezone.now(),
            planned_end_date=timezone.now() + timedelta(hours=8),
            status='in_progress',
            priority='urgent',
            created_by=self.production_manager
        )
        
        result = self.query_service.get_production_orders_for_user(user=self.admin_user)
        
        assert result.count() == 2

    def test_get_production_orders_for_unauthorized_user(self):
        """권한 없는 사용자의 생산 주문 조회 테스트"""
        ProductionOrder.objects.create(
            order_number='ORD-UNAUTH-001',
            finished_product=self.test_product,
            planned_quantity=Decimal('10'),
            planned_start_date=timezone.now(),
            planned_end_date=timezone.now() + timedelta(hours=8),
            status='planned',
            priority='normal',
            created_by=self.admin_user
        )
        
        result = self.query_service.get_production_orders_for_user(user=self.viewer)
        
        assert result.count() == 0

    def test_get_production_dashboard_data_permission_denied(self):
        """권한 없는 사용자의 대시보드 조회 시도 테스트"""
        with pytest.raises(PermissionDenied, match='대시보드 조회 권한이 없습니다'):
            self.query_service.get_production_dashboard_data(user=self.viewer)

    def test_get_production_dashboard_data_success(self):
        """정상적인 생산 대시보드 데이터 조회 테스트"""
        today = timezone.now().date()
        
        # 오늘 주문 생성
        ProductionOrder.objects.create(
            order_number='ORD-TODAY-001',
            finished_product=self.test_product,
            planned_quantity=Decimal('10'),
            planned_start_date=timezone.now().replace(hour=9),
            planned_end_date=timezone.now().replace(hour=17),
            actual_start_date=timezone.now().replace(hour=9),
            status='in_progress',
            priority='normal',
            created_by=self.admin_user
        )
        
        ProductionOrder.objects.create(
            order_number='ORD-TODAY-002',
            finished_product=self.test_product,
            planned_quantity=Decimal('5'),
            produced_quantity=Decimal('5'),
            planned_start_date=timezone.now().replace(hour=10),
            planned_end_date=timezone.now().replace(hour=18),
            actual_start_date=timezone.now().replace(hour=10),
            actual_end_date=timezone.now().replace(hour=16),
            status='completed',
            priority='urgent',
            created_by=self.admin_user
        )
        
        result = self.query_service.get_production_dashboard_data(user=self.admin_user)
        
        assert 'today_stats' in result
        assert 'week_stats' in result
        assert 'urgent_orders' in result
        assert 'overdue_orders' in result
        
        # 오늘 통계 확인
        today_stats = result['today_stats']
        assert today_stats['total_orders'] == 2
        assert today_stats['in_progress'] == 1
        assert today_stats['completed'] == 1


@pytest.mark.unit
@pytest.mark.django_db
class TestMaterialTraceabilityService:
    """Material Traceability Service 단위 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.traceability_service = MaterialTraceabilityService()
        
        # Test Users
        self.admin_user = User.objects.create_user(
            username='admin_trace',
            password='test123',
            role='admin'
        )
        
        # Test Supplier
        self.test_supplier = Supplier.objects.create(
            name='추적성 테스트 공급업체',
            code='SUP-TRACE',
            contact_person='추적성 담당자',
            email='trace@test.com',
            phone='010-9876-5432',
            address='추적성 테스트 주소',
            status='active',
            created_by=self.admin_user
        )
        
        # Test Raw Material
        self.test_material = RawMaterial.objects.create(
            name='추적성 테스트 원자재',
            code='MAT-TRACE',
            category='ingredient',
            description='추적성용 원자재',
            unit='kg',
            supplier=self.test_supplier,
            is_active=True,
            created_by=self.admin_user
        )
        
        # Test Material Lot
        self.test_lot = MaterialLot.objects.create(
            raw_material=self.test_material,
            supplier=self.test_supplier,
            lot_number='LOT-TRACE-001',
            quantity_received=Decimal('50.0'),
            quantity_current=Decimal('30.0'),
            unit_price=Decimal('1500.00'),
            received_date=timezone.now().date(),
            expiry_date=timezone.now().date() + timedelta(days=30),
            quality_test_passed=True,
            quality_test_date=timezone.now().date(),
            quality_test_notes='품질 검사 통과',
            status='in_use',
            created_by=self.admin_user
        )

    def test_get_material_traceability_success(self):
        """원자재 로트 추적성 정보 조회 테스트"""
        result = self.traceability_service.get_material_traceability(
            material_lot_id=self.test_lot.id
        )
        
        assert 'lot_info' in result
        assert 'supplier_info' in result
        assert 'quality_info' in result
        assert 'usage_history' in result
        
        # 로트 정보 확인
        lot_info = result['lot_info']
        assert lot_info['lot_number'] == 'LOT-TRACE-001'
        assert lot_info['material_code'] == 'MAT-TRACE'
        assert lot_info['current_quantity'] == Decimal('30.0')
        assert lot_info['original_quantity'] == Decimal('50.0')
        
        # 공급업체 정보 확인
        supplier_info = result['supplier_info']
        assert supplier_info['name'] == '추적성 테스트 공급업체'
        assert supplier_info['code'] == 'SUP-TRACE'
        
        # 품질 정보 확인
        quality_info = result['quality_info']
        assert quality_info['test_passed'] is True
        assert quality_info['test_notes'] == '품질 검사 통과'

    def test_get_material_traceability_not_found(self):
        """존재하지 않는 로트의 추적성 조회 테스트"""
        import uuid
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(ValidationError, match='존재하지 않는 원자재 로트입니다'):
            self.traceability_service.get_material_traceability(
                material_lot_id=non_existent_id
            )

    def test_get_forward_traceability_success(self):
        """전방 추적성 조회 테스트"""
        # Test Product
        test_product = FinishedProduct.objects.create(
            code='PROD-TRACE',
            name='추적성 테스트 제품',
            description='추적성용 완제품',
            version='1.0',
            shelf_life_days=30,
            net_weight=Decimal('1.000'),
            packaging_type='박스',
            is_active=True,
            created_by=self.admin_user
        )
        
        # Test Production Order
        production_order = ProductionOrder.objects.create(
            order_number='ORD-TRACE-001',
            finished_product=test_product,
            planned_quantity=Decimal('10'),
            produced_quantity=Decimal('9'),
            planned_start_date=timezone.now() - timedelta(hours=8),
            planned_end_date=timezone.now() - timedelta(hours=1),
            actual_start_date=timezone.now() - timedelta(hours=8),
            actual_end_date=timezone.now() - timedelta(hours=1),
            status='completed',
            priority='normal',
            created_by=self.admin_user
        )
        
        result = self.traceability_service.get_forward_traceability(
            production_order_id=production_order.id
        )
        
        assert 'production_info' in result
        assert 'used_materials' in result
        
        # 생산 정보 확인
        production_info = result['production_info']
        assert production_info['order_number'] == 'ORD-TRACE-001'
        assert production_info['product_name'] == '추적성 테스트 제품'
        assert production_info['produced_quantity'] == Decimal('9')

    def test_get_forward_traceability_not_found(self):
        """존재하지 않는 생산 주문의 전방 추적성 조회 테스트"""
        import uuid
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(ValidationError, match='존재하지 않는 생산 주문입니다'):
            self.traceability_service.get_forward_traceability(
                production_order_id=non_existent_id
            )