"""User 모델 관련 테스트 헬퍼 함수들"""
from core.models.user import User


def create_test_user(role='operator', **kwargs):
    """테스트용 사용자 생성"""
    defaults = {
        'username': f'test_{role}',
        'password': 'testpass123',
        'email': f'{role}@test.com',
        'role': role,
        'employee_id': f'TEST_{role.upper()}',
        'department': f'{role} 부서',
        'phone': '010-1234-5678'
    }
    defaults.update(kwargs)
    return User.objects.create_user(**defaults)


def create_admin_user(**kwargs):
    """관리자 사용자 생성"""
    defaults = {
        'username': 'test_admin',
        'employee_id': 'ADMIN001',
        'department': '관리팀'
    }
    defaults.update(kwargs)
    return create_test_user(role='admin', **defaults)


def create_quality_manager(**kwargs):
    """품질관리자 사용자 생성"""
    defaults = {
        'username': 'test_quality',
        'employee_id': 'QM001', 
        'department': '품질관리팀'
    }
    defaults.update(kwargs)
    return create_test_user(role='quality_manager', **defaults)


def create_operator(**kwargs):
    """작업자 사용자 생성"""
    defaults = {
        'username': 'test_operator',
        'employee_id': 'OP001',
        'department': '생산팀'
    }
    defaults.update(kwargs)
    return create_test_user(role='operator', **defaults)


def create_users_batch(count=5, role='operator', **kwargs):
    """여러 사용자 일괄 생성"""
    users = []
    for i in range(count):
        user_kwargs = kwargs.copy()
        user_kwargs.update({
            'username': f'test_{role}_{i+1}',
            'employee_id': f'TEST_{role.upper()}_{i+1:03d}'
        })
        users.append(create_test_user(role=role, **user_kwargs))
    return users