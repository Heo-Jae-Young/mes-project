"""사용자 모델 단위 테스트"""

import pytest
from core.models import User
from django.contrib.auth import authenticate


@pytest.mark.unit
class TestUserModel:
    """사용자 모델 테스트"""

    def test_user_creation_with_roles(self):
        """역할별 사용자 생성 테스트"""
        # Admin 사용자
        admin = User.objects.create_user(
            username="admin_test",
            password="admin123",
            email="admin@test.com",
            role="admin"
        )
        assert admin.role == "admin"
        assert admin.is_active is True
        
        # Operator 사용자
        operator = User.objects.create_user(
            username="operator_test", 
            password="operator123",
            email="operator@test.com",
            role="operator"
        )
        assert operator.role == "operator"
        
        # Quality Manager 사용자
        quality_manager = User.objects.create_user(
            username="quality_test",
            password="quality123", 
            email="quality@test.com",
            role="quality_manager"
        )
        assert quality_manager.role == "quality_manager"

    def test_user_authentication(self):
        """사용자 인증 테스트"""
        # Given: 사용자 생성
        user = User.objects.create_user(
            username="auth_test",
            password="testpass123",
            email="auth@test.com",
            role="operator"
        )
        
        # When & Then: 올바른 비밀번호로 인증
        authenticated_user = authenticate(username="auth_test", password="testpass123")
        assert authenticated_user is not None
        assert authenticated_user.username == "auth_test"
        
        # When & Then: 잘못된 비밀번호로 인증 실패
        failed_auth = authenticate(username="auth_test", password="wrongpass")
        assert failed_auth is None

    def test_user_str_representation(self):
        """사용자 __str__ 메서드 테스트"""
        user = User.objects.create_user(
            username="str_test",
            password="test123",
            email="str@test.com", 
            role="admin"
        )
        
        # User 모델의 __str__: "username (role)" 형태
        assert str(user) == "str_test (admin)"

    def test_user_unique_username(self):
        """사용자명 중복 방지 테스트"""
        # 첫 번째 사용자 생성
        User.objects.create_user(
            username="duplicate_test",
            password="test123",
            email="first@test.com",
            role="admin"
        )
        
        # 중복 사용자명으로 생성 시도
        with pytest.raises(Exception):
            User.objects.create_user(
                username="duplicate_test",  # 중복!
                password="test456", 
                email="second@test.com",
                role="operator"
            )

    def test_user_email_validation(self):
        """이메일 유효성 검사 테스트"""
        # 정상적인 이메일
        user = User.objects.create_user(
            username="email_test",
            password="test123",
            email="valid@example.com",
            role="operator"
        )
        assert user.email == "valid@example.com"
        
        # 빈 이메일도 허용되는지 확인 (모델 설정에 따라)
        user2 = User.objects.create_user(
            username="email_test2",
            password="test123", 
            email="",
            role="operator"
        )
        assert user2.email == ""

    def test_user_role_choices(self):
        """사용자 역할 선택지 테스트"""
        valid_roles = ["admin", "quality_manager", "operator"]
        
        for role in valid_roles:
            user = User.objects.create_user(
                username=f"role_test_{role}",
                password="test123",
                email=f"{role}@test.com",
                role=role
            )
            assert user.role == role

    def test_user_is_active_default(self):
        """사용자 활성 상태 기본값 테스트"""
        user = User.objects.create_user(
            username="active_test",
            password="test123",
            email="active@test.com",
            role="operator"
        )
        assert user.is_active is True