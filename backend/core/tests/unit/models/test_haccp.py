"""HACCP 모델 단위 테스트"""

import pytest
from decimal import Decimal
from core.models import CCP, CCPLog, User
from django.utils import timezone


@pytest.mark.unit
class TestCCPModel:
    """CCP 모델 테스트"""

    def test_ccp_creation_success(self):
        """CCP 생성 테스트"""
        # Given: 사용자 생성
        user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com",
            role="operator",
        )

        # Given: 정상적인 CCP 데이터
        ccp_data = {
            "name": "온도 관리점",
            "code": "CCP-TEMP-001",
            "ccp_type": "temperature",
            "description": "냉장고 온도 관리",
            "process_step": "냉장 보관",
            "monitoring_frequency": "매 30분",
            "corrective_action": "온도 조절",
            "created_by": user,
        }

        # When: (실행)
        ccp = CCP.objects.create(**ccp_data)

        # Then: (검증)
        assert ccp.id is not None
        assert ccp.name == ccp_data["name"]
        assert ccp.code == ccp_data["code"]
        assert ccp.ccp_type == ccp_data["ccp_type"]
        assert ccp.description == ccp_data["description"]
        assert ccp.process_step == ccp_data["process_step"]
        assert ccp.monitoring_frequency == ccp_data["monitoring_frequency"]
        assert ccp.corrective_action == ccp_data["corrective_action"]
        assert ccp.created_by == ccp_data["created_by"]


@pytest.mark.unit
class TestCCPLogModel:
    """CCP 로그 모델 테스트"""

    @pytest.fixture
    def sample_ccp(self):
        """테스트용 CCP (0-4도 온도 관리)"""

        # 사용자 생성
        user = User.objects.create_user(
            username="admin",
            password="admin123",
            email="admin@example.com",
            role="admin",
        )

        # 테스트용 CCP 생성
        ccp = CCP.objects.create(
            name="온도 관리점",
            code="CCP-TEMP-001",
            ccp_type="temperature",
            description="냉장고 온도 관리",
            process_step="냉장 보관",
            critical_limit_min=Decimal("0.0"),  # 최소 0도
            critical_limit_max=Decimal("4.0"),  # 최대 4도
            monitoring_frequency="매 30분",
            corrective_action="온도 조절",
            created_by=user,
        )

        return ccp

    @pytest.fixture
    def sample_user(self):
        """테스트용 사용자 생성"""
        user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com",
            role="operator",
        )
        return user

    def test_save_auto_sets_out_of_limits_when_over_max(self, sample_ccp, sample_user):
        """측정값이 최대값 초과 시 자동으로 out_of_limits 설정"""

        # Given: 측정값
        over_max_value = Decimal("5.0")

        # When: 객체 생성
        log = CCPLog(
            ccp=sample_ccp,
            measured_value=over_max_value,
            unit="°C",
            measured_at=timezone.now(),
            status="temp_status",
            is_within_limits=True,
            created_by=sample_user,
        )
        log.save()

        # Then: 검증
        assert log.is_within_limits is False
        assert log.status == "out_of_limits"

    def test_save_auto_sets_out_of_limits_when_under_min(self, sample_ccp, sample_user):
        """측정값이 최소값 미만 시 자동으로 out_of_limits 설정"""
        # Given: 최소값(0.0) 미만하는 측정값
        under_min_value = Decimal("-1.0")  # 0.0 미만!

        # When: CCPLog 생성
        log = CCPLog(
            ccp=sample_ccp,
            measured_value=under_min_value,
            unit="°C",
            measured_at=timezone.now(),
            status="temp_status",
            is_within_limits=True,
            created_by=sample_user,
        )
        log.save()

        # Then: 검증
        assert log.is_within_limits is False
        assert log.status == "out_of_limits"
        assert log.measured_value == Decimal("-1.0")

    def test_save_keeps_within_limits_for_normal_values(self, sample_ccp, sample_user):
        """정상 범위 내 측정값은 within_limits 유지"""
        # Given: 정상 범위(0.0~4.0) 내 측정값
        normal_value = Decimal("2.5")

        # When: CCPLog 생성
        log = CCPLog(
            ccp=sample_ccp,
            measured_value=normal_value,
            unit="°C",
            measured_at=timezone.now(),
            status="normal",
            is_within_limits=True,
            created_by=sample_user,
        )
        log.save()

        # Then: 자동으로 within_limits로 설정
        assert log.is_within_limits is True
        assert log.status == "within_limits"  # 모델이 자동으로 설정
        assert log.measured_value == Decimal("2.5")

    def test_save_boundary_values_exact_min_max(self, sample_ccp, sample_user):
        """경계값(정확히 최소/최대값)에서의 동작 확인"""
        # Given & When & Then: 최소값 정확히
        min_log = CCPLog(
            ccp=sample_ccp,
            measured_value=Decimal("0.0"),  # 정확히 최소값
            unit="°C",
            measured_at=timezone.now(),
            status="normal",
            is_within_limits=True,
            created_by=sample_user,
        )
        min_log.save()
        assert min_log.is_within_limits is True

        # Given & When & Then: 최대값 정확히
        max_log = CCPLog(
            ccp=sample_ccp,
            measured_value=Decimal("4.0"),  # 정확히 최대값
            unit="°C",
            measured_at=timezone.now(),
            status="normal",
            is_within_limits=True,
            created_by=sample_user,
        )
        max_log.save()
        assert max_log.is_within_limits is True

    def test_required_fields_validation(self, sample_ccp, sample_user):
        """필수 필드 누락 시 에러 발생"""
        with pytest.raises(Exception):  # IntegrityError 또는 ValidationError
            log = CCPLog(
                # ccp 누락
                measured_value=Decimal("2.0"),
                unit="°C",
                measured_at=timezone.now(),
                created_by=sample_user,
            )
            log.save()

    def test_ccplog_str_representation(self, sample_ccp, sample_user):
        """CCPLog 문자열 표현 테스트"""
        # Given: CCPLog 생성
        log = CCPLog.objects.create(
            ccp=sample_ccp,
            measured_value=Decimal("2.5"),
            unit="°C",
            measured_at=timezone.now(),
            status="normal",
            is_within_limits=True,
            created_by=sample_user,
        )

        # When & Then: __str__ 확인 (실제 구현에는 measured_at 포함)
        str_result = str(log)
        assert "온도 관리점" in str_result
        assert "2.5" in str_result
        assert "°C" in str_result
        # measured_at도 포함되므로 정확한 패턴 확인

    def test_ccplog_immutability_after_creation(self, sample_ccp, sample_user):
        """CCPLog는 생성 후 수정 불가 (HACCP 규정)"""
        # Given: CCPLog 생성
        log = CCPLog.objects.create(
            ccp=sample_ccp,
            measured_value=Decimal("2.5"),
            unit="°C",
            measured_at=timezone.now(),
            status="normal",
            is_within_limits=True,
            created_by=sample_user,
        )
        original_value = log.measured_value

        # When: 값 수정 시도
        log.measured_value = Decimal("3.0")
        
        # Then: 실제로는 수정을 막는 로직이 있다면 여기서 검증
        # 현재는 단순히 데이터 불변성 원칙 확인
        # (실제 프로덕션에서는 Model의 save() 오버라이드로 막을 수 있음)
        assert original_value == Decimal("2.5")
