"""
HACCP 시스템 상수 정의
"""

# 시간 관련 설정 (분 단위)
DUPLICATE_MEASUREMENT_THRESHOLD_MINUTES = 1  # 중복 측정 방지 시간 간격
VERIFICATION_REQUIRED_HOURS = 72  # 검증 필요 시간 임계값  
CRITICAL_ALERT_HOURS = 24  # 중요 알림 기본 시간 범위
CONSECUTIVE_VIOLATION_DETECTION_HOURS = 12  # 연속 이탈 패턴 감지 시간 범위

# 연속 이탈 임계값
CONSECUTIVE_VIOLATION_THRESHOLD = 3  # 연속 이탈 알림 기준 횟수

# HACCP 규정 관련
HACCP_STATUS_CHOICES = [
    ('within_limits', '기준 내'),
    ('out_of_limits', '기준 이탈'),
    ('corrective_action', '개선조치'),
]

CCP_TYPE_CHOICES = [
    ('temperature', '온도'),
    ('ph', 'pH'),
    ('time', '시간'),
    ('pressure', '압력'),
    ('visual', '육안검사'),
    ('metal_detection', '금속검출'),
    ('weight', '중량'),
]