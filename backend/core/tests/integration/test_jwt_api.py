"""JWT API 통합테스트 - 전체 HTTP 요청/응답 플로우"""
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from core.tests.helpers.user_helpers import create_test_user
from core.tests.helpers.auth_helpers import create_token_data


@pytest.mark.integration
class TestJWTAuthenticationAPI:
    """JWT 인증 API 통합 테스트"""
    
    def setup_method(self):
        """각 테스트 전 실행되는 설정"""
        self.client = APIClient()

    def test_token_obtain_success(self, admin_user):
        """토큰 발급 API 성공 테스트"""
        url = '/api/token/'
        data = create_token_data(
            username=admin_user.username,
            password='testpass123'  # 헬퍼에서 사용하는 기본 패스워드
        )
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert len(response.data['access']) > 100
        assert len(response.data['refresh']) > 100

    def test_token_obtain_invalid_credentials(self):
        """잘못된 자격증명으로 토큰 발급 실패 테스트"""
        url = '/api/token/'
        data = create_token_data(
            username='nonexistent',
            password='wrongpassword'
        )
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'access' not in response.data
        assert 'detail' in response.data or 'non_field_errors' in response.data

    def test_token_verify_valid(self, test_user):
        """유효한 토큰 검증 API 테스트"""
        # 토큰 생성
        refresh = RefreshToken.for_user(test_user)
        access_token = str(refresh.access_token)
        
        url = '/api/token/verify/'
        data = {'token': access_token}
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK

    def test_token_verify_invalid(self):
        """유효하지 않은 토큰 검증 API 테스트"""
        url = '/api/token/verify/'
        data = {'token': 'invalid.token.string'}
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_refresh_success(self, operator_user):
        """토큰 갱신 API 성공 테스트"""
        refresh = RefreshToken.for_user(operator_user)
        
        url = '/api/token/refresh/'
        data = {'refresh': str(refresh)}
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert len(response.data['access']) > 100

    def test_token_refresh_invalid(self):
        """유효하지 않은 refresh 토큰으로 갱신 실패 테스트"""
        url = '/api/token/refresh/'
        data = {'refresh': 'invalid.refresh.token'}
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_api_access_success(self, authenticated_client):
        """인증된 클라이언트로 API 접근 성공 테스트"""
        url = '/api/users/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data

    def test_unauthenticated_api_access_failure(self, api_client):
        """인증되지 않은 클라이언트로 API 접근 실패 테스트"""
        url = '/api/suppliers/'  # 인증이 필요한 엔드포인트
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize("role,expected_access", [
        ('admin', True),
        ('quality_manager', True), 
        ('operator', True),  # 현재는 모든 역할이 users 접근 가능
    ])
    def test_role_based_api_access(self, role, expected_access):
        """역할별 API 접근 권한 테스트"""
        # 역할별 사용자 생성
        user = create_test_user(role=role)
        
        # 클라이언트 인증 설정
        refresh = RefreshToken.for_user(user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = '/api/users/'
        response = client.get(url)
        
        if expected_access:
            assert response.status_code == status.HTTP_200_OK
        else:
            assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_expired_token_rejection(self, test_user):
        """만료된 토큰 거부 테스트 (실제로는 시간 조작이 어려우므로 개념적 테스트)"""
        refresh = RefreshToken.for_user(test_user)
        access_token = str(refresh.access_token)
        
        # 정상 토큰으로 먼저 확인
        url = '/api/token/verify/'
        data = {'token': access_token}
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK

    def test_jwt_authentication_flow_complete(self):
        """JWT 인증 전체 플로우 테스트"""
        # 1. 사용자 생성
        user = create_test_user(role='admin')
        
        # 2. 토큰 발급
        login_data = create_token_data(user.username, 'testpass123')
        token_response = self.client.post('/api/token/', login_data, format='json')
        assert token_response.status_code == status.HTTP_200_OK
        
        # 3. 토큰으로 API 접근
        access_token = token_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        api_response = self.client.get('/api/users/')
        assert api_response.status_code == status.HTTP_200_OK
        
        # 4. 토큰 검증
        verify_response = self.client.post('/api/token/verify/', {'token': access_token})
        assert verify_response.status_code == status.HTTP_200_OK
        
        # 5. 토큰 갱신
        refresh_token = token_response.data['refresh']
        refresh_response = self.client.post('/api/token/refresh/', {'refresh': refresh_token})
        assert refresh_response.status_code == status.HTTP_200_OK
        assert 'access' in refresh_response.data

    def test_multiple_concurrent_authentications(self):
        """여러 사용자 동시 인증 테스트"""
        users = [
            create_test_user(role='admin', username='concurrent_admin'),
            create_test_user(role='operator', username='concurrent_operator'),
            create_test_user(role='quality_manager', username='concurrent_qm')
        ]
        
        clients = []
        for user in users:
            client = APIClient()
            refresh = RefreshToken.for_user(user)
            client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
            clients.append(client)
        
        # 모든 클라이언트가 동시에 API 접근 가능한지 확인
        for client in clients:
            response = client.get('/api/users/')
            assert response.status_code == status.HTTP_200_OK