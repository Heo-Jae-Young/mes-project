import pytest
import uuid
from rest_framework.test import APIRequestFactory
from datetime import date, timedelta
from core.models import Supplier
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


@pytest.mark.integration
@pytest.mark.django_db
class TestRawMaterialSerializersIntegration:
    def test_create_material_and_lot_workflow(self, test_user):
        supplier = create_unique_supplier(test_user)
        factory = APIRequestFactory()
        request = factory.post("/raw-materials/")
        request.user = test_user

        material_data = {
            "name": "Integration Material",
            "code": f"INT-MAT-{uuid.uuid4().hex[:6]}",
            "category": "ingredient",
            "unit": "kg",
            "supplier_id": supplier.id,
        }
        material_serializer = RawMaterialCreateSerializer(
            data=material_data, context={"request": request}
        )
        assert material_serializer.is_valid(), material_serializer.errors
        material = material_serializer.save()

        lot_data = get_base_lot_data(material.id, supplier.id)
        lot_serializer = MaterialLotCreateSerializer(
            data=lot_data, context={"request": request}
        )
        assert lot_serializer.is_valid(), lot_serializer.errors
        lot = lot_serializer.save()

        material_read_serializer = RawMaterialSerializer(material)
        assert material_read_serializer.data["created_by"]["id"] == test_user.id

        lot_read_serializer = MaterialLotSerializer(lot)
        assert lot_read_serializer.data["raw_material"]["id"] == str(material.id)
