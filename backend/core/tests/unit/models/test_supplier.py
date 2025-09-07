"""공급업체 모델 단위 테스트"""

import pytest  
from core.models import Supplier, User


@pytest.mark.unit
class TestSupplierModel:
    """공급업체 모델 테스트"""

    @pytest.fixture
    def sample_user(self):
        """테스트용 사용자"""
        return User.objects.create_user(
            username="supplier_admin",
            password="admin123", 
            email="admin@test.com",
            role="admin"
        )

    def test_supplier_creation_success(self, sample_user):
        """공급업체 생성 테스트"""
        supplier = Supplier.objects.create(
            name="테스트 공급업체",
            code="SUP001",
            contact_person="김담당",
            phone="02-1234-5678", 
            email="supplier@test.com",
            address="서울시 강남구",
            created_by=sample_user
        )
        
        assert supplier.name == "테스트 공급업체"
        assert supplier.code == "SUP001"
        assert supplier.contact_person == "김담당"
        assert supplier.status == "active"

    def test_supplier_str_representation(self, sample_user):
        """공급업체 __str__ 메서드 테스트"""
        supplier = Supplier.objects.create(
            name="문자열 테스트 공급업체",
            code="SUP002",
            contact_person="이담당",
            phone="02-9876-5432",
            email="test@supplier.com", 
            address="부산시 해운대구",
            created_by=sample_user
        )
        
        # Supplier 모델의 실제 __str__ 확인 필요
        assert "문자열 테스트 공급업체" in str(supplier)

    def test_supplier_unique_code_constraint(self, sample_user):
        """공급업체 코드 중복 방지 테스트"""
        # 첫 번째 공급업체
        Supplier.objects.create(
            name="공급업체1",
            code="DUPLICATE_CODE", 
            contact_person="담당자1",
            phone="02-1111-1111",
            email="sup1@test.com",
            address="서울",
            created_by=sample_user
        )
        
        # 중복 코드로 생성 시도  
        with pytest.raises(Exception):
            Supplier.objects.create(
                name="공급업체2", 
                code="DUPLICATE_CODE",  # 중복!
                contact_person="담당자2",
                phone="02-2222-2222",
                email="sup2@test.com", 
                address="부산",
                created_by=sample_user
            )

    def test_supplier_status_management(self, sample_user):
        """공급업체 상태 관리 테스트"""
        supplier = Supplier.objects.create(
            name="상태 테스트 공급업체",
            code="SUP003",
            contact_person="상태담당",
            phone="02-3333-3333",
            email="status@test.com",
            address="대구", 
            status="active",
            created_by=sample_user
        )
        
        assert supplier.status == "active"
        
        # 정지 상태로 변경
        supplier.status = "suspended"
        supplier.save()
        
        supplier.refresh_from_db()
        assert supplier.status == "suspended"

    def test_supplier_required_fields(self, sample_user):
        """공급업체 필수 필드 검증"""
        # 필수 필드들이 모두 있으면 성공
        supplier = Supplier.objects.create(
            name="필수필드 테스트",
            code="SUP004",
            contact_person="필수담당",
            phone="02-4444-4444", 
            email="required@test.com",
            address="인천",
            created_by=sample_user
        )
        assert supplier.name == "필수필드 테스트"

    def test_supplier_certification_field(self, sample_user):
        """공급업체 인증 정보 선택 필드 테스트"""
        # certification은 선택 필드
        supplier = Supplier.objects.create(
            name="인증 테스트 공급업체", 
            code="SUP005",
            contact_person="인증담당",
            phone="02-5555-5555",
            email="cert@test.com",
            address="광주",
            certification="HACCP, ISO 22000",
            created_by=sample_user
        )
        
        assert supplier.certification == "HACCP, ISO 22000"