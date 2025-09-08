"""사용자 시리얼라이저 통합 테스트"""

import pytest

from core.serializers.user_serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
)


@pytest.mark.integration
@pytest.mark.django_db
class TestUserSerializersIntegration:
    """사용자 시리얼라이저 통합 테스트"""

    def test_create_and_read_cycle(self):
        """생성 후 조회 사이클 테스트"""
        # 1. 사용자 생성
        create_data = {
            "username": "cycleuser",
            "email": "cycle@test.com",
            "password": "CyclePassword123!",
            "password_confirm": "CyclePassword123!",
            "role": "quality_manager",
            "first_name": "Cycle",
            "last_name": "Test",
        }

        create_serializer = UserCreateSerializer(data=create_data)
        assert create_serializer.is_valid(), create_serializer.errors

        user = create_serializer.save()

        # 2. 생성된 사용자 조회
        read_serializer = UserSerializer(user)
        read_data = read_serializer.data

        assert read_data["username"] == "cycleuser"
        assert read_data["email"] == "cycle@test.com"
        assert read_data["role"] == "quality_manager"
        assert read_data["first_name"] == "Cycle"
        assert read_data["last_name"] == "Test"
        assert "password" not in read_data

    def test_create_update_read_cycle(self):
        """생성 -> 수정 -> 조회 사이클 테스트"""
        # 1. 사용자 생성
        create_data = {
            "username": "fullcycleuser",
            "email": "fullcycle@test.com",
            "password": "InitialPassword123!",
            "password_confirm": "InitialPassword123!",
            "role": "operator",
        }

        create_serializer = UserCreateSerializer(data=create_data)
        assert create_serializer.is_valid(), create_serializer.errors
        user = create_serializer.save()

        # 2. 사용자 수정
        update_data = {
            "email": "updated_fullcycle@test.com",
            "role": "quality_manager",
            "first_name": "Updated",
            "password": "UpdatedPassword123!",
            "password_confirm": "UpdatedPassword123!",
        }

        update_serializer = UserUpdateSerializer(user, data=update_data, partial=True)
        assert update_serializer.is_valid(), update_serializer.errors
        updated_user = update_serializer.save()

        # 3. 수정된 사용자 조회
        read_serializer = UserSerializer(updated_user)
        read_data = read_serializer.data

        assert read_data["email"] == "updated_fullcycle@test.com"
        assert read_data["role"] == "quality_manager"
        assert read_data["first_name"] == "Updated"
        assert updated_user.check_password("UpdatedPassword123!")
