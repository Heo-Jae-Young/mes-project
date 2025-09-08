import pytest
from rest_framework.test import APIRequestFactory

from core.serializers.product_serializers import (
    FinishedProductSerializer,
    FinishedProductCreateSerializer,
    FinishedProductUpdateSerializer,
)


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


@pytest.mark.integration
@pytest.mark.django_db
class TestFinishedProductSerializersIntegration:
    """완제품 시리얼라이저 통합 테스트"""

    def test_create_and_read_cycle(self, test_user):
        factory = APIRequestFactory()
        request = factory.post("/products/")
        request.user = test_user
        create_data = get_full_product_data()
        create_serializer = FinishedProductCreateSerializer(
            data=create_data, context={"request": request}
        )
        assert create_serializer.is_valid(), create_serializer.errors
        product = create_serializer.save()

        read_serializer = FinishedProductSerializer(product)
        read_data = read_serializer.data

        assert read_data["name"] == create_data["name"]
        assert read_data["created_by"]["id"] == test_user.id

    def test_create_update_read_cycle(self, test_user):
        factory = APIRequestFactory()
        request = factory.post("/products/")
        request.user = test_user
        create_data = get_full_product_data()
        create_serializer = FinishedProductCreateSerializer(
            data=create_data, context={"request": request}
        )
        assert create_serializer.is_valid(), create_serializer.errors
        product = create_serializer.save()

        update_data = {"name": "Updated Full Cycle Product", "version": "2.0"}
        update_serializer = FinishedProductUpdateSerializer(
            product, data=update_data, partial=True
        )
        assert update_serializer.is_valid(), update_serializer.errors
        updated_product = update_serializer.save()

        read_serializer = FinishedProductSerializer(updated_product)
        read_data = read_serializer.data

        assert read_data["name"] == "Updated Full Cycle Product"
