"""공급업체 시리얼라이저 통합 테스트"""

import pytest
from rest_framework.test import APIRequestFactory

from core.serializers.supplier_serializers import (
    SupplierSerializer, SupplierCreateSerializer, SupplierUpdateSerializer
)


@pytest.mark.integration
@pytest.mark.django_db
class TestSupplierSerializersIntegration:
    """공급업체 시리얼라이저 통합 테스트"""

    def test_create_and_read_cycle(self, test_user):
        """생성 후 조회 사이클 테스트"""
        # 1. 공급업체 생성
        factory = APIRequestFactory()
        request = factory.post('/suppliers/')
        request.user = test_user
        
        create_data = {
            'name': 'Cycle Test Supplier',
            'code': 'CYCLE001',
            'contact_person': 'Cycle Manager',
            'email': 'cycle@test.com',
            'phone': '02-1234-5678',
            'address': 'Cycle Address',
            'certification': 'ISO 14001',
            'status': 'active'
        }
        
        create_serializer = SupplierCreateSerializer(
            data=create_data, 
            context={'request': request}
        )
        assert create_serializer.is_valid(), create_serializer.errors
        
        supplier = create_serializer.save()
        
        # 2. 생성된 공급업체 조회
        read_serializer = SupplierSerializer(supplier)
        read_data = read_serializer.data
        
        assert read_data['name'] == 'Cycle Test Supplier'
        assert read_data['code'] == 'CYCLE001'
        assert read_data['contact_person'] == 'Cycle Manager'
        assert read_data['email'] == 'cycle@test.com'
        assert read_data['status'] == 'active'
        assert read_data['created_by']['id'] == test_user.id

    def test_create_update_read_cycle(self, test_user):
        """생성 -> 수정 -> 조회 사이클 테스트"""
        # 1. 공급업체 생성
        factory = APIRequestFactory()
        request = factory.post('/suppliers/')
        request.user = test_user
        
        create_data = {
            'name': 'Full Cycle Supplier',
            'code': 'FULL001',
            'contact_person': 'Full Manager',
            'email': 'full@test.com',
            'phone': '02-1111-2222',
            'address': 'Full Cycle Address',
            'status': 'active'
        }
        
        create_serializer = SupplierCreateSerializer(
            data=create_data,
            context={'request': request}
        )
        assert create_serializer.is_valid(), create_serializer.errors
        supplier = create_serializer.save()
        
        # 2. 공급업체 수정
        update_data = {
            'name': 'Updated Full Cycle Supplier',
            'contact_person': 'Updated Manager',
            'email': 'updated_full@test.com',
            'phone': '02-9999-8888',
            'status': 'inactive'
        }
        
        update_serializer = SupplierUpdateSerializer(supplier, data=update_data, partial=True)
        assert update_serializer.is_valid(), update_serializer.errors
        updated_supplier = update_serializer.save()
        
        # 3. 수정된 공급업체 조회
        read_serializer = SupplierSerializer(updated_supplier)
        read_data = read_serializer.data
        
        assert read_data['name'] == 'Updated Full Cycle Supplier'
        assert read_data['contact_person'] == 'Updated Manager'
        assert read_data['email'] == 'updated_full@test.com'
        assert read_data['phone'] == '02-9999-8888'
        assert read_data['status'] == 'inactive'
        assert read_data['code'] == 'FULL001'  # 코드는 변경되지 않음

    def test_multiple_suppliers_unique_codes(self, test_user):
        """여러 공급업체 생성 시 고유 코드 보장 테스트"""
        factory = APIRequestFactory()
        request = factory.post('/suppliers/')
        request.user = test_user

        suppliers_data = [
            {'name': 'Supplier A', 'code': 'UNIQUE_A', 'contact_person': 'Manager A', 'email': 'a@test.com', 'phone': '1', 'address': 'A', 'status': 'active'},
            {'name': 'Supplier B', 'code': 'UNIQUE_B', 'contact_person': 'Manager B', 'email': 'b@test.com', 'phone': '2', 'address': 'B', 'status': 'active'},
            {'name': 'Supplier C', 'code': 'UNIQUE_C', 'contact_person': 'Manager C', 'email': 'c@test.com', 'phone': '3', 'address': 'C', 'status': 'active'},
        ]
        
        created_suppliers = []
        
        # 각각 성공적으로 생성되어야 함
        for data in suppliers_data:
            serializer = SupplierCreateSerializer(data=data, context={'request': request})
            assert serializer.is_valid(), f"Failed for {data['code']}: {serializer.errors}"
            supplier = serializer.save()
            created_suppliers.append(supplier)
        
        # 모든 코드가 고유한지 확인
        codes = [s.code for s in created_suppliers]
        assert len(codes) == len(set(codes))  # 중복 없음
        
        # 중복 코드로 추가 생성 시도는 실패해야 함
        duplicate_data = {'name': 'Duplicate', 'code': 'UNIQUE_A', 'contact_person': 'Duplicate', 'email': 'd@test.com', 'phone': '4', 'address': 'D', 'status': 'active'}
        duplicate_serializer = SupplierCreateSerializer(data=duplicate_data, context={'request': request})
        assert not duplicate_serializer.is_valid()
        assert 'code' in duplicate_serializer.errors
