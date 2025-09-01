"""User 모델 관련 테스트 헬퍼 함수들"""
from core.models.user import User


def create_test_user(role='operator', **kwargs):
    """테스트용 사용자 생성"""
    import random
    random_num = random.randint(1000, 9999)
    defaults = {
        'username': f'test_{role}_{random_num}',
        'password': 'testpass123',
        'email': f'{role}_{random_num}@test.com',
        'role': role,
        'employee_id': f'TEST_{role.upper()}_{random_num}',
        'department': f'{role} 부서',
        'phone': '010-1234-5678'
    }
    defaults.update(kwargs)
    return User.objects.create_user(**defaults)


def create_admin_user(**kwargs):
    """관리자 사용자 생성"""
    import random
    random_num = random.randint(1000, 9999)
    defaults = {
        'username': f'test_admin_{random_num}',
        'employee_id': f'ADMIN{random_num}',
        'department': '관리팀'
    }
    defaults.update(kwargs)
    return create_test_user(role='admin', **defaults)


def create_quality_manager(**kwargs):
    """품질관리자 사용자 생성"""
    import random
    random_num = random.randint(1000, 9999)
    defaults = {
        'username': f'test_quality_{random_num}',
        'employee_id': f'QM{random_num}',
        'department': '품질관리팀'
    }
    defaults.update(kwargs)
    return create_test_user(role='quality_manager', **defaults)


def create_operator(**kwargs):
    """작업자 사용자 생성"""
    import random
    random_num = random.randint(1000, 9999)
    defaults = {
        'username': f'test_operator_{random_num}',
        'employee_id': f'OP{random_num}',
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