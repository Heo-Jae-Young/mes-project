"""사용자 시리얼라이저 단위 테스트"""

import pytest

from core.models import User
from core.serializers.user_serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
)


@pytest.mark.unit
@pytest.mark.django_db
class TestUserSerializer:
    """UserSerializer 테스트"""

    def test_user_serialization(self, test_user):
        """사용자 직렬화 테스트"""
        serializer = UserSerializer(test_user)
        data = serializer.data

        # 필수 필드 검증
        assert data["id"] == test_user.id
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert data["role"] == test_user.role
        assert data["is_active"] == test_user.is_active

        # 비밀번호 필드 제외 확인
        assert "password" not in data

        # 읽기 전용 필드들 포함 확인
        assert "created_at" in data
        assert "updated_at" in data

    def test_user_serialization_with_all_fields(self):
        """모든 필드가 포함된 사용자 직렬화"""
        user = User.objects.create_user(
            username="fulluser",
            email="full@test.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            role="quality_manager",
            employee_id="EMP001",
            department="QC",
            phone="010-1234-5678",
        )

        serializer = UserSerializer(user)
        data = serializer.data

        assert data["first_name"] == "Test"
        assert data["last_name"] == "User"
        assert data["employee_id"] == "EMP001"
        assert data["department"] == "QC"
        assert data["phone"] == "010-1234-5678"


@pytest.mark.unit
@pytest.mark.django_db
class TestUserCreateSerializer:
    """UserCreateSerializer 테스트"""

    def test_valid_user_creation(self):
        """유효한 사용자 생성 테스트"""
        data = {
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "SecurePassword123!",
            "password_confirm": "SecurePassword123!",
            "first_name": "New",
            "last_name": "User",
            "role": "operator",
            "employee_id": "EMP002",
            "department": "Production",
            "phone": "010-9876-5432",
        }

        serializer = UserCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

        user = serializer.save()

        assert user.username == "newuser"
        assert user.email == "newuser@test.com"
        assert user.check_password("SecurePassword123!")
        assert user.role == "operator"
        assert user.employee_id == "EMP002"

    def test_password_mismatch_validation(self):
        """비밀번호 불일치 검증 테스트"""
        data = {
            "username": "testuser",
            "email": "test@test.com",
            "password": "Password123!",
            "password_confirm": "DifferentPassword123!",
            "role": "operator",
        }

        serializer = UserCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "비밀번호가 일치하지 않습니다." in str(serializer.errors)

    def test_weak_password_validation(self):
        """약한 비밀번호 검증 테스트"""
        data = {
            "username": "testuser",
            "email": "test@test.com",
            "password": "123",  # 너무 약한 비밀번호
            "password_confirm": "123",
            "role": "operator",
        }

        serializer = UserCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "password" in serializer.errors

    def test_missing_required_fields(self):
        """필수 필드 누락 테스트"""
        data = {
            "username": "testuser",
            # email 누락
            "password": "SecurePassword123!",
            "password_confirm": "SecurePassword123!",
        }

        serializer = UserCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_password_confirm_is_removed_after_validation(self):
        """비밀번호 확인 필드가 검증 후 제거되는지 테스트"""
        data = {
            "username": "testuser",
            "email": "test@test.com",
            "password": "SecurePassword123!",
            "password_confirm": "SecurePassword123!",
            "role": "operator",
        }

        serializer = UserCreateSerializer(data=data)
        assert serializer.is_valid()

        user = serializer.save()
        # password_confirm이 실제로 User 모델에 저장되지 않음을 확인
        assert not hasattr(user, "password_confirm")


@pytest.mark.unit
@pytest.mark.django_db
class TestUserUpdateSerializer:
    """UserUpdateSerializer 테스트"""

    def test_valid_user_update(self, test_user):
        """유효한 사용자 정보 수정 테스트"""
        data = {
            "email": "updated@test.com",
            "first_name": "Updated",
            "last_name": "Name",
            "department": "Updated Dept",
        }

        serializer = UserUpdateSerializer(test_user, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors

        updated_user = serializer.save()

        assert updated_user.email == "updated@test.com"
        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == "Name"
        assert updated_user.department == "Updated Dept"

    def test_password_update(self, test_user):
        """비밀번호 업데이트 테스트"""
        data = {
            "password": "NewSecurePassword123!",
            "password_confirm": "NewSecurePassword123!",
        }

        serializer = UserUpdateSerializer(test_user, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors

        updated_user = serializer.save()
        assert updated_user.check_password("NewSecurePassword123!")

    def test_password_update_mismatch(self, test_user):
        """비밀번호 업데이트 불일치 테스트"""
        data = {
            "password": "NewPassword123!",
            "password_confirm": "DifferentPassword123!",
        }

        serializer = UserUpdateSerializer(test_user, data=data, partial=True)
        assert not serializer.is_valid()
        assert "비밀번호가 일치하지 않습니다." in str(serializer.errors)

    def test_partial_password_update_validation(self, test_user):
        """부분적 비밀번호 업데이트 검증"""
        # password만 있고 password_confirm이 없는 경우
        data = {"password": "NewPassword123!"}

        serializer = UserUpdateSerializer(test_user, data=data, partial=True)
        assert not serializer.is_valid()
        assert "비밀번호가 일치하지 않습니다." in str(serializer.errors)

        # password_confirm만 있고 password가 없는 경우
        data = {"password_confirm": "NewPassword123!"}

        serializer = UserUpdateSerializer(test_user, data=data, partial=True)
        assert not serializer.is_valid()
        assert "비밀번호가 일치하지 않습니다." in str(serializer.errors)

    def test_user_deactivation(self, test_user):
        """사용자 비활성화 테스트"""
        assert test_user.is_active is True

        data = {"is_active": False}

        serializer = UserUpdateSerializer(test_user, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors

        updated_user = serializer.save()
        assert updated_user.is_active is False

    def test_role_update(self, test_user):
        """역할 변경 테스트"""
        original_role = test_user.role
        new_role = "admin" if original_role != "admin" else "operator"

        data = {"role": new_role}

        serializer = UserUpdateSerializer(test_user, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors

        updated_user = serializer.save()
        assert updated_user.role == new_role

    def test_empty_update(self, test_user):
        """빈 데이터로 업데이트 테스트"""
        original_email = test_user.email

        serializer = UserUpdateSerializer(test_user, data={}, partial=True)
        assert serializer.is_valid()

        updated_user = serializer.save()
        # 아무것도 변경되지 않음
        assert updated_user.email == original_email
