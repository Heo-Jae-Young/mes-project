"""JWT 인증 관련 테스트 헬퍼 함수들"""
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from .user_helpers import create_test_user


def generate_jwt_token(user):
    """사용자로부터 JWT 토큰 생성"""
    return RefreshToken.for_user(user)


def generate_jwt_for_role(role='admin'):
    """특정 역할의 사용자 생성하고 JWT 토큰 반환"""
    user = create_test_user(role=role)
    return RefreshToken.for_user(user), user


def create_authenticated_client(role='admin', user=None):
    """인증된 API 클라이언트 생성"""
    client = APIClient()
    
    if user is None:
        user = create_test_user(role=role)
    
    token = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
    
    return client, user, token


def authenticate_client(client, user):
    """기존 클라이언트에 인증 설정"""
    token = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
    return token


def get_auth_headers(user):
    """인증 헤더 딕셔너리 반환"""
    token = RefreshToken.for_user(user)
    return {
        'HTTP_AUTHORIZATION': f'Bearer {token.access_token}'
    }


def create_token_data(username='testuser', password='testpass123'):
    """토큰 요청용 데이터 생성"""
    return {
        'username': username,
        'password': password
    }