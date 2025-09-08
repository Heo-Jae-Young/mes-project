"""공급업체 시리얼라이저 단위 테스트"""

import pytest
from rest_framework.test import APIRequestFactory

from core.models import Supplier
from core.serializers.supplier_serializers import (
    SupplierSerializer,
    SupplierCreateSerializer,
    SupplierUpdateSerializer,
)


@pytest.mark.unit
@pytest.mark.django_db
class TestSupplierSerializer:
    """SupplierSerializer 테스트"""

    def test_supplier_serialization(self, test_supplier, test_user):
        """공급업체 직렬화 테스트"""
        test_supplier.created_by = test_user
        test_supplier.save()

        serializer = SupplierSerializer(test_supplier)
        data = serializer.data

        # 필수 필드 검증
        assert data["id"] == str(test_supplier.id)
        assert data["name"] == test_supplier.name
        assert data["code"] == test_supplier.code
        assert data["contact_person"] == test_supplier.contact_person
        assert data["email"] == test_supplier.email
        assert data["status"] == test_supplier.status

        # 읽기 전용 필드들 포함 확인
        assert "created_at" in data
        assert "updated_at" in data
        assert "created_by" in data

        # created_by 중첩 객체 확인
        assert data["created_by"]["id"] == test_user.id
        assert data["created_by"]["username"] == test_user.username

    def test_supplier_serialization_with_all_fields(self, test_user):
        """모든 필드가 포함된 공급업체 직렯화"""
        supplier = Supplier.objects.create(
            name="Complete Supplier Co.",
            code="COMP001",
            contact_person="John Manager",
            email="contact@complete.com",
            phone="02-1234-5678",
            address="123 Business St, Seoul",
            certification="ISO 9001:2015",
            status="active",
            created_by=test_user,
        )

        serializer = SupplierSerializer(supplier)
        data = serializer.data

        assert data["phone"] == "02-1234-5678"
        assert data["address"] == "123 Business St, Seoul"
        assert data["certification"] == "ISO 9001:2015"


@pytest.mark.unit
@pytest.mark.django_db
class TestSupplierCreateSerializer:
    """SupplierCreateSerializer 테스트"""

    def test_valid_supplier_creation(self, test_user):
        """유효한 공급업체 생성 테스트"""
        factory = APIRequestFactory()
        request = factory.post("/suppliers/")
        request.user = test_user

        data = {
            "name": "New Supplier Inc.",
            "code": "NEW001",
            "contact_person": "Jane Contact",
            "email": "jane@newsupplier.com",
            "phone": "02-9876-5432",
            "address": "456 Supply Ave, Seoul",
            "certification": "HACCP",
            "status": "active",
        }

        serializer = SupplierCreateSerializer(data=data, context={"request": request})
        assert serializer.is_valid(), serializer.errors

        supplier = serializer.save()

        assert supplier.name == "New Supplier Inc."
        assert supplier.code == "NEW001"
        assert supplier.contact_person == "Jane Contact"
        assert supplier.status == "active"

    def test_duplicate_code_validation(self, test_supplier, test_user):
        """중복 코드 검증 테스트"""
        factory = APIRequestFactory()
        request = factory.post("/suppliers/")
        request.user = test_user

        data = {
            "name": "Another Supplier",
            "code": test_supplier.code,  # 기존 supplier와 같은 코드
            "contact_person": "Another Contact",
            "email": "another@test.com",
            "phone": "02-1111-2222",
            "address": "Another Address",
            "status": "active",
        }

        serializer = SupplierCreateSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "code" in serializer.errors

    def test_missing_required_fields(self):
        """필수 필드 누락 테스트"""
        data = {
            "name": "Incomplete Supplier",
            # code 누락
            "contact_person": "Contact Person",
        }

        serializer = SupplierCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "code" in serializer.errors
        # email도 필수 필드이므로 검증
        assert "email" in serializer.errors
        assert "phone" in serializer.errors
        assert "address" in serializer.errors

    def test_created_by_auto_assignment_with_request_context(self, test_user):
        """요청 컨텍스트에서 created_by 자동 할당 테스트"""
        factory = APIRequestFactory()
        request = factory.post("/suppliers/")
        request.user = test_user

        data = {
            "name": "Context Supplier",
            "code": "CTX001",
            "contact_person": "Context Manager",
            "email": "ctx@test.com",
            "phone": "02-3333-4444",
            "address": "Context Address",
            "status": "active",
        }

        serializer = SupplierCreateSerializer(data=data, context={"request": request})
        assert serializer.is_valid(), serializer.errors

        supplier = serializer.save()
        assert supplier.created_by == test_user

    def test_created_by_without_request_context(self):
        """요청 컨텍스트 없이 생성 테스트"""
        data = {
            "name": "No Context Supplier",
            "code": "NOCTX001",
            "contact_person": "No Context Manager",
            "email": "noctx@test.com",
            "phone": "02-5555-6666",
            "address": "No Context Address",
            "status": "active",
        }

        serializer = SupplierCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors

    def test_optional_fields(self, test_user):
        """선택적 필드들 테스트"""
        factory = APIRequestFactory()
        request = factory.post("/suppliers/")
        request.user = test_user

        # 최소한의 필수 필드만으로 생성
        data = {
            "name": "Minimal Supplier",
            "code": "MIN001",
            "contact_person": "Min Contact",
            "email": "minimal@test.com",
            "phone": "02-1111-1111",
            "address": "Minimal Address",
            "status": "active",
        }

        serializer = SupplierCreateSerializer(data=data, context={"request": request})
        assert serializer.is_valid(), serializer.errors

        supplier = serializer.save()
        assert supplier.phone == "02-1111-1111"
        assert supplier.address == "Minimal Address"
        assert supplier.certification == ""  # 기본값


@pytest.mark.unit
@pytest.mark.django_db
class TestSupplierUpdateSerializer:
    """SupplierUpdateSerializer 테스트"""

    def test_valid_supplier_update(self, test_supplier):
        """유효한 공급업체 수정 테스트"""
        data = {
            "name": "Updated Supplier Name",
            "contact_person": "Updated Contact Person",
            "email": "updated@test.com",
            "phone": "02-1111-2222",
            "address": "Updated Address",
            "status": "inactive",
        }

        serializer = SupplierUpdateSerializer(test_supplier, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors

        updated_supplier = serializer.save()

        assert updated_supplier.name == "Updated Supplier Name"
        assert updated_supplier.contact_person == "Updated Contact Person"
        assert updated_supplier.email == "updated@test.com"
        assert updated_supplier.status == "inactive"

    def test_partial_update(self, test_supplier):
        """부분 업데이트 테스트"""
        original_name = test_supplier.name
        original_contact = test_supplier.contact_person

        data = {"email": "partial_update@test.com", "status": "suspended"}

        serializer = SupplierUpdateSerializer(test_supplier, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors

        updated_supplier = serializer.save()

        # 수정된 필드들
        assert updated_supplier.email == "partial_update@test.com"
        assert updated_supplier.status == "suspended"

        # 기존 값들은 유지
        assert updated_supplier.name == original_name
        assert updated_supplier.contact_person == original_contact

    def test_code_field_not_in_update(self, test_supplier):
        """코드 필드가 업데이트 필드에 포함되지 않음 확인"""
        data = {
            "name": "Updated Name",
            "code": "SHOULD_NOT_UPDATE",  # 이 필드는 무시되어야 함
        }

        original_code = test_supplier.code

        serializer = SupplierUpdateSerializer(test_supplier, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors

        updated_supplier = serializer.save()

        # 코드는 변경되지 않아야 함
        assert updated_supplier.code == original_code
        assert updated_supplier.name == "Updated Name"

    def test_empty_update(self, test_supplier):
        """빈 데이터로 업데이트 테스트"""
        original_name = test_supplier.name
        original_status = test_supplier.status

        serializer = SupplierUpdateSerializer(test_supplier, data={}, partial=True)
        assert serializer.is_valid()

        updated_supplier = serializer.save()

        # 아무것도 변경되지 않음
        assert updated_supplier.name == original_name
        assert updated_supplier.status == original_status
