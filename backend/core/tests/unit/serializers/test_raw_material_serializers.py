"""원자재 시리얼라이저 단위 테스트"""

import pytest
import uuid
from datetime import date, timedelta
from decimal import Decimal
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from core.models import RawMaterial, MaterialLot, Supplier
from core.serializers.raw_material_serializers import (
    RawMaterialSerializer,
    RawMaterialCreateSerializer,
    MaterialLotSerializer,
    MaterialLotCreateSerializer,
)


# Helper to create unique objects for tests
def create_unique_supplier(user):
    unique_code = f"SUP-{uuid.uuid4().hex[:8]}"
    return Supplier.objects.create(
        name="Test Supplier",
        code=unique_code,
        created_by=user,
        address="123 Test St",
        phone="123-456-7890",
        email=f"{unique_code}@test.com",
    )


def create_unique_raw_material(supplier, user):
    unique_code = f"MAT-{uuid.uuid4().hex[:8]}"
    return RawMaterial.objects.create(
        name="Test Raw Material",
        code=unique_code,
        category="ingredient",
        unit="kg",
        supplier=supplier,
        created_by=user,
    )


def get_base_lot_data(material_id, supplier_id):
    today = date.today()
    return {
        "lot_number": f"LOT-{uuid.uuid4().hex[:8]}",
        "raw_material_id": str(material_id),
        "supplier_id": str(supplier_id),
        "received_date": today.isoformat(),
        "expiry_date": (today + timedelta(days=30)).isoformat(),
        "quantity_received": "100.0",
        "unit_price": "10.50",
    }


@pytest.mark.unit
@pytest.mark.django_db
class TestRawMaterialSerializer:
    def test_raw_material_serialization(self, test_user):
        supplier = create_unique_supplier(test_user)
        raw_material = create_unique_raw_material(supplier, test_user)
        serializer = RawMaterialSerializer(raw_material)
        data = serializer.data
        assert data["id"] == str(raw_material.id)
        assert data["supplier"]["id"] == str(supplier.id)
        assert data["created_by"]["id"] == test_user.id

    def test_inventory_info_calculation(self, test_user):
        supplier = create_unique_supplier(test_user)
        raw_material = create_unique_raw_material(supplier, test_user)
        MaterialLot.objects.create(
            lot_number="LOT001",
            raw_material=raw_material,
            supplier=supplier,
            received_date=timezone.now(),
            expiry_date=date.today() + timedelta(days=5),
            quantity_received=Decimal("100.0"),
            quantity_current=Decimal("80.0"),
            unit_price=Decimal("10.0"),
            status="in_storage",
            created_by=test_user,
        )
        serializer = RawMaterialSerializer(raw_material)
        inventory_info = serializer.data["inventory_info"]
        assert inventory_info["totalQuantity"] == 80.0
        assert inventory_info["activeLots"] == 1
        assert inventory_info["nearExpiry"] == 1


@pytest.mark.unit
@pytest.mark.django_db
class TestRawMaterialCreateSerializer:
    def test_valid_raw_material_creation(self, test_user):
        supplier = create_unique_supplier(test_user)
        factory = APIRequestFactory()
        request = factory.post("/raw-materials/")
        request.user = test_user
        data = {
            "name": "New Material",
            "code": f"NEW-{uuid.uuid4().hex[:8]}",
            "category": "packaging",
            "unit": "ea",
            "supplier_id": supplier.id,
        }
        serializer = RawMaterialCreateSerializer(
            data=data, context={"request": request}
        )
        assert serializer.is_valid(), serializer.errors
        material = serializer.save()
        assert material.name == "New Material"
        assert material.created_by == test_user

    def test_duplicate_code_validation(self, test_user):
        supplier = create_unique_supplier(test_user)
        raw_material = create_unique_raw_material(supplier, test_user)
        data = {
            "name": "Duplicate Material",
            "code": raw_material.code,
            "category": "ingredient",
            "unit": "kg",
            "supplier_id": supplier.id,
        }
        serializer = RawMaterialCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "code" in serializer.errors
        assert "unique" in [e.code for e in serializer.errors["code"]]


@pytest.mark.unit
@pytest.mark.django_db
class TestMaterialLotSerializer:
    def test_material_lot_serialization(self, test_user):
        supplier = create_unique_supplier(test_user)
        raw_material = create_unique_raw_material(supplier, test_user)
        lot = MaterialLot.objects.create(
            lot_number="LOT-SERIALIZER-TEST",
            raw_material=raw_material,
            supplier=supplier,
            received_date=timezone.now(),
            expiry_date=date.today() + timedelta(days=15),
            quantity_received=Decimal("100.0"),
            quantity_current=Decimal("100.0"),
            unit_price=Decimal("10.0"),
            created_by=test_user,
        )
        serializer = MaterialLotSerializer(lot)
        data = serializer.data
        assert data["id"] == str(lot.id)
        assert data["created_by"]["id"] == test_user.id


@pytest.mark.unit
@pytest.mark.django_db
class TestMaterialLotCreateSerializer:
    def test_valid_material_lot_creation(self, test_user):
        supplier = create_unique_supplier(test_user)
        raw_material = create_unique_raw_material(supplier, test_user)
        factory = APIRequestFactory()
        request = factory.post("/material-lots/")
        request.user = test_user
        data = get_base_lot_data(raw_material.id, supplier.id)
        serializer = MaterialLotCreateSerializer(
            data=data, context={"request": request}
        )
        assert serializer.is_valid(), serializer.errors
        lot = serializer.save()
        assert lot.lot_number == data["lot_number"]
        assert lot.created_by == test_user

    def test_quantity_received_validation(self, test_user):
        supplier = create_unique_supplier(test_user)
        raw_material = create_unique_raw_material(supplier, test_user)
        data = get_base_lot_data(raw_material.id, supplier.id)
        data["quantity_received"] = "0"
        serializer = MaterialLotCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "quantity_received" in serializer.errors
        assert "invalid" in [e.code for e in serializer.errors["quantity_received"]]
