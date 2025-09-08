import pytest
from rest_framework.test import APIRequestFactory
from django.utils import timezone
from core.models import CCP, CCPLog
from core.serializers.haccp_serializers import (
    CCPSerializer,
    CCPCreateSerializer,
    CCPLogCreateSerializer,
    CCPLogUpdateSerializer,
)
from decimal import Decimal
from datetime import timedelta


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


@pytest.mark.integration
@pytest.mark.django_db
class TestHACCPSerializersIntegration:
    """HACCP 시리얼라이저 통합 테스트"""

    def test_ccp_create_and_log_workflow(
        self, test_user, test_product, test_production_order
    ):
        factory = APIRequestFactory()
        request = factory.post("/ccps/")
        request.user = test_user

        ccp_data = get_full_ccp_data(test_product.id)
        ccp_data.update(
            {
                "code": "INT_TEST_001",
                "critical_limit_min": 70.0,
                "critical_limit_max": 75.0,
            }
        )

        ccp_serializer = CCPCreateSerializer(
            data=ccp_data, context={"request": request}
        )
        assert ccp_serializer.is_valid(), ccp_serializer.errors
        ccp = ccp_serializer.save()

        log_data = {
            "ccp_id": str(ccp.id),
            "production_order_id": str(test_production_order.id),
            "measured_value": "78.0",
            "unit": "C",
            "measured_at": timezone.now().isoformat(),
        }
        log_serializer = CCPLogCreateSerializer(
            data=log_data, context={"request": request}
        )
        assert log_serializer.is_valid(), log_serializer.errors
        log = log_serializer.save()

        update_data = {
            "corrective_action_taken": "Heater adjusted",
            "corrective_action_by_id": test_user.id,
        }
        update_serializer = CCPLogUpdateSerializer(log, data=update_data, partial=True)
        assert update_serializer.is_valid(), update_serializer.errors
        updated_log = update_serializer.save()

        ccp.refresh_from_db()
        ccp_read_serializer = CCPSerializer(ccp)
        assert ccp_read_serializer.data["compliance_rate"] == 0.0

    def test_multiple_ccps_logs_statistics(
        self, test_user, test_product, test_production_order
    ):
        factory = APIRequestFactory()
        request = factory.post("/ccps/")
        request.user = test_user

        ccp_data = get_full_ccp_data(test_product.id)
        ccp_data.update(
            {
                "code": "STAT_001",
                "ccp_type": "ph",
                "critical_limit_min": 6.0,
                "critical_limit_max": 7.0,
            }
        )

        ccp_serializer = CCPCreateSerializer(
            data=ccp_data, context={"request": request}
        )
        assert ccp_serializer.is_valid(), ccp_serializer.errors
        ccp = ccp_serializer.save()

        log_values = [6.2, 6.5, 6.8, 6.1, 6.9, 6.6, 6.3, 6.7, 5.5, 7.5]
        for i, value in enumerate(log_values):
            CCPLog.objects.create(
                ccp=ccp,
                production_order=test_production_order,
                measured_value=Decimal(str(value)),
                unit="pH",
                measured_at=timezone.now() - timedelta(days=i + 1),
                created_by=test_user,
            )

        serializer = CCPSerializer(ccp)
        data = serializer.data
        assert data["total_logs"] == 10
        assert data["out_of_limits_count"] == 2
        assert data["compliance_rate"] == 80.0
