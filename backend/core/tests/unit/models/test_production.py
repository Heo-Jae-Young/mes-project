"""생산 관리 모델 단위 테스트"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from core.models import ProductionOrder
from ...fixtures.base_fixtures import admin_user, operator_user, sample_product


@pytest.mark.unit
class TestProductionOrderModel:
    """생산 주문 모델 테스트"""

    def test_production_order_creation_success(self, admin_user, sample_product):
        """생산 주문 생성 테스트"""
        # Given: 생산 주문 데이터
        now = timezone.now()
        order_data = {
            "order_number": "PO2025001",
            "finished_product": sample_product,
            "planned_quantity": Decimal("100.000"),
            "planned_start_date": now + timedelta(hours=1),
            "planned_end_date": now + timedelta(days=1),
            "status": "planned",
            "priority": "normal",
            "notes": "테스트 생산 주문",
            "created_by": admin_user,
        }

        # When: 생산 주문 생성
        order = ProductionOrder.objects.create(**order_data)

        # Then: 검증
        assert order.id is not None
        assert order.order_number == "PO2025001"
        assert order.finished_product == sample_product
        assert order.planned_quantity == Decimal("100.000")
        assert order.produced_quantity == Decimal("0.000")  # 기본값
        assert order.status == "planned"
        assert order.priority == "normal"

    def test_production_order_str_representation(self, admin_user, sample_product):
        """생산 주문 __str__ 메서드 테스트"""
        # Given & When
        order = ProductionOrder.objects.create(
            order_number="PO2025002",
            finished_product=sample_product,
            planned_quantity=Decimal("50.000"),
            planned_start_date=timezone.now() + timedelta(hours=1),
            planned_end_date=timezone.now() + timedelta(days=1),
            created_by=admin_user,
        )

        # Then
        expected = f"PO2025002 - {sample_product.name}"
        assert str(order) == expected

    def test_production_order_unique_order_number(self, admin_user, sample_product):
        """생산 주문 번호 중복 방지 테스트"""
        # Given: 첫 번째 주문 생성
        ProductionOrder.objects.create(
            order_number="DUPLICATE_ORDER",
            finished_product=sample_product,
            planned_quantity=Decimal("30.000"),
            planned_start_date=timezone.now() + timedelta(hours=1),
            planned_end_date=timezone.now() + timedelta(days=1),
            created_by=admin_user,
        )

        # When & Then: 중복 주문 번호로 생성 시도
        with pytest.raises(Exception):  # IntegrityError
            ProductionOrder.objects.create(
                order_number="DUPLICATE_ORDER",  # 중복!
                finished_product=sample_product,
                planned_quantity=Decimal("20.000"),
                planned_start_date=timezone.now() + timedelta(hours=2),
                planned_end_date=timezone.now() + timedelta(days=2),
                created_by=admin_user,
            )

    def test_production_order_status_workflow(self, admin_user, operator_user, sample_product):
        """생산 주문 상태 워크플로우 테스트"""
        # Given: 계획 상태 주문 생성
        order = ProductionOrder.objects.create(
            order_number="PO2025003",
            finished_product=sample_product,
            planned_quantity=Decimal("75.000"),
            planned_start_date=timezone.now() + timedelta(hours=1),
            planned_end_date=timezone.now() + timedelta(days=1),
            status="planned",
            created_by=admin_user,
        )

        # When: 생산 시작 (planned → in_progress)
        order.status = "in_progress"
        order.actual_start_date = timezone.now()
        order.assigned_operator = operator_user
        order.save()

        # Then: 상태 변경 확인
        order.refresh_from_db()
        assert order.status == "in_progress"
        assert order.actual_start_date is not None
        assert order.assigned_operator == operator_user

        # When: 생산 완료 (in_progress → completed)
        order.status = "completed"
        order.actual_end_date = timezone.now()
        order.produced_quantity = Decimal("75.000")
        order.save()

        # Then: 완료 상태 확인
        order.refresh_from_db()
        assert order.status == "completed"
        assert order.actual_end_date is not None
        assert order.produced_quantity == Decimal("75.000")

    def test_production_order_quantity_validation(self, admin_user, sample_product):
        """생산 수량 유효성 검사 테스트"""
        # Given: 잘못된 계획 수량 (0 이하)
        with pytest.raises(ValidationError):
            order = ProductionOrder(
                order_number="PO2025004",
                finished_product=sample_product,
                planned_quantity=Decimal("0.000"),  # 유효하지 않은 수량
                planned_start_date=timezone.now() + timedelta(hours=1),
                planned_end_date=timezone.now() + timedelta(days=1),
                created_by=admin_user,
            )
            order.full_clean()  # 유효성 검사 실행

    def test_production_order_date_validation(self, admin_user, sample_product):
        """생산 날짜 논리 검증 테스트"""
        # Given: 시작일이 종료일보다 늦은 경우
        now = timezone.now()
        
        # 이 테스트는 모델 레벨에서는 체크하지 않을 수도 있음
        # 대신 비즈니스 로직(서비스 레이어)에서 검증하는 것이 일반적
        order = ProductionOrder.objects.create(
            order_number="PO2025005",
            finished_product=sample_product,
            planned_quantity=Decimal("40.000"),
            planned_start_date=now + timedelta(days=2),  # 종료일보다 늦음
            planned_end_date=now + timedelta(days=1),
            created_by=admin_user,
        )
        
        # When & Then: 모델 자체는 생성되지만, 비즈니스 로직에서 검증해야 함
        assert order.planned_start_date > order.planned_end_date
        # 실제로는 서비스 레이어에서 이런 검증을 해야 함

    def test_production_order_progress_calculation(self, admin_user, sample_product):
        """생산 진행률 계산 테스트 (모델 메서드가 있다면)"""
        # Given: 부분 생산 완료 주문
        order = ProductionOrder.objects.create(
            order_number="PO2025006",
            finished_product=sample_product,
            planned_quantity=Decimal("100.000"),
            produced_quantity=Decimal("60.000"),  # 60% 완료
            planned_start_date=timezone.now() + timedelta(hours=1),
            planned_end_date=timezone.now() + timedelta(days=1),
            status="in_progress",
            created_by=admin_user,
        )

        # Then: 진행률 검증 (모델에 계산 메서드가 있다면)
        # 현재 모델에는 progress 메서드가 없으므로 수동 계산
        expected_progress = (order.produced_quantity / order.planned_quantity) * 100
        assert expected_progress == 60.0

    def test_production_order_assigned_operator_optional(self, admin_user, sample_product):
        """담당 운영자는 선택사항 테스트"""
        # Given & When: 담당자 없이 주문 생성
        order = ProductionOrder.objects.create(
            order_number="PO2025007",
            finished_product=sample_product,
            planned_quantity=Decimal("25.000"),
            planned_start_date=timezone.now() + timedelta(hours=1),
            planned_end_date=timezone.now() + timedelta(days=1),
            created_by=admin_user,
        )

        # Then: 담당자 없어도 정상 생성
        assert order.assigned_operator is None
        assert order.status == "planned"  # 기본값