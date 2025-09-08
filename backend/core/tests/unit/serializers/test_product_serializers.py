"""완제품 시리얼라이저 단위 테스트"""

import pytest
from unittest.mock import patch
from decimal import Decimal
from rest_framework.test import APIRequestFactory
from core.serializers.product_serializers import (
    FinishedProductSerializer,
    FinishedProductCreateSerializer,
    FinishedProductUpdateSerializer,
)
from core.services.cost_calculation_service import CostCalculationService


# 테스트에 사용할 완전한 기본 데이터
def get_full_product_data():
    return {
        "name": "Test Product",
        "code": "TP001",
        "description": "A test product description",
        "version": "1.0",
        "shelf_life_days": 30,
        "net_weight": 500.0,
        "packaging_type": "box",
        "storage_temp_min": 0.0,
        "storage_temp_max": 25.0,
        "allergen_info": "None",
        "is_active": True,
    }


@pytest.mark.unit
@pytest.mark.django_db
class TestFinishedProductSerializer:
    """FinishedProductSerializer 테스트"""

    def test_product_serialization_basic_fields(self, test_product, test_user):
        test_product.created_by = test_user
        test_product.save()
        serializer = FinishedProductSerializer(test_product)
        data = serializer.data
        assert data["id"] == str(test_product.id)
        assert data["created_by"]["id"] == test_user.id

    @patch.object(CostCalculationService, "calculate_product_cost")
    @patch.object(FinishedProductSerializer, "get_has_bom", return_value=True)
    def test_product_serialization_with_bom_and_cost_info(
        self, mock_get_has_bom, mock_calculate_cost, test_product
    ):
        """BOM 및 원가 정보가 포함된 완제품 직렬화"""
        mock_calculate_cost.return_value = {
            "unit_cost": Decimal("15.50"),
            "bom_missing": False,
            "calculation_method": "fifo",
            "warnings": [],
        }

        serializer = FinishedProductSerializer(test_product)
        data = serializer.data

        assert data["has_bom"] is True
        assert data["estimated_unit_cost"] == "15.50"
        assert data["cost_calculation_status"]["bom_missing"] is False

    @patch.object(CostCalculationService, "calculate_product_cost")
    def test_product_serialization_with_cost_calculation_error(
        self, mock_calculate_cost, test_product
    ):
        mock_calculate_cost.side_effect = Exception("Cost calculation failed")
        serializer = FinishedProductSerializer(test_product)
        data = serializer.data
        assert data["estimated_unit_cost"] == "0"
        assert data["cost_calculation_status"]["calculation_method"] == "error"


@pytest.mark.unit
@pytest.mark.django_db
class TestFinishedProductCreateSerializer:
    """FinishedProductCreateSerializer 테스트"""

    def test_valid_product_creation(self, test_user):
        factory = APIRequestFactory()
        request = factory.post("/products/")
        request.user = test_user
        data = get_full_product_data()
        data["code"] = "NTP001"
        serializer = FinishedProductCreateSerializer(
            data=data, context={"request": request}
        )
        assert serializer.is_valid(), serializer.errors
        product = serializer.save()
        assert product.name == "Test Product"

    def test_duplicate_code_validation(self, test_product):
        data = get_full_product_data()
        data["code"] = test_product.code
        serializer = FinishedProductCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "code" in serializer.errors

    def test_shelf_life_validation(self):
        data = get_full_product_data()
        data["shelf_life_days"] = 0
        serializer = FinishedProductCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "shelf_life_days" in serializer.errors
        assert "유통기한은 0일보다 커야 합니다." in str(
            serializer.errors["shelf_life_days"]
        )

    def test_net_weight_validation(self):
        data = get_full_product_data()
        data["net_weight"] = 0
        serializer = FinishedProductCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "net_weight" in serializer.errors
        assert "순중량은 0보다 커야 합니다." in str(serializer.errors["net_weight"])

    def test_created_by_auto_assignment(self, test_user):
        factory = APIRequestFactory()
        request = factory.post("/products/")
        request.user = test_user
        data = get_full_product_data()
        data["code"] = "CBT001"
        serializer = FinishedProductCreateSerializer(
            data=data, context={"request": request}
        )
        assert serializer.is_valid(), serializer.errors
        product = serializer.save()
        assert product.created_by == test_user


@pytest.mark.unit
@pytest.mark.django_db
class TestFinishedProductUpdateSerializer:
    """FinishedProductUpdateSerializer 테스트"""

    def test_valid_product_update(self, test_product):
        data = {"name": "Updated Product Name", "version": "2.0"}
        serializer = FinishedProductUpdateSerializer(
            test_product, data=data, partial=True
        )
        assert serializer.is_valid(), serializer.errors
        updated_product = serializer.save()
        assert updated_product.name == "Updated Product Name"
