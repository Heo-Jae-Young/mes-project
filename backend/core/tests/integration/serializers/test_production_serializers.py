import pytest
from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from core.serializers.production_serializers import (
    ProductionOrderSerializer,
    ProductionOrderCreateSerializer,
)


# 테스트를 위한 기본 데이터 생성 함수
def get_base_production_data(product_id):
    start_time = timezone.now() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=8)
    return {
        "order_number": "PO-TEST-001",
        "finished_product_id": str(product_id),
        "planned_quantity": 100,
        "planned_start_date": start_time.isoformat(),
        "planned_end_date": end_time.isoformat(),
        "status": "planned",
        "priority": "normal",
    }


@pytest.mark.integration
@pytest.mark.django_db
class TestProductionOrderSerializersIntegration:
    """생산오더 시리얼라이저 통합 테스트"""

    def test_create_and_read_cycle(self, test_user, test_product):
        factory = APIRequestFactory()
        request = factory.post("/production-orders/")
        request.user = test_user
        create_data = get_base_production_data(test_product.id)
        create_data["assigned_operator_id"] = test_user.id

        create_serializer = ProductionOrderCreateSerializer(
            data=create_data, context={"request": request}
        )
        assert create_serializer.is_valid(), create_serializer.errors
        order = create_serializer.save()

        read_serializer = ProductionOrderSerializer(order)
        read_data = read_serializer.data

        assert read_data["order_number"] == create_data["order_number"]
        assert read_data["created_by"]["id"] == test_user.id
        assert read_data["assigned_operator"]["id"] == test_user.id

    def test_multiple_orders_unique_numbers(self, test_product, test_user):
        factory = APIRequestFactory()
        request = factory.post("/production-orders/")
        request.user = test_user

        base_time = timezone.now() + timedelta(hours=1)
        orders_data = [
            {"order_number": "UNIQUE-A-001", "planned_quantity": 100},
            {"order_number": "UNIQUE-B-001", "planned_quantity": 200},
        ]

        for i, base_data in enumerate(orders_data):
            data = get_base_production_data(test_product.id)
            data.update(base_data)
            serializer = ProductionOrderCreateSerializer(
                data=data, context={"request": request}
            )
            assert (
                serializer.is_valid()
            ), f"Failed for {data['order_number']}: {serializer.errors}"
            serializer.save()

        duplicate_data = get_base_production_data(test_product.id)
        duplicate_data["order_number"] = "UNIQUE-A-001"
        duplicate_serializer = ProductionOrderCreateSerializer(
            data=duplicate_data, context={"request": request}
        )
        assert not duplicate_serializer.is_valid()
        assert "order_number" in duplicate_serializer.errors
