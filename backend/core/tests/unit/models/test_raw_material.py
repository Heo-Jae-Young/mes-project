"""원자재 모델 단위 테스트"""

import pytest
from decimal import Decimal
from django.utils import timezone
from core.models import RawMaterial, MaterialLot
from ...fixtures.base_fixtures import admin_user, sample_supplier, flour_material, sugar_material, flour_lot


@pytest.mark.unit
class TestRawMaterialModel:
    """원자재 카탈로그 모델 테스트"""

    def test_raw_material_creation_with_fixtures(self, admin_user, sample_supplier):
        """픽스처를 사용한 원자재 생성 테스트"""
        material = RawMaterial.objects.create(
            name="소금", code="RM003", category="ingredient", unit="kg",
            supplier=sample_supplier, created_by=admin_user
        )
        
        assert material.name == "소금"
        assert material.code == "RM003"
        assert str(material) == "소금 (RM003)"
        assert material.is_active is True

    def test_raw_material_str_representation(self, flour_material):
        """픽스처 원자재 __str__ 테스트"""
        assert str(flour_material) == "밀가루 (RM001)"

    def test_raw_material_unique_code_constraint(self, admin_user, sample_supplier):
        """원자재 코드 중복 방지 테스트"""
        # 첫 번째 원자재
        RawMaterial.objects.create(
            name="재료1", code="DUPLICATE", category="ingredient", unit="kg",
            supplier=sample_supplier, created_by=admin_user
        )
        
        # 중복 코드로 생성 시도
        with pytest.raises(Exception):
            RawMaterial.objects.create(
                name="재료2", code="DUPLICATE", category="ingredient", unit="kg",
                supplier=sample_supplier, created_by=admin_user
            )


@pytest.mark.unit  
class TestMaterialLotModel:
    """원자재 로트 모델 테스트"""

    def test_material_lot_creation_with_fixtures(self, admin_user, sample_supplier, sugar_material):
        """픽스처를 사용한 로트 생성 테스트"""
        lot = MaterialLot.objects.create(
            lot_number="SUGAR2025001", raw_material=sugar_material,
            supplier=sample_supplier, received_date=timezone.now(),
            quantity_received=Decimal("200.0"), quantity_current=Decimal("200.0"),
            unit_price=Decimal("800.00"), created_by=admin_user
        )
        
        assert lot.lot_number == "SUGAR2025001"
        assert lot.quantity_current == Decimal("200.0")
        assert str(lot) == "설탕 - SUGAR2025001"
        assert lot.status == "received"

    def test_material_lot_str_representation(self, flour_lot):
        """픽스처 로트 __str__ 테스트"""
        assert str(flour_lot) == "밀가루 - FLOUR2025001"

    def test_lot_quantity_tracking(self, flour_lot):
        """로트 수량 추적 테스트"""
        original_received = flour_lot.quantity_received
        
        # 수량 사용
        flour_lot.quantity_current = Decimal("70.0")
        flour_lot.status = "in_use"
        flour_lot.save()
        
        flour_lot.refresh_from_db()
        assert flour_lot.quantity_current == Decimal("70.0")
        assert flour_lot.quantity_received == original_received  # 원래 입고량 유지
        assert flour_lot.status == "in_use"

    def test_lot_unique_lot_number(self, admin_user, sample_supplier, flour_material):
        """로트 번호 중복 방지 테스트"""
        # 첫 번째 로트
        MaterialLot.objects.create(
            lot_number="DUPLICATE_LOT", raw_material=flour_material,
            supplier=sample_supplier, received_date=timezone.now(),
            quantity_received=Decimal("50.0"), quantity_current=Decimal("50.0"),
            unit_price=Decimal("1200.00"), created_by=admin_user
        )
        
        # 중복 로트 번호로 생성 시도
        with pytest.raises(Exception):
            MaterialLot.objects.create(
                lot_number="DUPLICATE_LOT", raw_material=flour_material,
                supplier=sample_supplier, received_date=timezone.now(),
                quantity_received=Decimal("30.0"), quantity_current=Decimal("30.0"),
                unit_price=Decimal("1300.00"), created_by=admin_user
            )