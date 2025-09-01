"""Supplier 모델 관련 테스트 헬퍼 함수들"""
from core.models.supplier import Supplier


def create_test_supplier(name='테스트 공급업체', **kwargs):
    """테스트용 공급업체 생성"""
    defaults = {
        'name': name,
        'code': f'SUP{hash(name) % 10000:04d}',  # 이름 기반 고유 코드 생성
        'contact_person': '김담당자',
        'phone': '02-1234-5678',
        'email': f'{name.lower().replace(" ", "")}@supplier.com',
        'address': '서울시 강남구 테스트로 123',
        'business_registration_number': '123-45-67890',
        'is_approved': True,
        'quality_rating': 'A',
        'certification_info': 'HACCP 인증, ISO 22000'
    }
    defaults.update(kwargs)
    return Supplier.objects.create(**defaults)


def create_food_supplier(**kwargs):
    """식품 공급업체 생성"""
    defaults = {
        'name': '프리미엄 식품',
        'code': 'FOOD001',
        'contact_person': '이식품',
        'certification_info': 'HACCP 인증, 유기농 인증, ISO 22000',
        'quality_rating': 'A+'
    }
    defaults.update(kwargs)
    return create_test_supplier(**defaults)


def create_packaging_supplier(**kwargs):
    """포장재 공급업체 생성"""
    defaults = {
        'name': '안전 포장재',
        'code': 'PACK001',
        'contact_person': '박포장',
        'certification_info': 'FDA 승인, BPA Free',
        'quality_rating': 'A'
    }
    defaults.update(kwargs)
    return create_test_supplier(**defaults)


def create_unapproved_supplier(**kwargs):
    """승인되지 않은 공급업체 생성"""
    defaults = {
        'name': '신규 공급업체',
        'code': 'NEW001',
        'is_approved': False,
        'quality_rating': 'N/A',
        'certification_info': '검토 중'
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
        'A+': {'name': '최우수 공급업체', 'certification_info': 'HACCP, ISO 22000, 유기농'},
        'A': {'name': '우수 공급업체', 'certification_info': 'HACCP, ISO 22000'},
        'B': {'name': '보통 공급업체', 'certification_info': 'HACCP'},
        'C': {'name': '개선 필요 공급업체', 'certification_info': '기본 인증'}
    }
    
    defaults = rating_info.get(rating, rating_info['B'])
    defaults.update({
        'quality_rating': rating,
        'code': f'{rating}001'
    })
    defaults.update(kwargs)
    return create_test_supplier(**defaults)