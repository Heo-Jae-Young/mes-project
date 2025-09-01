"""pytest fixtures 설정 파일"""
import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from core.tests.helpers.user_helpers import (
    create_test_user, create_admin_user, create_quality_manager, create_operator
)
from core.tests.helpers.auth_helpers import create_authenticated_client
from core.tests.helpers.haccp_helpers import create_test_ccp, create_test_ccp_log
from core.tests.helpers.supplier_helpers import create_test_supplier


# ================================
# User Fixtures
# ================================

@pytest.fixture
def test_user():
    """기본 테스트 사용자 (operator 역할)"""
    return create_test_user()


@pytest.fixture
def admin_user():
    """관리자 사용자"""
    return create_admin_user()


@pytest.fixture
def quality_manager():
    """품질관리자 사용자"""
    return create_quality_manager()


@pytest.fixture
def operator_user():
    """작업자 사용자"""
    return create_operator()


@pytest.fixture
def users_by_role():
    """역할별 사용자 딕셔너리"""
    return {
        'admin': create_admin_user(),
        'quality_manager': create_quality_manager(),
        'operator': create_operator()
    }


# ================================
# JWT Token Fixtures
# ================================

@pytest.fixture
def jwt_token(test_user):
    """기본 사용자의 JWT 토큰"""
    return RefreshToken.for_user(test_user)


@pytest.fixture
def admin_jwt_token(admin_user):
    """관리자의 JWT 토큰"""
    return RefreshToken.for_user(admin_user)


@pytest.fixture
def operator_jwt_token(operator_user):
    """작업자의 JWT 토큰"""
    return RefreshToken.for_user(operator_user)


# ================================
# API Client Fixtures
# ================================

@pytest.fixture
def api_client():
    """기본 API 클라이언트 (인증 없음)"""
    return APIClient()


@pytest.fixture
def authenticated_client(test_user):
    """인증된 API 클라이언트 (기본 사용자)"""
    client, user, token = create_authenticated_client(user=test_user)
    return client


@pytest.fixture
def admin_client(admin_user):
    """관리자 인증 API 클라이언트"""
    client, user, token = create_authenticated_client(user=admin_user)
    return client


@pytest.fixture
def operator_client(operator_user):
    """작업자 인증 API 클라이언트"""
    client, user, token = create_authenticated_client(user=operator_user)
    return client


# ================================
# HACCP Fixtures
# ================================

@pytest.fixture
def test_ccp():
    """기본 테스트 CCP"""
    return create_test_ccp()


@pytest.fixture
def temperature_ccp():
    """온도 관리점"""
    return create_test_ccp(
        name='Temperature Control',
        description='냉장고 온도 관리',
        critical_limit_min=0.0,
        critical_limit_max=4.0
    )


@pytest.fixture
def test_ccp_log(test_ccp, operator_user):
    """기본 테스트 CCP 로그"""
    return create_test_ccp_log(ccp=test_ccp, recorded_by=operator_user)


# ================================
# Supplier Fixtures
# ================================

@pytest.fixture
def test_supplier():
    """기본 테스트 공급업체"""
    return create_test_supplier()


@pytest.fixture
def approved_supplier():
    """승인된 공급업체"""
    return create_test_supplier(
        name='승인된 공급업체',
        is_approved=True,
        quality_rating='A'
    )


@pytest.fixture
def unapproved_supplier():
    """승인되지 않은 공급업체"""
    return create_test_supplier(
        name='미승인 공급업체',
        is_approved=False,
        quality_rating='N/A'
    )


# ================================
# Database Fixtures
# ================================

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """모든 테스트에서 데이터베이스 접근 허용"""
    pass


# ================================
# Parametrized Fixtures
# ================================

@pytest.fixture(params=['admin', 'quality_manager', 'operator'])
def user_with_role(request):
    """다양한 역할의 사용자 (parametrized)"""
    role = request.param
    return create_test_user(role=role)


@pytest.fixture(params=['A+', 'A', 'B', 'C'])
def supplier_with_rating(request):
    """다양한 등급의 공급업체 (parametrized)"""
    from core.tests.helpers.supplier_helpers import create_supplier_with_rating
    rating = request.param
    return create_supplier_with_rating(rating=rating)