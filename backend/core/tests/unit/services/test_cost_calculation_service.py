import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth import get_user_model

from core.services.cost_calculation_service import CostCalculationService
from core.models import (
    FinishedProduct, BOM, RawMaterial, MaterialLot, Supplier
)

User = get_user_model()


@pytest.mark.unit
@pytest.mark.django_db
class TestCostCalculationService:
    """Cost Calculation Service 단위 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.cost_service = CostCalculationService()
        self.current_time = timezone.now()
        
        # Test Users
        self.admin_user = User.objects.create_user(
            username='admin_cost',
            password='test123',
            role='admin'
        )
        
        # Test Supplier
        self.test_supplier = Supplier.objects.create(
            name='원가계산 테스트 공급업체',
            code='SUP-COST',
            contact_person='원가 담당자',
            email='cost@test.com',
            phone='010-1234-5678',
            address='원가계산 테스트 주소',
            status='active',
            created_by=self.admin_user
        )
        
        # Test Raw Materials
        self.material_flour = RawMaterial.objects.create(
            name='밀가루',
            code='MAT-FLOUR',
            category='ingredient',
            description='제빵용 밀가루',
            unit='kg',
            supplier=self.test_supplier,
            is_active=True,
            created_by=self.admin_user
        )
        
        self.material_sugar = RawMaterial.objects.create(
            name='설탕',
            code='MAT-SUGAR',
            category='ingredient',
            description='백설탕',
            unit='kg',
            supplier=self.test_supplier,
            is_active=True,
            created_by=self.admin_user
        )
        
        # Test Material Lots
        self.flour_lot = MaterialLot.objects.create(
            raw_material=self.material_flour,
            supplier=self.test_supplier,
            lot_number='FLOUR-001',
            quantity_received=Decimal('100.0'),
            quantity_current=Decimal('80.0'),
            unit_price=Decimal('1100.00'),
            received_date=self.current_time.date() - timedelta(days=5),
            expiry_date=self.current_time.date() + timedelta(days=30),
            quality_test_passed=True,
            status='in_storage',
            created_by=self.admin_user
        )
        
        self.sugar_lot = MaterialLot.objects.create(
            raw_material=self.material_sugar,
            supplier=self.test_supplier,
            lot_number='SUGAR-001',
            quantity_received=Decimal('50.0'),
            quantity_current=Decimal('30.0'),
            unit_price=Decimal('800.00'),
            received_date=self.current_time.date() - timedelta(days=10),
            expiry_date=self.current_time.date() + timedelta(days=40),
            quality_test_passed=True,
            status='in_storage',
            created_by=self.admin_user
        )
        
        # Test Product
        self.test_product = FinishedProduct.objects.create(
            code='PROD-BREAD',
            name='식빵',
            description='테스트용 식빵',
            version='1.0',
            shelf_life_days=3,
            net_weight=Decimal('0.500'),
            packaging_type='비닐포장',
            is_active=True,
            created_by=self.admin_user
        )
        
        # Test BOM (식빵 1개 = 밀가루 0.4kg + 설탕 0.1kg)
        self.bom_flour = BOM.objects.create(
            finished_product=self.test_product,
            raw_material=self.material_flour,
            quantity_per_unit=Decimal('0.4'),
            is_active=True,
            created_by=self.admin_user
        )
        
        self.bom_sugar = BOM.objects.create(
            finished_product=self.test_product,
            raw_material=self.material_sugar,
            quantity_per_unit=Decimal('0.1'),
            is_active=True,
            created_by=self.admin_user
        )

    def test_calculate_product_cost_success(self):
        """정상적인 제품 원가 계산 테스트"""
        result = self.cost_service.calculate_product_cost(self.test_product.id)
        
        assert result is not None
        assert 'total_cost' in result
        assert 'unit_cost' in result
        assert 'material_costs' in result
        assert 'calculation_method' in result
        assert 'bom_missing' in result
        
        # 예상 원가: 밀가루(0.4kg * 1100원) + 설탕(0.1kg * 800원) = 440 + 80 = 520원
        assert result['total_cost'] == Decimal('520.00')
        assert result['unit_cost'] == Decimal('520.00')  # 1개 생산 기준
        assert result['bom_missing'] is False
        assert result['calculation_method'] == 'current_lot'
        
        # 원가 구성 확인
        material_costs = result['material_costs']
        assert len(material_costs) == 2
        
        # 밀가루 비용 확인
        flour_cost = next(item for item in material_costs if item['material']['code'] == 'MAT-FLOUR')
        assert flour_cost['unit_price'] == Decimal('1100.00')
        assert flour_cost['total_cost'] == Decimal('440.00')
        assert flour_cost['required_quantity'] == Decimal('0.4')
        
        # 설탕 비용 확인
        sugar_cost = next(item for item in material_costs if item['material']['code'] == 'MAT-SUGAR')
        assert sugar_cost['unit_price'] == Decimal('800.00')
        assert sugar_cost['total_cost'] == Decimal('80.00')
        assert sugar_cost['required_quantity'] == Decimal('0.1')

    def test_calculate_product_cost_multiple_quantity(self):
        """여러 개 생산 시 원가 계산 테스트"""
        result = self.cost_service.calculate_product_cost(self.test_product.id, production_quantity=10)
        
        assert result['production_quantity'] == 10
        assert result['total_cost'] == Decimal('5200.00')  # 520 * 10
        assert result['unit_cost'] == Decimal('520.00')  # 개당 원가는 동일
        
        # 원자재 총 소요량 확인
        material_costs = result['material_costs']
        flour_cost = next(item for item in material_costs if item['material']['code'] == 'MAT-FLOUR')
        sugar_cost = next(item for item in material_costs if item['material']['code'] == 'MAT-SUGAR')
        
        assert flour_cost['required_quantity'] == Decimal('4.0')  # 0.4 * 10
        assert flour_cost['total_cost'] == Decimal('4400.00')  # 440 * 10
        assert sugar_cost['required_quantity'] == Decimal('1.0')  # 0.1 * 10
        assert sugar_cost['total_cost'] == Decimal('800.00')  # 80 * 10

    def test_calculate_product_cost_no_bom(self):
        """BOM이 설정되지 않은 제품의 원가 계산 테스트"""
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
        
        result = self.cost_service.calculate_product_cost(product_without_bom.id)
        
        assert result['bom_missing'] is True
        assert result['total_cost'] == Decimal('0.00')
        assert result['unit_cost'] == Decimal('0.00')
        assert len(result['material_costs']) == 0
        assert 'BOM(자재명세서)가 설정되지 않았습니다.' in result['warnings']

    def test_calculate_product_cost_no_material_lots(self):
        """원자재 로트가 없는 경우 테스트"""
        # 모든 로트 삭제
        MaterialLot.objects.all().delete()
        
        result = self.cost_service.calculate_product_cost(self.test_product.id)
        
        assert result['calculation_method'] == 'no_data'
        assert result['total_cost'] == Decimal('0.00')
        assert len(result['warnings']) > 0

    def test_calculate_product_cost_insufficient_stock(self):
        """재고 부족 시 원가 계산 테스트"""
        # 재고량을 매우 적게 설정
        self.flour_lot.quantity_current = Decimal('0.1')  # 0.4kg 필요하지만 0.1kg만 있음
        self.flour_lot.save()
        
        result = self.cost_service.calculate_product_cost(self.test_product.id)
        
        # 재고 부족해도 계산은 진행됨 (FIFO 평균가 사용)
        assert result['total_cost'] > Decimal('0.00')
        
        # 재고 부족 상황이어도 계산은 진행됨
        flour_cost = next(item for item in result['material_costs'] if item['material']['code'] == 'MAT-FLOUR')
        # 실제 재고량보다 많이 필요한 상황
        assert flour_cost['lot_info']['total_available_quantity'] < flour_cost['required_quantity']

    def test_calculate_product_cost_quality_failed_lots_excluded(self):
        """품질검사 실패 로트 제외 테스트"""
        # 품질검사 실패 로트 생성
        failed_lot = MaterialLot.objects.create(
            raw_material=self.material_flour,
            supplier=self.test_supplier,
            lot_number='FLOUR-FAILED-001',
            quantity_received=Decimal('50.0'),
            quantity_current=Decimal('50.0'),
            unit_price=Decimal('500.00'),  # 매우 낮은 가격
            received_date=self.current_time.date() - timedelta(days=3),
            expiry_date=self.current_time.date() + timedelta(days=30),
            quality_test_passed=False,  # 품질검사 실패
            status='in_storage',
            created_by=self.admin_user
        )
        
        result = self.cost_service.calculate_product_cost(self.test_product.id)
        
        # 품질검사 실패 로트는 제외되어야 함
        flour_cost = next(item for item in result['material_costs'] if item['material']['code'] == 'MAT-FLOUR')
        assert flour_cost['unit_price'] == Decimal('1100.00')  # 품질검사 통과한 로트 가격

    def test_calculate_product_cost_recent_average_fallback(self):
        """현재 재고 부족 시 최근 평균가 사용 테스트"""
        # 추가 과거 로트 생성
        old_flour_lot = MaterialLot.objects.create(
            raw_material=self.material_flour,
            supplier=self.test_supplier,
            lot_number='FLOUR-OLD-001',
            quantity_received=Decimal('100.0'),
            quantity_current=Decimal('0.0'),  # 재고 없음
            unit_price=Decimal('1000.00'),
            received_date=self.current_time.date() - timedelta(days=20),
            expiry_date=self.current_time.date() + timedelta(days=10),
            quality_test_passed=True,
            status='used',
            created_by=self.admin_user
        )
        
        # 현재 재고 소진
        self.flour_lot.quantity_current = Decimal('0.0')
        self.flour_lot.status = 'used'
        self.flour_lot.save()
        
        result = self.cost_service.calculate_product_cost(self.test_product.id)
        
        # recent_average 또는 historical_average 사용됨
        assert result['calculation_method'] in ['recent_average', 'historical_average']

    def test_calculate_product_cost_invalid_product_id(self):
        """존재하지 않는 제품 ID로 원가 계산 시도 테스트"""
        import uuid
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(ValueError, match='Product with id .* not found'):
            self.cost_service.calculate_product_cost(non_existent_id)

    def test_get_products_cost_summary(self):
        """제품 원가 요약 조회 테스트"""
        result = self.cost_service.get_products_cost_summary()
        
        assert isinstance(result, list)
        assert len(result) >= 1  # 최소 1개 제품 있음
        
        # 테스트 제품 확인
        bread_cost = next((item for item in result if item['product_code'] == 'PROD-BREAD'), None)
        assert bread_cost is not None
        assert bread_cost['unit_cost'] == Decimal('520.00')
        assert bread_cost['bom_missing'] is False  # BOM이 있음
        assert bread_cost['calculation_method'] == 'current_lot'

    def test_calculate_fifo_average_price_sufficient_stock(self):
        """FIFO 평균가 계산 - 충분한 재고 테스트"""
        # 여러 로트 생성
        lots_queryset = MaterialLot.objects.filter(
            raw_material=self.material_flour,
            quality_test_passed=True,
            quantity_current__gt=0
        ).order_by('received_date')
        
        # 0.4kg 필요 (현재 재고로 충분)
        result_price = self.cost_service._calculate_fifo_average_price(
            lots_queryset, Decimal('0.4')
        )
        
        assert result_price == Decimal('1100.00')  # 가장 오래된 로트 가격

    def test_calculate_fifo_average_price_mixed_lots(self):
        """FIFO 평균가 계산 - 여러 로트 혼합 사용 테스트"""
        # 추가 로트 생성 (더 비싼 가격)
        expensive_lot = MaterialLot.objects.create(
            raw_material=self.material_flour,
            supplier=self.test_supplier,
            lot_number='FLOUR-EXPENSIVE-001',
            quantity_received=Decimal('50.0'),
            quantity_current=Decimal('50.0'),
            unit_price=Decimal('1300.00'),
            received_date=self.current_time.date() - timedelta(days=1),  # 더 최근
            expiry_date=self.current_time.date() + timedelta(days=35),
            quality_test_passed=True,
            status='in_storage',
            created_by=self.admin_user
        )
        
        # 현재 로트의 재고를 10kg으로 제한
        self.flour_lot.quantity_current = Decimal('10.0')
        self.flour_lot.save()
        
        lots_queryset = MaterialLot.objects.filter(
            raw_material=self.material_flour,
            quality_test_passed=True,
            quantity_current__gt=0
        ).order_by('received_date')
        
        # 20kg 필요 (첫 번째 로트 10kg + 두 번째 로트 10kg)
        result_price = self.cost_service._calculate_fifo_average_price(
            lots_queryset, Decimal('20.0')
        )
        
        # 가중 평균: (10 * 1100 + 10 * 1300) / 20 = 24000 / 20 = 1200
        assert result_price == Decimal('1200.00')

    def test_calculate_product_cost_with_inactive_bom(self):
        """비활성 BOM 제외 테스트"""
        # BOM을 비활성화
        self.bom_sugar.is_active = False
        self.bom_sugar.save()
        
        result = self.cost_service.calculate_product_cost(self.test_product.id)
        
        # 설탕 BOM이 제외되어 밀가루 비용만 계산됨
        assert result['total_cost'] == Decimal('440.00')  # 밀가루만
        assert len(result['material_costs']) == 1
        
        flour_cost = result['material_costs'][0]
        assert flour_cost['material']['code'] == 'MAT-FLOUR'