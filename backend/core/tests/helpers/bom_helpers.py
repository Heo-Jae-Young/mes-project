"""BOM 관련 테스트 헬퍼 함수들"""
import random
from decimal import Decimal
from core.models import BOM
from .user_helpers import create_test_user
from .production_helpers import create_test_finished_product
from .supplier_helpers import create_test_raw_material


def create_test_bom(**kwargs):
    """테스트용 BOM 생성"""
    user = kwargs.pop('created_by', None)
    if not user:
        user = create_test_user(role='admin')
    
    finished_product = kwargs.pop('finished_product', None)
    if not finished_product:
        finished_product = create_test_finished_product(created_by=user)
    
    raw_material = kwargs.pop('raw_material', None)
    if not raw_material:
        raw_material = create_test_raw_material()
    
    defaults = {
        'finished_product': finished_product,
        'raw_material': raw_material,
        'quantity_per_unit': Decimal('5.000'),
        'unit': 'kg',
        'is_active': True,
        'notes': 'Test BOM item',
        'created_by': user
    }
    defaults.update(kwargs)
    return BOM.objects.create(**defaults)


def create_bom_batch(count=3, **kwargs):
    """여러 BOM 아이템 일괄 생성"""
    bom_items = []
    user = kwargs.get('created_by') or create_test_user(role='admin')
    finished_product = kwargs.get('finished_product') or create_test_finished_product(created_by=user)
    
    for i in range(count):
        # 각 BOM 아이템마다 다른 원자재 생성
        raw_material = create_test_raw_material(
            name=f'Test Material {i+1}',
            code=f'TM{i+1:03d}'
        )
        bom_kwargs = kwargs.copy()
        bom_kwargs.update({
            'finished_product': finished_product,
            'raw_material': raw_material,
            'quantity_per_unit': Decimal(f'{(i+1)*2}.000'),
            'created_by': user
        })
        bom_items.append(create_test_bom(**bom_kwargs))
    return bom_items


def create_inactive_bom(**kwargs):
    """비활성 BOM 생성"""
    defaults = {
        'is_active': False,
        'notes': 'Inactive test BOM item'
    }
    defaults.update(kwargs)
    return create_test_bom(**defaults)


def create_bom_with_specific_quantity(quantity_per_unit, **kwargs):
    """특정 소요량을 가진 BOM 생성"""
    defaults = {
        'quantity_per_unit': Decimal(str(quantity_per_unit)),
    }
    defaults.update(kwargs)
    return create_test_bom(**defaults)


def create_random_bom(**kwargs):
    """랜덤 데이터가 포함된 BOM 생성 (테스트 간 중복 방지)"""
    random_suffix = random.randint(1000, 9999)
    units = ['kg', 'L', 'g', 'ml', 'pcs']
    
    defaults = {
        'quantity_per_unit': Decimal(f'{random.uniform(0.1, 50.0):.3f}'),
        'unit': random.choice(units),
        'notes': f'Random test BOM {random_suffix}',
    }
    defaults.update(kwargs)
    return create_test_bom(**defaults)


def create_bom_for_product(finished_product, raw_materials, **kwargs):
    """특정 제품에 대해 여러 원자재로 BOM 생성"""
    bom_items = []
    user = kwargs.get('created_by') or create_test_user(role='admin')
    
    for raw_material in raw_materials:
        try:
            bom = create_test_bom(
                finished_product=finished_product,
                raw_material=raw_material,
                created_by=user,
                **kwargs
            )
            bom_items.append(bom)
        except Exception:
            # unique_together 제약 등으로 실패 시 스킵
            continue
    
    return bom_items


def assert_bom_valid(bom):
    """BOM 유효성 검증 헬퍼"""
    assert bom.quantity_per_unit > 0, "소요량은 0보다 커야 합니다"
    assert bom.unit, "단위가 설정되어야 합니다"
    assert bom.finished_product, "완제품이 설정되어야 합니다"
    assert bom.raw_material, "원자재가 설정되어야 합니다"
    assert bom.created_by, "생성자가 설정되어야 합니다"


def calculate_total_cost(bom_items, production_quantity=1):
    """BOM 아이템들의 총 원가 계산 헬퍼"""
    total_cost = Decimal('0')
    for bom in bom_items:
        material_cost = getattr(bom.raw_material, 'unit_price', Decimal('0'))
        required_quantity = bom.calculate_total_required_quantity(production_quantity)
        total_cost += material_cost * required_quantity
    return total_cost