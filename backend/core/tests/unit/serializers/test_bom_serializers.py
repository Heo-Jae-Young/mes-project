"""BOM 시리얼라이저 단위 테스트"""

import pytest
from decimal import Decimal
from rest_framework.test import APIRequestFactory

from core.models import BOM
from core.serializers.bom_serializers import (
    BOMCreateSerializer, BOMUpdateSerializer, BOMListSerializer, BOMDetailSerializer, ProductBOMSummarySerializer
)


@pytest.mark.unit
@pytest.mark.django_db
class TestBOMCreateSerializer:
    """BOMCreateSerializer 테스트"""

    def test_valid_bom_creation(self, test_finished_product, test_raw_material, test_user):
        """유효한 BOM 생성 테스트"""
        factory = APIRequestFactory()
        request = factory.post('/boms/')
        request.user = test_user

        data = {
            'finished_product': test_finished_product.id,
            'raw_material': test_raw_material.id,
            'quantity_per_unit': '10.500',
            'unit': 'kg',
            'is_active': True,
            'notes': 'Test BOM creation'
        }

        serializer = BOMCreateSerializer(data=data, context={'request': request})
        assert serializer.is_valid(), serializer.errors

        bom = serializer.save()

        assert bom.finished_product == test_finished_product
        assert bom.raw_material == test_raw_material
        assert bom.quantity_per_unit == Decimal('10.500')
        assert bom.unit == 'kg'
        assert bom.is_active is True
        assert bom.notes == 'Test BOM creation'
        assert bom.created_by == test_user

    def test_duplicate_bom_combination_validation(self, test_finished_product, test_raw_material, test_user):
        """동일 제품-원자재 조합 중복 검증 테스트"""
        # 기존 BOM 생성
        BOM.objects.create(
            finished_product=test_finished_product,
            raw_material=test_raw_material,
            quantity_per_unit=Decimal('1.0'),
            unit='g',
            created_by=test_user
        )

        factory = APIRequestFactory()
        request = factory.post('/boms/')
        request.user = test_user

        data = {
            'finished_product': test_finished_product.id,
            'raw_material': test_raw_material.id,
            'quantity_per_unit': '2.000',
            'unit': 'kg',
        }

        serializer = BOMCreateSerializer(data=data, context={'request': request})
        assert not serializer.is_valid()
        # Django의 unique_together 검증이나 custom validation 둘 다 가능
        assert ('raw_material' in serializer.errors and '이미 해당 제품에 등록된 원자재입니다.' in str(serializer.errors['raw_material'])) or \
               ('non_field_errors' in serializer.errors and 'unique' in str(serializer.errors['non_field_errors']).lower())

    def test_quantity_per_unit_validation_zero_or_negative(self, test_finished_product, test_raw_material):
        """단위당 소요량 0 또는 음수 값 검증 테스트"""
        data = {
            'finished_product': test_finished_product.id,
            'raw_material': test_raw_material.id,
            'quantity_per_unit': '0.000',
            'unit': 'kg',
        }

        serializer = BOMCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'quantity_per_unit' in serializer.errors
        assert ('단위당 소요량은 0보다 커야 합니다.' in str(serializer.errors['quantity_per_unit']) or 
                'greater than or equal to 0.001' in str(serializer.errors['quantity_per_unit']))

        data['quantity_per_unit'] = '-1.000'
        serializer = BOMCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'quantity_per_unit' in serializer.errors
        assert ('단위당 소요량은 0보다 커야 합니다.' in str(serializer.errors['quantity_per_unit']) or 
                'greater than or equal to 0.001' in str(serializer.errors['quantity_per_unit']))

    def test_missing_required_fields(self):
        """필수 필드 누락 테스트"""
        data = {
            # finished_product, raw_material, quantity_per_unit, unit 누락
        }

        serializer = BOMCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'finished_product' in serializer.errors
        assert 'raw_material' in serializer.errors
        assert 'quantity_per_unit' in serializer.errors
        assert 'unit' in serializer.errors

    def test_created_by_without_request_context(self, test_finished_product, test_raw_material):
        """요청 컨텍스트 없이 생성 시 created_by 누락 검증 테스트"""
        data = {
            'finished_product': test_finished_product.id,
            'raw_material': test_raw_material.id,
            'quantity_per_unit': '1.000',
            'unit': 'kg',
        }

        serializer = BOMCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors
        assert '인증된 사용자가 필요합니다.' in str(serializer.errors['non_field_errors'])


@pytest.mark.unit
@pytest.mark.django_db
class TestBOMUpdateSerializer:
    """BOMUpdateSerializer 테스트"""

    def test_valid_bom_update(self, test_bom):
        """유효한 BOM 수정 테스트"""
        data = {
            'quantity_per_unit': '15.000',
            'unit': 'g',
            'is_active': False,
            'notes': 'Updated notes'
        }

        serializer = BOMUpdateSerializer(test_bom, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors

        updated_bom = serializer.save()

        assert updated_bom.quantity_per_unit == Decimal('15.000')
        assert updated_bom.unit == 'g'
        assert updated_bom.is_active is False
        assert updated_bom.notes == 'Updated notes'

    def test_quantity_per_unit_validation_zero_or_negative_update(self, test_bom):
        """업데이트 시 단위당 소요량 0 또는 음수 값 검증 테스트"""
        data = {
            'quantity_per_unit': '0.000',
        }

        serializer = BOMUpdateSerializer(test_bom, data=data, partial=True)
        assert not serializer.is_valid()
        assert 'quantity_per_unit' in serializer.errors
        assert ('단위당 소요량은 0보다 커야 합니다.' in str(serializer.errors['quantity_per_unit']) or 
                'greater than or equal to 0.001' in str(serializer.errors['quantity_per_unit']))

        data['quantity_per_unit'] = '-1.000'
        serializer = BOMUpdateSerializer(test_bom, data=data, partial=True)
        assert not serializer.is_valid()
        assert 'quantity_per_unit' in serializer.errors
        assert ('단위당 소요량은 0보다 커야 합니다.' in str(serializer.errors['quantity_per_unit']) or 
                'greater than or equal to 0.001' in str(serializer.errors['quantity_per_unit']))


@pytest.mark.unit
@pytest.mark.django_db
class TestBOMListSerializer:
    """BOMListSerializer 테스트"""

    def test_bom_list_serialization(self, test_bom):
        """BOM 목록 직렬화 테스트"""
        serializer = BOMListSerializer(test_bom)
        data = serializer.data

        assert data['id'] == str(test_bom.id)
        assert data['finished_product']['id'] == str(test_bom.finished_product.id)
        assert data['raw_material']['id'] == str(test_bom.raw_material.id)
        assert data['quantity_per_unit'] == str(test_bom.quantity_per_unit)
        assert data['unit'] == test_bom.unit
        assert data['is_active'] == test_bom.is_active
        assert data['notes'] == test_bom.notes
        assert 'created_at' in data
        assert 'updated_at' in data
        assert 'total_required_for_production' in data

    def test_total_required_for_production_calculation_with_context(self, test_bom):
        """컨텍스트에 production_quantity 전달 시 총 소요량 계산 테스트"""
        production_quantity = 10
        serializer = BOMListSerializer(test_bom, context={'production_quantity': production_quantity})
        data = serializer.data

        expected_total = test_bom.quantity_per_unit * Decimal(str(production_quantity))
        assert Decimal(data['total_required_for_production']) == expected_total

    def test_total_required_for_production_calculation_without_context(self, test_bom):
        """컨텍스트에 production_quantity 없을 시 기본값(1)으로 총 소요량 계산 테스트"""
        serializer = BOMListSerializer(test_bom)
        data = serializer.data

        expected_total = test_bom.quantity_per_unit * Decimal('1')
        assert Decimal(data['total_required_for_production']) == expected_total


@pytest.mark.unit
@pytest.mark.django_db
class TestBOMDetailSerializer:
    """BOMDetailSerializer 테스트"""

    def test_bom_detail_serialization(self, test_bom):
        """BOM 상세 직렬화 테스트"""
        serializer = BOMDetailSerializer(test_bom)
        data = serializer.data

        assert data['id'] == str(test_bom.id)
        assert data['finished_product']['id'] == str(test_bom.finished_product.id)
        assert data['raw_material']['id'] == str(test_bom.raw_material.id)
        assert data['quantity_per_unit'] == str(test_bom.quantity_per_unit)
        assert data['unit'] == test_bom.unit
        assert data['is_active'] == test_bom.is_active
        assert data['notes'] == test_bom.notes
        assert 'created_at' in data
        assert 'updated_at' in data
        assert 'material_info' in data
        assert 'product_info' in data

        # material_info와 product_info 필드 내용 확인
        assert data['material_info']['id'] == str(test_bom.raw_material.id)
        assert data['product_info']['id'] == str(test_bom.finished_product.id)


@pytest.mark.unit
@pytest.mark.django_db
class TestProductBOMSummarySerializer:
    """ProductBOMSummarySerializer 테스트"""

    def test_product_bom_summary_serialization(self, test_bom):
        """제품 BOM 요약 직렬화 테스트"""
        serializer = ProductBOMSummarySerializer(test_bom)
        data = serializer.data

        assert data['id'] == str(test_bom.id)
        assert data['raw_material_name'] == test_bom.raw_material.name
        assert data['raw_material_code'] == test_bom.raw_material.code
        assert data['raw_material_category'] == test_bom.raw_material.category
        assert data['quantity_per_unit'] == str(test_bom.quantity_per_unit)
        assert data['unit'] == test_bom.unit
        assert data['is_active'] == test_bom.is_active