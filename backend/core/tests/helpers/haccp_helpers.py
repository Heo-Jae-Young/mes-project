"""HACCP 관련 모델 테스트 헬퍼 함수들"""
from decimal import Decimal
from datetime import datetime, timezone as tz
from django.utils import timezone
from core.models.haccp import CCP, CCPLog
from .user_helpers import create_test_user


def create_test_ccp(name='Temperature Control', **kwargs):
    """테스트용 CCP 생성"""
    user = kwargs.pop('created_by', None)
    if not user:
        user = create_test_user(role='admin')
    
    import random
    random_num = random.randint(1000, 9999)
    defaults = {
        'name': name,
        'code': f'CCP{random_num}',
        'ccp_type': 'temperature',
        'description': f'{name} 중요관리점',
        'process_step': '냉장 보관 단계',
        'critical_limit_min': Decimal('2.000'),
        'critical_limit_max': Decimal('8.000'),
        'monitoring_frequency': 'hourly',
        'corrective_action': '온도 조절 및 재측정',
        'responsible_person': user.username,
        'monitoring_method': '디지털 온도계 측정',
        'verification_method': '온도계 교정',
        'record_keeping': '온도 기록지 작성',
        'is_active': True,
        'created_by': user
    }
    defaults.update(kwargs)
    return CCP.objects.create(**defaults)


def create_test_ccp_log(ccp=None, created_by=None, **kwargs):
    """테스트용 CCP 로그 생성"""
    if ccp is None:
        ccp = create_test_ccp()
    
    if created_by is None:
        created_by = create_test_user(role='operator')
    
    defaults = {
        'ccp': ccp,
        'measured_value': Decimal('5.500'),
        'unit': 'C',
        'measured_at': timezone.now(),
        'status': 'within_limits',
        'is_within_limits': True,
        'deviation_notes': '',
        'created_by': created_by
    }
    defaults.update(kwargs)
    return CCPLog.objects.create(**defaults)


def create_temperature_ccp(**kwargs):
    """온도 관리점 생성"""
    defaults = {
        'name': 'Temperature Control',
        'description': '냉장고 온도 관리',
        'critical_limit_min': Decimal('0.00'),
        'critical_limit_max': Decimal('4.00'),
        'monitoring_frequency': 'every_2_hours'
    }
    defaults.update(kwargs)
    return create_test_ccp(**defaults)


def create_ph_ccp(**kwargs):
    """pH 관리점 생성"""
    defaults = {
        'name': 'pH Control',
        'description': 'pH 수준 관리',
        'critical_limit_min': Decimal('6.0'),
        'critical_limit_max': Decimal('7.5'),
        'monitoring_frequency': 'daily'
    }
    defaults.update(kwargs)
    return create_test_ccp(**defaults)


def create_out_of_limit_log(ccp=None, **kwargs):
    """한계 기준 초과 로그 생성"""
    if ccp is None:
        ccp = create_test_ccp()
    
    defaults = {
        'measured_value': Decimal('15.000'),  # 한계 초과 값
        'status': 'out_of_limits',
        'is_within_limits': False,
        'corrective_action_taken': '즉시 온도 조절 실시',
        'deviation_notes': '한계 기준 초과로 인한 개선 조치'
    }
    defaults.update(kwargs)
    return create_test_ccp_log(ccp=ccp, **kwargs)


def create_multiple_ccp_logs(ccp, count=10, **kwargs):
    """여러 CCP 로그 생성"""
    logs = []
    for i in range(count):
        log_kwargs = kwargs.copy()
        log_kwargs.update({
            'measured_value': Decimal(f'{4.0 + i * 0.5}'),  # 점진적으로 증가
            'deviation_notes': f'측정 {i+1}번째'
        })
        logs.append(create_test_ccp_log(ccp=ccp, **log_kwargs))
    return logs