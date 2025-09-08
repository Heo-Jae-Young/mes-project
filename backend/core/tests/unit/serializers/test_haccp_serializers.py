"""HACCP 시리얼라이저 단위 테스트"""

import pytest
from datetime import datetime, timedelta, timezone as dt_timezone
from decimal import Decimal
from unittest.mock import patch
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from core.models import CCPLog
from core.serializers.haccp_serializers import (
    CCPSerializer,
    CCPCreateSerializer,
    CCPLogCreateSerializer,
    CCPLogUpdateSerializer,
)


# CCPCreateSerializer에 필요한 완전한 기본 데이터
def get_full_ccp_data(product_id=None):
    base_data = {
        "name": "Test CCP",
        "code": "TEST_CCP_001",
        "ccp_type": "temperature",
        "description": "Test description",
        "process_step": "Test process step",
        "monitoring_frequency": "hourly",
        "corrective_action": "Test corrective action",
        "responsible_person": "Test person",
        "monitoring_method": "Test monitoring method",
        "verification_method": "Test verification method",
        "record_keeping": "Test record keeping",
        "is_active": True,
    }
    if product_id:
        base_data["finished_product_id"] = str(product_id)
    return base_data


@pytest.mark.unit
@pytest.mark.django_db
class TestCCPSerializer:
    """CCPSerializer 테스트"""

    def test_ccp_serialization_basic_fields(self, test_ccp, test_user, test_product):
        test_ccp.created_by = test_user
        test_ccp.finished_product = test_product
        test_ccp.save()
        serializer = CCPSerializer(test_ccp)
        data = serializer.data
        assert data["id"] == str(test_ccp.id)
        assert data["created_by"]["id"] == test_user.id

    @patch("django.utils.timezone.now")
    def test_ccp_statistics_calculation_with_logs(
        self, mock_now, test_ccp, test_production_order, test_user
    ):
        """로그가 있는 CCP 통계 계산 테스트 (시간 고정)"""
        fixed_now = datetime(2025, 9, 8, 12, 0, 0, tzinfo=dt_timezone.utc)
        mock_now.return_value = fixed_now

        # 30일 내 로그 4개 (정상 2, 이탈 2), 30일 전 로그 1개
        CCPLog.objects.create(
            ccp=test_ccp,
            production_order=test_production_order,
            measured_value=Decimal("5.0"),
            measured_at=fixed_now - timedelta(days=29),
            created_by=test_user,
        )
        CCPLog.objects.create(
            ccp=test_ccp,
            production_order=test_production_order,
            measured_value=Decimal("10.0"),
            measured_at=fixed_now - timedelta(days=15),
            created_by=test_user,
        )
        CCPLog.objects.create(
            ccp=test_ccp,
            production_order=test_production_order,
            measured_value=Decimal("3.0"),
            measured_at=fixed_now - timedelta(days=5),
            created_by=test_user,
        )
        CCPLog.objects.create(
            ccp=test_ccp,
            production_order=test_production_order,
            measured_value=Decimal("12.0"),
            measured_at=fixed_now - timedelta(days=5),
            created_by=test_user,
        )
        CCPLog.objects.create(
            ccp=test_ccp,
            production_order=test_production_order,
            measured_value=Decimal("4.0"),
            measured_at=fixed_now - timedelta(days=35),
            created_by=test_user,
        )

        serializer = CCPSerializer(test_ccp)
        data = serializer.data

        assert data["total_logs"] == 5
        assert data["out_of_limits_count"] == 2
        assert data["compliance_rate"] == 50.0


@pytest.mark.unit
@pytest.mark.django_db
class TestCCPCreateSerializer:
    """CCPCreateSerializer 테스트"""

    def test_valid_ccp_creation(self, test_product, test_user):
        data = get_full_ccp_data(test_product.id)
        data.update(
            {
                "code": "NEW_TEMP_001",
                "critical_limit_min": 72.0,
                "critical_limit_max": 75.0,
            }
        )

        factory = APIRequestFactory()
        request = factory.post("/ccps/")
        request.user = test_user

        serializer = CCPCreateSerializer(data=data, context={"request": request})
        assert serializer.is_valid(), serializer.errors
        ccp = serializer.save()
        assert ccp.name == "Test CCP"
        assert ccp.created_by == test_user

    def test_duplicate_code_validation(self, test_ccp, test_product):
        data = get_full_ccp_data(test_product.id)
        data["code"] = test_ccp.code
        serializer = CCPCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "code" in serializer.errors
        assert "unique" in [e.code for e in serializer.errors["code"]]

    def test_numeric_type_limit_validation_failure(self, test_product):
        data = get_full_ccp_data(test_product.id)
        data.update(
            {
                "code": "TEMP_NO_LIMITS",
                "critical_limit_min": None,
                "critical_limit_max": None,
            }
        )
        serializer = CCPCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "최소값 또는 최대값 중 하나는 설정해야 합니다" in str(serializer.errors)

    def test_limit_range_validation(self, test_product):
        data = get_full_ccp_data(test_product.id)
        data.update(
            {
                "code": "INVALID_RANGE",
                "critical_limit_min": 10.0,
                "critical_limit_max": 5.0,
            }
        )
        serializer = CCPCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "critical_limit_min" in serializer.errors

    def test_created_by_auto_assignment(self, test_user, test_product):
        factory = APIRequestFactory()
        request = factory.post("/ccps/")
        request.user = test_user
        data = get_full_ccp_data(test_product.id)
        data.update({"code": "CB_TEST_001", "ccp_type": "visual"})
        serializer = CCPCreateSerializer(data=data, context={"request": request})
        assert serializer.is_valid(), serializer.errors
        ccp = serializer.save()
        assert ccp.created_by == test_user


@pytest.mark.unit
@pytest.mark.django_db
class TestCCPLogCreateSerializer:
    """CCPLogCreateSerializer 테스트"""

    def test_valid_ccp_log_creation(self, test_ccp, test_production_order, test_user):
        data = {
            "ccp_id": str(test_ccp.id),
            "production_order_id": str(test_production_order.id),
            "measured_value": "15.5",
            "unit": "C",
            "measured_at": timezone.now().isoformat(),
        }
        factory = APIRequestFactory()
        request = factory.post("/ccp-logs/")
        request.user = test_user
        serializer = CCPLogCreateSerializer(data=data, context={"request": request})
        assert serializer.is_valid(), serializer.errors
        log = serializer.save()
        assert log.created_by == test_user

    def test_missing_measured_value_validation(self, test_ccp):
        data = {"ccp_id": str(test_ccp.id), "measured_value": None, "unit": "C"}
        serializer = CCPLogCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "measured_value" in serializer.errors
        assert "null" in [e.code for e in serializer.errors["measured_value"]]

    def test_future_measurement_time_validation(self, test_ccp):
        future_time = timezone.now() + timedelta(hours=1)
        data = {
            "ccp_id": str(test_ccp.id),
            "measured_value": "10.0",
            "unit": "C",
            "measured_at": future_time.isoformat(),
        }
        serializer = CCPLogCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "measured_at" in serializer.errors


@pytest.mark.unit
@pytest.mark.django_db
class TestCCPLogUpdateSerializer:
    """CCPLogUpdateSerializer 테스트"""

    def test_valid_corrective_action_update(
        self, test_ccp, test_production_order, test_user
    ):
        log = CCPLog.objects.create(
            ccp=test_ccp,
            production_order=test_production_order,
            measured_value=Decimal("15.0"),
            unit="C",
            measured_at=timezone.now(),
            created_by=test_user,
        )
        data = {
            "corrective_action_taken": "온도 조절 후 재측정 완료",
            "corrective_action_by_id": test_user.id,
            "verified_by_id": test_user.id,
            "verification_date": timezone.now().isoformat(),
        }
        serializer = CCPLogUpdateSerializer(log, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors
        updated_log = serializer.save()
        assert updated_log.status == "corrective_action"
