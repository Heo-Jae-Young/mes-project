"""Supplier 모델 관련 테스트 헬퍼 함수들"""
from datetime import timedelta
from django.utils import timezone
from core.models.supplier import Supplier
from core.models.raw_material import RawMaterial, MaterialLot
from .user_helpers import create_test_user


def create_test_supplier(name='테스트 공급업체', **kwargs):
    """테스트용 공급업체 생성"""
    user = kwargs.pop('created_by', None)
    if not user:
        user = create_test_user(role='admin')
    
    defaults = {
        'name': name,
        'code': f'SUP{hash(name) % 10000:04d}',  # 이름 기반 고유 코드 생성
        'contact_person': '김담당자',
        'phone': '02-1234-5678',
        'email': f'{name.lower().replace(" ", "")}@supplier.com',
        'address': '서울시 강남구 테스트로 123',
        'certification': 'HACCP 인증, ISO 22000',
        'status': 'active',
        'created_by': user
    }
    defaults.update(kwargs)
    return Supplier.objects.create(**defaults)


def create_food_supplier(**kwargs):
    """식품 공급업체 생성"""
    defaults = {
        'name': '프리미엄 식품',
        'code': 'FOOD001',
        'contact_person': '이식품',
        'certification': 'HACCP 인증, 유기농 인증, ISO 22000'
    }
    defaults.update(kwargs)
    return create_test_supplier(**defaults)


def create_packaging_supplier(**kwargs):
    """포장재 공급업체 생성"""
    defaults = {
        'name': '안전 포장재',
        'code': 'PACK001',
        'contact_person': '박포장',
        'certification': 'FDA 승인, BPA Free, HACCP'
    }
    defaults.update(kwargs)
    return create_test_supplier(**defaults)


def create_unapproved_supplier(**kwargs):
    """승인되지 않은 공급업체 생성"""
    defaults = {
        'name': '신규 공급업체',
        'code': 'NEW001',
        'status': 'inactive',
        'certification': '검토 중'
    }
    defaults.update(kwargs)
    return create_test_supplier(**defaults)


def create_suppliers_batch(count=5, **kwargs):
    """여러 공급업체 일괄 생성"""
    suppliers = []
    for i in range(count):
        supplier_kwargs = kwargs.copy()
        supplier_kwargs.update({
            'name': f'공급업체 {i+1}',
            'code': f'SUP{i+1:03d}',
            'contact_person': f'담당자{i+1}',
            'phone': f'02-1234-{5678+i}'
        })
        suppliers.append(create_test_supplier(**supplier_kwargs))
    return suppliers


def create_supplier_with_rating(rating='A', **kwargs):
    """특정 등급의 공급업체 생성"""
    rating_info = {
        'A+': {'name': '최우수 공급업체', 'certification': 'HACCP, ISO 22000, 유기농'},
        'A': {'name': '우수 공급업체', 'certification': 'HACCP, ISO 22000'},
        'B': {'name': '보통 공급업체', 'certification': 'HACCP'},
        'C': {'name': '개선 필요 공급업체', 'certification': '기본 인증'}
    }
    
    defaults = rating_info.get(rating, rating_info['B'])
    defaults.update({
        'code': f'{rating}001'
    })
    defaults.update(kwargs)
    return create_test_supplier(**defaults)


def create_test_raw_material(**kwargs):
    """테스트용 원자재 생성"""
    user = kwargs.pop('created_by', None)
    if not user:
        user = create_test_user(role='admin')
    
    supplier = kwargs.pop('supplier', None)
    if not supplier:
        supplier = create_test_supplier(created_by=user)
    
    defaults = {
        'name': '테스트 원자재',
        'code': 'RM001',
        'category': 'ingredient',
        'description': '테스트용 원자재입니다',
        'unit': 'kg',
        'shelf_life_days': 30,
        'supplier': supplier,
        'created_by': user
    }
    defaults.update(kwargs)
    return RawMaterial.objects.create(**defaults)


def create_test_material_lot(**kwargs):
    """테스트용 원자재 로트 생성"""
    user = kwargs.pop('created_by', None)
    if not user:
        user = create_test_user(role='admin')
    
    raw_material = kwargs.pop('raw_material', None)
    if not raw_material:
        raw_material = create_test_raw_material(created_by=user)
    
    supplier = kwargs.pop('supplier', None)
    if not supplier:
        supplier = raw_material.supplier
    
    now = timezone.now()
    defaults = {
        'lot_number': f'LOT{hash(str(now)) % 10000:04d}',
        'raw_material': raw_material,
        'supplier': supplier,
        'received_date': now,
        'expiry_date': (now + timedelta(days=30)).date(),
        'quantity_received': 100.0,
        'quantity_current': 100.0,
        'unit_price': 10.50,
        'status': 'received',
        'quality_test_passed': True,
        'created_by': user
    }
    defaults.update(kwargs)
    return MaterialLot.objects.create(**defaults)