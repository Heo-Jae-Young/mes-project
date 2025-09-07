"""공통 테스트 픽스처"""

import pytest
from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone
from core.models import User, Supplier, RawMaterial, MaterialLot, CCP, FinishedProduct


@pytest.fixture
def admin_user():
    """관리자 사용자"""
    return User.objects.create_user(
        username="admin",
        password="admin123",
        email="admin@test.com",
        role="admin"
    )


@pytest.fixture  
def operator_user():
    """운영자 사용자"""
    return User.objects.create_user(
        username="operator",
        password="operator123", 
        email="operator@test.com",
        role="operator"
    )


@pytest.fixture
def quality_manager_user():
    """품질관리자 사용자"""
    return User.objects.create_user(
        username="quality_manager",
        password="quality123",
        email="quality@test.com", 
        role="quality_manager"
    )


@pytest.fixture
def sample_supplier(admin_user):
    """기본 공급업체"""
    return Supplier.objects.create(
        name="테스트 공급업체",
        code="SUP001", 
        contact_person="김담당",
        phone="02-1234-5678",
        email="supplier@test.com",
        address="서울시 강남구 테스트로 123",
        created_by=admin_user
    )


@pytest.fixture
def flour_material(admin_user, sample_supplier):
    """밀가루 원자재"""
    return RawMaterial.objects.create(
        name="밀가루",
        code="RM001",
        category="ingredient", 
        description="1등급 밀가루",
        unit="kg",
        storage_temp_min=Decimal("0.0"),
        storage_temp_max=Decimal("25.0"),
        shelf_life_days=365,
        allergens="글루텐",
        supplier=sample_supplier,
        created_by=admin_user
    )


@pytest.fixture
def sugar_material(admin_user, sample_supplier):
    """설탕 원자재"""
    return RawMaterial.objects.create(
        name="설탕",
        code="RM002", 
        category="ingredient",
        description="백설탕",
        unit="kg",
        storage_temp_min=Decimal("10.0"),
        storage_temp_max=Decimal("30.0"), 
        shelf_life_days=730,
        supplier=sample_supplier,
        created_by=admin_user
    )


@pytest.fixture
def flour_lot(admin_user, sample_supplier, flour_material):
    """밀가루 로트"""
    return MaterialLot.objects.create(
        lot_number="FLOUR2025001",
        raw_material=flour_material,
        supplier=sample_supplier,
        received_date=timezone.now(),
        expiry_date=date.today() + timedelta(days=365),
        quantity_received=Decimal("100.000"),
        quantity_current=Decimal("100.000"), 
        unit_price=Decimal("1500.00"),
        status="received",
        storage_location="A-01-01",
        temperature_at_receipt=Decimal("20.00"),
        created_by=admin_user
    )


@pytest.fixture
def temperature_ccp(admin_user):
    """온도 관리점"""
    return CCP.objects.create(
        name="냉장고 온도 관리점",
        code="CCP-TEMP-001",
        ccp_type="temperature",
        description="냉장고 온도 모니터링",
        process_step="냉장 보관",
        critical_limit_min=Decimal("0.0"),
        critical_limit_max=Decimal("4.0"),
        monitoring_frequency="매 30분",
        corrective_action="온도 조절 및 설비 점검",
        responsible_person="품질관리팀",
        monitoring_method="디지털 온도계",
        verification_method="일일 검증",
        record_keeping="CCP 로그 시스템",
        created_by=admin_user
    )


@pytest.fixture
def sample_product(admin_user):
    """기본 완제품"""
    return FinishedProduct.objects.create(
        name="화이트 브레드",
        code="FP001",
        description="부드러운 식빵",
        version="1.0",
        net_weight=Decimal("500.0"),
        packaging_type="플라스틱 포장",
        shelf_life_days=7,
        storage_temp_min=Decimal("15.0"),
        storage_temp_max=Decimal("25.0"),
        allergen_info="글루텐, 달걀, 우유",
        created_by=admin_user
    )