"""Service Layer 단위 테스트"""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone
from django.test import TestCase
from rest_framework.exceptions import ValidationError, PermissionDenied

from core.services.user_service import UserService, UserQueryService, UserStatsService
from core.services.haccp_service import HaccpService, HaccpQueryService
from core.services.production_service import ProductionService, ProductionQueryService
from core.services.supplier_service import SupplierService, SupplierQueryService
from core.tests.helpers.user_helpers import (
    create_admin_user, create_quality_manager, create_operator, create_test_user
)
from core.tests.helpers.haccp_helpers import create_test_ccp, create_test_ccp_log
from core.tests.helpers.production_helpers import (
    create_test_production_order, create_in_progress_production_order, 
    create_completed_production_order
)
from core.tests.helpers.supplier_helpers import create_test_supplier, create_test_material_lot


@pytest.mark.unit
class UserServiceTest(TestCase):
    """UserService 단위 테스트"""

    def setUp(self):
        self.service = UserService()
        self.admin_user = create_admin_user()
        self.operator_user = create_operator()

    def test_change_password_success_admin(self):
        """관리자가 다른 사용자 비밀번호 변경 성공"""
        self.service.change_password(
            user_to_change=self.operator_user,
            old_password=None,
            new_password='newpass123',
            new_password_confirm='newpass123',
            acting_user=self.admin_user
        )
        
        # 비밀번호가 변경되었는지 확인
        self.operator_user.refresh_from_db()
        self.assertTrue(self.operator_user.check_password('newpass123'))

    def test_change_password_success_self(self):
        """사용자가 자신의 비밀번호 변경 성공"""
        self.service.change_password(
            user_to_change=self.operator_user,
            old_password='testpass123',
            new_password='newpass123',
            new_password_confirm='newpass123',
            acting_user=self.operator_user
        )
        
        self.operator_user.refresh_from_db()
        self.assertTrue(self.operator_user.check_password('newpass123'))

    def test_change_password_permission_denied(self):
        """권한 없는 사용자가 다른 사용자 비밀번호 변경 시도"""
        other_user = create_operator(username='other_operator')
        
        with self.assertRaises(PermissionDenied):
            self.service.change_password(
                user_to_change=other_user,
                old_password='testpass123',
                new_password='newpass123',
                new_password_confirm='newpass123',
                acting_user=self.operator_user
            )

    def test_change_password_wrong_old_password(self):
        """잘못된 기존 비밀번호로 변경 시도"""
        with self.assertRaises(ValidationError):
            self.service.change_password(
                user_to_change=self.operator_user,
                old_password='wrongpass',
                new_password='newpass123',
                new_password_confirm='newpass123',
                acting_user=self.operator_user
            )

    def test_change_password_mismatch_confirmation(self):
        """새 비밀번호와 확인 비밀번호 불일치"""
        with self.assertRaises(ValidationError):
            self.service.change_password(
                user_to_change=self.operator_user,
                old_password='testpass123',
                new_password='newpass123',
                new_password_confirm='different123',
                acting_user=self.operator_user
            )


@pytest.mark.unit
class UserQueryServiceTest(TestCase):
    """UserQueryService 단위 테스트"""

    def setUp(self):
        self.service = UserQueryService()
        self.admin_user = create_admin_user()
        self.quality_user = create_quality_manager()
        self.operator_user = create_operator()

    def test_get_queryset_for_admin(self):
        """관리자는 모든 사용자 조회 가능"""
        queryset = self.service.get_queryset_for_user(self.admin_user)
        self.assertEqual(queryset.count(), 3)  # admin, quality, operator

    def test_get_queryset_for_quality_manager(self):
        """품질관리자는 모든 사용자 조회 가능"""
        queryset = self.service.get_queryset_for_user(self.quality_user)
        self.assertEqual(queryset.count(), 3)

    def test_get_queryset_for_operator(self):
        """운영자는 자신만 조회 가능"""
        queryset = self.service.get_queryset_for_user(self.operator_user)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.operator_user)


@pytest.mark.unit
class HaccpServiceTest(TestCase):
    """HaccpService 단위 테스트"""

    def setUp(self):
        self.service = HaccpService()
        self.admin_user = create_admin_user()
        self.operator_user = create_operator()
        self.ccp = create_test_ccp(created_by=self.admin_user)

    def test_validate_ccp_log_creation_success(self):
        """CCP 로그 생성 검증 성공"""
        # 예외가 발생하지 않아야 함
        self.service.validate_ccp_log_creation(
            ccp=self.ccp,
            measured_value=Decimal('25.0'),
            measured_at=timezone.now(),
            created_by=self.operator_user
        )

    def test_validate_ccp_log_creation_inactive_ccp(self):
        """비활성 CCP에 로그 생성 시도"""
        self.ccp.is_active = False
        self.ccp.save()
        
        with self.assertRaises(ValidationError) as context:
            self.service.validate_ccp_log_creation(
                ccp=self.ccp,
                measured_value=Decimal('25.0'),
                measured_at=timezone.now(),
                created_by=self.operator_user
            )
        
        self.assertIn('비활성 CCP', str(context.exception))

    def test_validate_ccp_log_creation_permission_denied(self):
        """권한 없는 사용자의 CCP 로그 생성 시도"""
        unauthorized_user = create_test_user(role='viewer')
        
        with self.assertRaises(PermissionDenied):
            self.service.validate_ccp_log_creation(
                ccp=self.ccp,
                measured_value=Decimal('25.0'),
                measured_at=timezone.now(),
                created_by=unauthorized_user
            )

    def test_validate_ccp_log_creation_future_time(self):
        """미래 시점 측정 시간으로 생성 시도"""
        future_time = timezone.now() + timedelta(hours=1)
        
        with self.assertRaises(ValidationError) as context:
            self.service.validate_ccp_log_creation(
                ccp=self.ccp,
                measured_value=Decimal('25.0'),
                measured_at=future_time,
                created_by=self.operator_user
            )
        
        self.assertIn('미래 시점', str(context.exception))

    def test_calculate_compliance_score_no_data(self):
        """데이터 없는 경우 컴플라이언스 점수 계산"""
        score = self.service.calculate_compliance_score()
        
        self.assertEqual(score['compliance_score'], 100)
        self.assertEqual(score['total_measurements'], 0)

    def test_calculate_compliance_score_with_data(self):
        """데이터 있는 경우 컴플라이언스 점수 계산"""
        # 기준 내 로그 2개 생성
        create_test_ccp_log(
            ccp=self.ccp,
            measured_value=Decimal('24.0'),
            is_within_limits=True,
            created_by=self.operator_user
        )
        create_test_ccp_log(
            ccp=self.ccp,
            measured_value=Decimal('26.0'),
            is_within_limits=True,
            created_by=self.operator_user
        )
        
        # 기준 초과 로그 1개 생성
        create_test_ccp_log(
            ccp=self.ccp,
            measured_value=Decimal('30.0'),
            is_within_limits=False,
            created_by=self.operator_user
        )
        
        score = self.service.calculate_compliance_score(ccp=self.ccp)
        
        self.assertEqual(score['total_measurements'], 3)
        self.assertEqual(score['within_limits_count'], 2)
        self.assertEqual(score['out_of_limits_count'], 1)
        self.assertAlmostEqual(score['compliance_rate'], 66.67, places=1)


@pytest.mark.unit
class ProductionServiceTest(TestCase):
    """ProductionService 단위 테스트"""

    def setUp(self):
        self.service = ProductionService()
        self.admin_user = create_admin_user()
        self.operator_user = create_operator()

    def test_validate_production_order_creation_success(self):
        """생산 주문 생성 검증 성공"""
        now = timezone.now()
        order_data = {
            'planned_start_date': now + timedelta(hours=1),
            'planned_end_date': now + timedelta(hours=8)
        }
        
        # 예외가 발생하지 않아야 함
        self.service.validate_production_order_creation(order_data, self.admin_user)

    def test_validate_production_order_creation_permission_denied(self):
        """권한 없는 사용자의 생산 주문 생성 시도"""
        unauthorized_user = create_test_user(role='viewer')
        order_data = {}
        
        with self.assertRaises(PermissionDenied):
            self.service.validate_production_order_creation(order_data, unauthorized_user)

    def test_validate_production_order_creation_invalid_dates(self):
        """잘못된 날짜로 생산 주문 생성 시도"""
        now = timezone.now()
        order_data = {
            'planned_start_date': now + timedelta(hours=8),
            'planned_end_date': now + timedelta(hours=1)  # 종료가 시작보다 빠름
        }
        
        with self.assertRaises(ValidationError) as context:
            self.service.validate_production_order_creation(order_data, self.admin_user)
        
        self.assertIn('종료 시간은 시작 시간보다 늦어야', str(context.exception))

    def test_get_production_efficiency_completed_order(self):
        """완료된 주문의 생산 효율성 계산"""
        order = create_completed_production_order(
            planned_quantity=100,
            produced_quantity=95,
            created_by=self.admin_user
        )
        
        # CCP 로그 생성 (HACCP 준수율 계산용)
        ccp = create_test_ccp(created_by=self.admin_user)
        create_test_ccp_log(
            ccp=ccp,
            production_order=order,
            is_within_limits=True,
            created_by=self.operator_user
        )
        
        efficiency = self.service.get_production_efficiency(order)
        
        self.assertIsNotNone(efficiency)
        self.assertEqual(efficiency['quantity_efficiency'], 95.0)
        self.assertEqual(efficiency['haccp_compliance'], 100.0)

    def test_get_production_efficiency_in_progress_order(self):
        """진행 중인 주문의 효율성 계산 (None 반환)"""
        order = create_in_progress_production_order(created_by=self.admin_user)
        
        efficiency = self.service.get_production_efficiency(order)
        
        self.assertIsNone(efficiency)


@pytest.mark.unit
class SupplierServiceTest(TestCase):
    """SupplierService 단위 테스트"""

    def setUp(self):
        self.service = SupplierService()
        self.admin_user = create_admin_user()
        self.operator_user = create_operator()

    def test_validate_supplier_creation_success(self):
        """공급업체 생성 검증 성공"""
        supplier_data = {
            'code': 'SUP001',
            'email': 'test@supplier.com',
            'certification': 'HACCP ISO9001'
        }
        
        # 예외가 발생하지 않아야 함
        self.service.validate_supplier_creation(supplier_data, self.admin_user)

    def test_validate_supplier_creation_permission_denied(self):
        """권한 없는 사용자의 공급업체 생성 시도"""
        supplier_data = {}
        
        with self.assertRaises(PermissionDenied):
            self.service.validate_supplier_creation(supplier_data, self.operator_user)

    def test_validate_supplier_creation_duplicate_code(self):
        """중복 코드로 공급업체 생성 시도"""
        existing_supplier = create_test_supplier(code='SUP001', created_by=self.admin_user)
        
        supplier_data = {
            'code': 'SUP001',  # 중복
            'email': 'new@supplier.com',
            'certification': 'HACCP'
        }
        
        with self.assertRaises(ValidationError) as context:
            self.service.validate_supplier_creation(supplier_data, self.admin_user)
        
        self.assertIn('이미 존재하는 공급업체 코드', str(context.exception))

    def test_validate_supplier_creation_missing_haccp(self):
        """HACCP 인증 누락으로 공급업체 생성 시도"""
        supplier_data = {
            'code': 'SUP002',
            'email': 'test@supplier.com',
            'certification': 'ISO9001'  # HACCP 누락
        }
        
        with self.assertRaises(ValidationError) as context:
            self.service.validate_supplier_creation(supplier_data, self.admin_user)
        
        self.assertIn('HACCP 인증 정보는 필수', str(context.exception))

    def test_evaluate_supplier_performance_no_data(self):
        """납품 이력 없는 공급업체 성과 평가"""
        supplier = create_test_supplier(created_by=self.admin_user)
        
        performance = self.service.evaluate_supplier_performance(supplier)
        
        self.assertEqual(performance['overall_score'], 0)
        self.assertEqual(performance['total_deliveries'], 0)

    def test_get_supplier_risk_assessment(self):
        """공급업체 리스크 평가"""
        supplier = create_test_supplier(
            certification='ISO9001',  # HACCP 누락
            created_by=self.admin_user
        )
        
        risk = self.service.get_supplier_risk_assessment(supplier)
        
        self.assertIn('risk_level', risk)
        self.assertIn('risk_score', risk)
        self.assertIn('HACCP 인증 누락', risk['risk_factors'])