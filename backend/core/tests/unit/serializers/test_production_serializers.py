"""생산 시리얼라이저 단위 테스트"""

import pytest
from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from core.models import ProductionOrder
from core.serializers.production_serializers import (
    ProductionOrderSerializer,
    ProductionOrderCreateSerializer,
    ProductionOrderUpdateSerializer,
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


@pytest.mark.unit
@pytest.mark.django_db
class TestProductionOrderSerializer:
    """ProductionOrderSerializer 테스트"""

    def test_production_order_serialization_basic_fields(
        self, test_production_order, test_user
    ):
        test_production_order.created_by = test_user
        test_production_order.assigned_operator = test_user
        test_production_order.save()

        serializer = ProductionOrderSerializer(test_production_order)
        data = serializer.data

        assert data["id"] == str(test_production_order.id)
        assert data["planned_quantity"] == "100.000"
        assert data["produced_quantity"] == "0.000"  # Fixture의 기본값은 0
        assert data["assigned_operator"]["id"] == test_user.id
        assert data["created_by"]["id"] == test_user.id

    def test_completion_rate_calculation(self, test_product, test_user):
        order = ProductionOrder.objects.create(
            order_number="COMP_TEST_001",
            finished_product=test_product,
            planned_quantity=100,
            produced_quantity=75,
            planned_start_date=timezone.now(),
            planned_end_date=timezone.now() + timedelta(days=1),
            created_by=test_user,
        )
        serializer = ProductionOrderSerializer(order)
        assert serializer.data["completion_rate"] == 75.0


@pytest.mark.unit
@pytest.mark.django_db
class TestProductionOrderCreateSerializer:
    """ProductionOrderCreateSerializer 테스트"""

    def test_valid_production_order_creation(self, test_product, test_user):
        factory = APIRequestFactory()
        request = factory.post("/production-orders/")
        request.user = test_user
        data = get_base_production_data(test_product.id)
        data["assigned_operator_id"] = test_user.id

        serializer = ProductionOrderCreateSerializer(
            data=data, context={"request": request}
        )
        assert serializer.is_valid(), serializer.errors
        order = serializer.save()
        assert order.order_number == "PO-TEST-001"
        assert order.assigned_operator == test_user
        assert order.created_by == test_user

    def test_duplicate_order_number_validation(
        self, test_production_order, test_product
    ):
        data = get_base_production_data(test_product.id)
        data["order_number"] = test_production_order.order_number
        serializer = ProductionOrderCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "order_number" in serializer.errors
        assert "unique" in [e.code for e in serializer.errors["order_number"]]

    def test_planned_quantity_validation(self, test_product):
        data = get_base_production_data(test_product.id)
        data["planned_quantity"] = 0
        serializer = ProductionOrderCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "planned_quantity" in serializer.errors
        assert "min_value" in [e.code for e in serializer.errors["planned_quantity"]]

    def test_date_range_validation_invalid(self, test_product):
        data = get_base_production_data(test_product.id)
        data["planned_end_date"] = (timezone.now() - timedelta(hours=1)).isoformat()
        serializer = ProductionOrderCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "planned_end_date" in serializer.errors

    def test_past_start_date_validation(self, test_product):
        data = get_base_production_data(test_product.id)
        data["planned_start_date"] = (timezone.now() - timedelta(hours=1)).isoformat()
        serializer = ProductionOrderCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "planned_start_date" in serializer.errors

    def test_optional_fields(self, test_product, test_user):
        factory = APIRequestFactory()
        request = factory.post("/production-orders/")
        request.user = test_user
        data = get_base_production_data(test_product.id)
        serializer = ProductionOrderCreateSerializer(
            data=data, context={"request": request}
        )
        assert serializer.is_valid(), serializer.errors
        order = serializer.save()
        assert order.status == "planned"
        assert order.assigned_operator is None


@pytest.mark.unit
@pytest.mark.django_db
class TestProductionOrderUpdateSerializer:
    """ProductionOrderUpdateSerializer 테스트"""

    def test_valid_production_order_update(self, test_production_order, test_user):
        data = {"planned_quantity": 1000, "assigned_operator_id": test_user.id}
        serializer = ProductionOrderUpdateSerializer(
            test_production_order, data=data, partial=True
        )
        assert serializer.is_valid(), serializer.errors
        updated_order = serializer.save()
        assert updated_order.planned_quantity == 1000
        assert updated_order.assigned_operator == test_user
