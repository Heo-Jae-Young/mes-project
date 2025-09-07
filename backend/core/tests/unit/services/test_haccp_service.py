import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError, PermissionDenied

from core.services.haccp_service import HaccpService, HaccpQueryService
from core.models import CCP, CCPLog, ProductionOrder, FinishedProduct
from core.constants import (
    DUPLICATE_MEASUREMENT_THRESHOLD_MINUTES,
    VERIFICATION_REQUIRED_HOURS,
    CRITICAL_ALERT_HOURS,
    CONSECUTIVE_VIOLATION_DETECTION_HOURS,
    CONSECUTIVE_VIOLATION_THRESHOLD
)

User = get_user_model()


@pytest.mark.unit
@pytest.mark.django_db
class TestHaccpService:
    """HACCP Service 단위 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.haccp_service = HaccpService()
        self.current_time = timezone.now()
        
        # Test Users
        self.admin_user = User.objects.create_user(
            username='admin_test',
            password='test123',
            role='admin'
        )
        self.quality_manager = User.objects.create_user(
            username='quality_test',
            password='test123',
            role='quality_manager'
        )
        self.operator = User.objects.create_user(
            username='operator_test',
            password='test123',
            role='operator'
        )
        self.viewer = User.objects.create_user(
            username='viewer_test',
            password='test123',
            role='viewer'
        )
        
        # Test CCP
        self.test_ccp = CCP.objects.create(
            code='CCP-001',
            name='냉장고 온도',
            ccp_type='temperature',
            description='냉장고 온도 관리',
            process_step='보관',
            critical_limit_min=Decimal('2.0'),
            critical_limit_max=Decimal('8.0'),
            monitoring_frequency='매 30분',
            corrective_action='온도 조절',
            responsible_person='operator_test',
            monitoring_method='온도계 측정',
            verification_method='일일 확인',
            record_keeping='로그 기록',
            is_active=True,
            created_by=self.admin_user
        )
        
        # Test Product and Production Order
        self.test_product = FinishedProduct.objects.create(
            code='PROD-001',
            name='테스트 제품',
            description='테스트용 완제품',
            version='1.0',
            shelf_life_days=30,
            net_weight=Decimal('1.000'),
            packaging_type='박스',
            is_active=True,
            created_by=self.admin_user
        )
        
        self.test_order = ProductionOrder.objects.create(
            order_number='ORD-001',
            finished_product=self.test_product,
            planned_quantity=Decimal('100'),
            planned_start_date=self.current_time,
            planned_end_date=self.current_time + timedelta(hours=8),
            status='planned',
            priority='normal',
            created_by=self.admin_user
        )

    def test_validate_ccp_log_creation_success(self):
        """정상적인 CCP 로그 생성 검증 테스트"""
        measured_value = Decimal('5.0')  # 정상 범위
        measured_at = self.current_time - timedelta(minutes=30)
        
        result_ccp = self.haccp_service.validate_ccp_log_creation(
            ccp_id=self.test_ccp.id,
            measured_value=measured_value,
            measured_at=measured_at,
            created_by=self.operator
        )
        
        assert result_ccp == self.test_ccp
        assert result_ccp.is_active is True

    def test_validate_ccp_log_creation_inactive_ccp(self):
        """비활성 CCP에 대한 검증 실패 테스트"""
        self.test_ccp.is_active = False
        self.test_ccp.save()
        
        with pytest.raises(ValidationError, match='존재하지 않거나 비활성화된 CCP입니다'):
            self.haccp_service.validate_ccp_log_creation(
                ccp_id=self.test_ccp.id,
                measured_value=Decimal('5.0'),
                measured_at=self.current_time - timedelta(minutes=30),
                created_by=self.operator
            )

    def test_validate_ccp_log_creation_permission_denied(self):
        """권한 없는 사용자의 CCP 로그 생성 시도 테스트"""
        with pytest.raises(PermissionDenied, match='CCP 로그 기록 권한이 없습니다'):
            self.haccp_service.validate_ccp_log_creation(
                ccp_id=self.test_ccp.id,
                measured_value=Decimal('5.0'),
                measured_at=self.current_time - timedelta(minutes=30),
                created_by=self.viewer
            )

    def test_validate_ccp_log_creation_future_time(self):
        """미래 시점 측정 시간 검증 실패 테스트"""
        future_time = self.current_time + timedelta(hours=1)
        
        with pytest.raises(ValidationError, match='미래 시점의 측정 시간은 입력할 수 없습니다'):
            self.haccp_service.validate_ccp_log_creation(
                ccp_id=self.test_ccp.id,
                measured_value=Decimal('5.0'),
                measured_at=future_time,
                created_by=self.operator
            )

    def test_validate_ccp_log_creation_duplicate_measurement(self):
        """중복 측정 방지 테스트"""
        measured_at = self.current_time - timedelta(minutes=30)
        
        # 기존 로그 생성
        CCPLog.objects.create(
            ccp=self.test_ccp,
            measured_value=Decimal('5.0'),
            unit='°C',
            measured_at=measured_at,
            status='within_limits',
            is_within_limits=True,
            created_by=self.operator,
            production_order=self.test_order
        )
        
        # 같은 시간대 중복 측정 시도
        duplicate_time = measured_at + timedelta(minutes=DUPLICATE_MEASUREMENT_THRESHOLD_MINUTES - 1)
        
        with pytest.raises(ValidationError, match='동일 시간대에 이미 측정 기록이 존재합니다'):
            self.haccp_service.validate_ccp_log_creation(
                ccp_id=self.test_ccp.id,
                measured_value=Decimal('6.0'),
                measured_at=duplicate_time,
                created_by=self.operator
            )

    def test_calculate_compliance_score_no_logs(self):
        """로그가 없는 경우 컴플라이언스 점수 계산"""
        result = self.haccp_service.calculate_compliance_score()
        
        expected = {
            'compliance_score': 100,
            'total_measurements': 0,
            'within_limits_count': 0,
            'out_of_limits_count': 0,
            'verification_rate': 0
        }
        
        assert result == expected

    def test_calculate_compliance_score_with_logs(self):
        """로그가 있는 경우 컴플라이언스 점수 계산"""
        # 정상 측정값 로그 3개
        for i in range(3):
            CCPLog.objects.create(
                ccp=self.test_ccp,
                measured_value=Decimal('5.0'),
                unit='°C',
                measured_at=self.current_time - timedelta(hours=i),
                status='within_limits',
                is_within_limits=True,
                verified_by=self.quality_manager,
                created_by=self.operator,
                production_order=self.test_order
            )
        
        # 이탈 측정값 로그 1개 (검증 안됨)
        CCPLog.objects.create(
            ccp=self.test_ccp,
            measured_value=Decimal('10.0'),
            unit='°C',
            measured_at=self.current_time - timedelta(hours=4),
            status='out_of_limits',
            is_within_limits=False,
            created_by=self.operator,
            production_order=self.test_order
        )
        
        result = self.haccp_service.calculate_compliance_score()
        
        # 총 4개 로그, 3개 정상, 1개 이탈
        # 컴플라이언스율: 75%, 검증률: 75% (3/4)
        # 가중점수: 75 * 0.7 + 75 * 0.3 = 75
        assert result['compliance_score'] == 75.0
        assert result['total_measurements'] == 4
        assert result['within_limits_count'] == 3
        assert result['out_of_limits_count'] == 1
        assert result['compliance_rate'] == 75.0
        assert result['verification_rate'] == 75.0

    def test_calculate_compliance_score_with_filters(self):
        """필터를 적용한 컴플라이언스 점수 계산"""
        # 다른 CCP 로그 생성 (필터링될 것)
        other_ccp = CCP.objects.create(
            code='CCP-002',
            name='다른 CCP',
            ccp_type='ph',
            description='pH 관리',
            process_step='처리',
            critical_limit_min=Decimal('6.0'),
            critical_limit_max=Decimal('7.0'),
            monitoring_frequency='매 60분',
            corrective_action='pH 조절',
            responsible_person='operator_test',
            monitoring_method='pH미터 측정',
            verification_method='일일 점검',
            record_keeping='수기 기록',
            is_active=True,
            created_by=self.admin_user
        )
        
        CCPLog.objects.create(
            ccp=other_ccp,
            measured_value=Decimal('6.5'),
            measured_at=self.current_time - timedelta(hours=1),
            is_within_limits=True,
            created_by=self.operator,
            production_order=self.test_order
        )
        
        # 대상 CCP 로그 생성
        CCPLog.objects.create(
            ccp=self.test_ccp,
            measured_value=Decimal('5.0'),
            measured_at=self.current_time - timedelta(hours=1),
            is_within_limits=True,
            verified_by=self.quality_manager,
            created_by=self.operator,
            production_order=self.test_order
        )
        
        # 특정 CCP만 필터링하여 계산
        result = self.haccp_service.calculate_compliance_score(ccp=self.test_ccp)
        
        assert result['total_measurements'] == 1
        assert result['within_limits_count'] == 1
        assert result['compliance_score'] == 100.0

    def test_get_critical_alerts_permission_denied(self):
        """권한 없는 사용자의 중요 알림 조회 시도"""
        with pytest.raises(PermissionDenied, match='중요 알림 조회 권한이 없습니다'):
            self.haccp_service.get_critical_alerts(user=self.operator)

    def test_get_critical_alerts_deviation_unresolved(self):
        """미해결 기준 이탈에 대한 중요 알림 테스트"""
        # 미해결 기준 이탈 로그 생성
        deviation_log = CCPLog.objects.create(
            ccp=self.test_ccp,
            measured_value=Decimal('15.0'),  # 기준 초과
            measured_at=self.current_time - timedelta(hours=2),
            is_within_limits=False,
            corrective_action_taken='',  # 개선조치 미실시
            created_by=self.operator,
            production_order=self.test_order
        )
        
        result = self.haccp_service.get_critical_alerts(user=self.admin_user)
        
        assert result['total_alerts'] == 1
        deviation_alert = result['critical_alerts'][0]
        assert deviation_alert['type'] == 'deviation'
        assert deviation_alert['severity'] == 'high'
        assert '기준 이탈 - 개선조치 필요' in deviation_alert['message']
        assert deviation_alert['ccp_code'] == self.test_ccp.code

    def test_get_critical_alerts_verification_pending(self):
        """검증 대기 항목에 대한 중요 알림 테스트"""
        # 검증 시간이 경과한 로그 생성
        old_log = CCPLog.objects.create(
            ccp=self.test_ccp,
            measured_value=Decimal('5.0'),
            measured_at=self.current_time - timedelta(hours=VERIFICATION_REQUIRED_HOURS + 1),
            is_within_limits=True,
            verified_by=None,  # 미검증
            created_by=self.operator,
            production_order=self.test_order
        )
        
        result = self.haccp_service.get_critical_alerts(user=self.quality_manager)
        
        assert result['total_alerts'] == 1
        verification_alert = result['critical_alerts'][0]
        assert verification_alert['type'] == 'verification_pending'
        assert verification_alert['severity'] == 'medium'
        assert '검증 대기 중' in verification_alert['message']

    def test_get_critical_alerts_consecutive_deviation(self):
        """연속 기준 이탈 패턴에 대한 중요 알림 테스트"""
        # 연속 이탈 로그 생성 (임계값 이상)
        for i in range(CONSECUTIVE_VIOLATION_THRESHOLD):
            CCPLog.objects.create(
                ccp=self.test_ccp,
                measured_value=Decimal('15.0'),  # 기준 초과
                unit='°C',
                measured_at=self.current_time - timedelta(hours=i),
                status='out_of_limits',
                is_within_limits=False,
                created_by=self.operator,
                production_order=self.test_order
            )
        
        result = self.haccp_service.get_critical_alerts(user=self.admin_user)
        
        consecutive_alerts = [alert for alert in result['critical_alerts'] 
                            if alert['type'] == 'consecutive_deviation']
        assert len(consecutive_alerts) == 1
        
        consecutive_alert = consecutive_alerts[0]
        assert consecutive_alert['severity'] == 'critical'
        assert f'연속 {CONSECUTIVE_VIOLATION_THRESHOLD}회 기준 이탈' in consecutive_alert['message']

    def test_generate_compliance_report_permission_denied(self):
        """권한 없는 사용자의 컴플라이언스 보고서 생성 시도"""
        date_from = self.current_time.date() - timedelta(days=7)
        date_to = self.current_time.date()
        
        with pytest.raises(PermissionDenied, match='컴플라이언스 보고서 생성 권한이 없습니다'):
            self.haccp_service.generate_compliance_report(
                date_from=date_from,
                date_to=date_to,
                user=self.operator
            )

    def test_generate_compliance_report_success(self):
        """정상적인 컴플라이언스 보고서 생성 테스트"""
        date_from = self.current_time.date() - timedelta(days=7)
        date_to = self.current_time.date()
        
        # 테스트 로그 생성
        CCPLog.objects.create(
            ccp=self.test_ccp,
            measured_value=Decimal('5.0'),
            measured_at=self.current_time - timedelta(days=3),
            is_within_limits=True,
            verified_by=self.quality_manager,
            created_by=self.operator,
            production_order=self.test_order
        )
        
        result = self.haccp_service.generate_compliance_report(
            date_from=date_from,
            date_to=date_to,
            user=self.admin_user
        )
        
        assert 'report_period' in result
        assert 'overall_statistics' in result
        assert 'ccp_statistics' in result
        assert 'trend_analysis' in result
        assert result['generated_by'] == self.admin_user.username
        
        # CCP 통계 검증
        ccp_stat = result['ccp_statistics'][0]
        assert ccp_stat['ccp_code'] == self.test_ccp.code
        assert ccp_stat['ccp_name'] == self.test_ccp.name
        assert ccp_stat['total_measurements'] == 1


@pytest.mark.unit
@pytest.mark.django_db 
class TestHaccpQueryService:
    """HACCP Query Service 단위 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.query_service = HaccpQueryService()
        
        # Test Users
        self.admin_user = User.objects.create_user(
            username='admin_query',
            password='test123',
            role='admin'
        )
        self.operator = User.objects.create_user(
            username='operator_query',
            password='test123',
            role='operator'
        )
        self.viewer = User.objects.create_user(
            username='viewer_query',
            password='test123',
            role='viewer'
        )
        
        # Test CCP
        self.test_ccp = CCP.objects.create(
            code='CCP-QUERY',
            name='쿼리 테스트 CCP',
            ccp_type='temperature',
            description='쿼리 테스트용 CCP',
            process_step='테스트',
            critical_limit_min=Decimal('0.0'),
            critical_limit_max=Decimal('10.0'),
            monitoring_frequency='매 10분',
            corrective_action='조치 실행',
            responsible_person='operator_query',
            monitoring_method='자동 측정',
            verification_method='시스템 확인',
            record_keeping='데이터베이스 로그',
            is_active=True,
            created_by=self.admin_user
        )

    def test_get_ccp_logs_for_operator(self):
        """운영자 역할의 CCP 로그 조회 테스트"""
        # 운영자가 생성한 로그
        operator_log = CCPLog.objects.create(
            ccp=self.test_ccp,
            measured_value=Decimal('5.0'),
            measured_at=timezone.now(),
            is_within_limits=True,
            created_by=self.operator
        )
        
        # 다른 사용자가 생성한 로그
        CCPLog.objects.create(
            ccp=self.test_ccp,
            measured_value=Decimal('6.0'),
            measured_at=timezone.now(),
            is_within_limits=True,
            created_by=self.admin_user
        )
        
        result = self.query_service.get_ccp_logs_for_user(user=self.operator)
        
        assert result.count() == 1
        assert result.first() == operator_log

    def test_get_ccp_logs_for_admin(self):
        """관리자 역할의 CCP 로그 조회 테스트 (모든 로그 접근 가능)"""
        CCPLog.objects.create(
            ccp=self.test_ccp,
            measured_value=Decimal('5.0'),
            unit='°C',
            measured_at=timezone.now(),
            status='within_limits',
            is_within_limits=True,
            created_by=self.operator
        )
        
        CCPLog.objects.create(
            ccp=self.test_ccp,
            measured_value=Decimal('6.0'),
            measured_at=timezone.now(),
            is_within_limits=True,
            created_by=self.admin_user
        )
        
        result = self.query_service.get_ccp_logs_for_user(user=self.admin_user)
        
        assert result.count() == 2

    def test_get_ccp_logs_for_unauthorized_user(self):
        """권한 없는 사용자의 CCP 로그 조회 테스트"""
        CCPLog.objects.create(
            ccp=self.test_ccp,
            measured_value=Decimal('5.0'),
            unit='°C',
            measured_at=timezone.now(),
            status='within_limits',
            is_within_limits=True,
            created_by=self.operator
        )
        
        result = self.query_service.get_ccp_logs_for_user(user=self.viewer)
        
        assert result.count() == 0

    def test_get_ccps_for_operator_with_responsibility(self):
        """담당자로 지정된 운영자의 CCP 조회 테스트"""
        result = self.query_service.get_ccps_for_user(user=self.operator)
        
        assert result.count() == 1
        assert result.first() == self.test_ccp

    def test_get_ccps_for_operator_without_responsibility(self):
        """담당자가 아닌 운영자의 CCP 조회 테스트"""
        other_operator = User.objects.create_user(
            username='other_operator',
            password='test123',
            role='operator'
        )
        
        result = self.query_service.get_ccps_for_user(user=other_operator)
        
        assert result.count() == 0

    def test_get_ccps_for_admin(self):
        """관리자의 CCP 조회 테스트 (모든 활성 CCP 접근 가능)"""
        result = self.query_service.get_ccps_for_user(user=self.admin_user)
        
        assert result.count() == 1
        assert result.first() == self.test_ccp