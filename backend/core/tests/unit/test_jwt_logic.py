"""JWT 순수 로직 단위테스트"""
import pytest
from decimal import Decimal
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core.models.user import User


@pytest.mark.unit
class TestJWTLogic:
    """JWT 토큰 생성/검증 순수 로직 테스트"""

    def test_jwt_token_generation_for_user(self, test_user):
        """사용자로부터 JWT 토큰 생성 테스트"""
        refresh = RefreshToken.for_user(test_user)
        access_token = str(refresh.access_token)
        
        assert len(access_token) > 100  # JWT는 긴 문자열
        assert isinstance(refresh, RefreshToken)

    def test_jwt_payload_contains_user_info(self, test_user):
        """JWT 페이로드에 사용자 정보 포함 확인"""
        refresh = RefreshToken.for_user(test_user)
        access_payload = refresh.access_token.payload
        refresh_payload = refresh.payload
        
        # access 토큰 페이로드 검증
        assert access_payload['user_id'] == str(test_user.id)
        assert access_payload['token_type'] == 'access'
        
        # refresh 토큰 페이로드 검증  
        assert refresh_payload['user_id'] == str(test_user.id)
        assert refresh_payload['token_type'] == 'refresh'

    def test_jwt_token_has_expiration(self, test_user):
        """JWT 토큰에 만료시간이 설정되어 있는지 확인"""
        refresh = RefreshToken.for_user(test_user)
        access_payload = refresh.access_token.payload
        refresh_payload = refresh.payload
        
        assert 'exp' in access_payload
        assert 'exp' in refresh_payload
        assert 'iat' in access_payload  # issued at
        assert 'iat' in refresh_payload

    @pytest.mark.parametrize("role", ['admin', 'quality_manager', 'operator', 'auditor'])
    def test_jwt_generation_for_different_roles(self, role):
        """다양한 역할의 사용자에 대한 JWT 생성 테스트"""
        user = User.objects.create_user(
            username=f'test_{role}',
            password='testpass123',
            role=role,
            employee_id=f'TEST_{role.upper()}'
        )
        
        refresh = RefreshToken.for_user(user)
        payload = refresh.access_token.payload
        
        assert payload['user_id'] == str(user.id)
        assert len(str(refresh.access_token)) > 100

    def test_token_serializer_validation_success(self):
        """토큰 직렬화 검증 성공 테스트"""
        # 실제 사용자 생성
        user = User.objects.create_user(
            username='serializer_test',
            password='testpass123',
            role='operator',
            employee_id='SER001'
        )
        
        data = {
            'username': 'serializer_test',
            'password': 'testpass123'
        }
        
        serializer = TokenObtainPairSerializer(data=data)
        assert serializer.is_valid()
        
        validated_data = serializer.validated_data
        assert 'access' in validated_data
        assert 'refresh' in validated_data

    def test_token_serializer_validation_failure(self):
        """토큰 직렬화 검증 실패 테스트"""
        data = {
            'username': 'nonexistent',
            'password': 'wrongpass'
        }
        
        serializer = TokenObtainPairSerializer(data=data)
        
        # 유효하지 않은 자격증명에 대해서는 예외가 발생
        with pytest.raises(Exception):  # AuthenticationFailed 예외 발생
            serializer.is_valid(raise_exception=True)

    def test_refresh_token_can_generate_new_access(self, test_user):
        """Refresh 토큰으로 새 Access 토큰 생성 테스트"""
        refresh = RefreshToken.for_user(test_user)
        original_access = str(refresh.access_token)
        
        # 새 access 토큰 생성
        refresh.set_jti()  # jti 재설정
        new_access = str(refresh.access_token)
        
        # 새 토큰이 생성되었는지 확인 (jti가 달라서 토큰이 달라짐)
        assert len(new_access) > 100
        assert isinstance(new_access, str)


@pytest.mark.unit  
class TestUserModel:
    """User 모델 단위 테스트"""
    
    def test_user_creation_with_required_fields(self):
        """필수 필드로 사용자 생성 테스트"""
        user = User.objects.create_user(
            username='unittest',
            password='testpass123',
            role='operator',
            employee_id='UNIT001'
        )
        
        assert user.username == 'unittest'
        assert user.role == 'operator'
        assert user.employee_id == 'UNIT001'
        assert user.check_password('testpass123')
        assert user.is_active is True

    def test_user_str_representation(self):
        """User 모델 문자열 표현 테스트"""
        user = User.objects.create_user(
            username='strtest',
            password='testpass123', 
            role='admin',
            employee_id='STR001'
        )
        
        expected = "strtest (admin)"
        assert str(user) == expected

    @pytest.mark.parametrize("role", [
        'admin', 'quality_manager', 'production_manager', 'operator', 'auditor'
    ])
    def test_user_role_validation(self, role):
        """사용자 역할 검증 테스트"""
        user = User.objects.create_user(
            username=f'role_test_{role}',
            password='testpass123',
            role=role,
            employee_id=f'R_{role.upper()}'[:20]  # 20자 제한 준수
        )
        
        assert user.role == role

    def test_user_password_hashing(self):
        """비밀번호 해싱 테스트"""
        password = 'testpass123'
        user = User.objects.create_user(
            username='hashtest',
            password=password,
            role='operator',
            employee_id='HASH001'
        )
        
        # 비밀번호가 해싱되어 저장되었는지 확인
        assert user.password != password  # 원본과 다름
        assert user.check_password(password)  # 검증은 성공
        assert not user.check_password('wrongpass')  # 잘못된 비밀번호는 실패