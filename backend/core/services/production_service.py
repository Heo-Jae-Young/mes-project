from datetime import datetime, timedelta
from decimal import Decimal
from django.db import transaction, models
from django.db.models import Sum, F, Q
from django.utils import timezone
from rest_framework.exceptions import ValidationError, PermissionDenied

from core.models import ProductionOrder, MaterialLot, RawMaterial, CCPLog, User


class ProductionService:
    """생산 주문 및 제조 실행 관련 비즈니스 로직"""

    def validate_production_order_creation(self, order_data, user):
        """
        생산 주문 생성 전 검증
        - 원자재 가용성 확인
        - 생산 계획 충돌 검사
        - 권한 검증
        """
        if user.role not in ['admin', 'quality_manager', 'production_manager']:
            raise PermissionDenied('생산 주문 생성 권한이 없습니다.')
        
        # 날짜 유효성 검증
        planned_start = order_data.get('planned_start_date')
        planned_end = order_data.get('planned_end_date')
        
        if planned_start >= planned_end:
            raise ValidationError('계획 종료 시간은 시작 시간보다 늦어야 합니다.')
        
        if planned_start < timezone.now():
            raise ValidationError('계획 시작 시간은 현재 시간 이후여야 합니다.')
        
        # 생산능력 검증 (동시 생산 주문 수 제한)
        concurrent_orders = ProductionOrder.objects.filter(
            status__in=['planned', 'in_progress'],
            planned_start_date__lt=planned_end,
            planned_end_date__gt=planned_start
        ).count()
        
        if concurrent_orders >= 5:  # 최대 동시 생산 주문 수
            raise ValidationError('해당 시간대에 생산 주문이 너무 많습니다.')

    @transaction.atomic
    def start_production(self, production_order, user):
        """
        생산 시작 처리
        - 원자재 할당 및 재고 차감
        - 상태 변경 및 실제 시작 시간 기록
        - 운영자 배정
        """
        if user.role not in ['admin', 'quality_manager', 'operator']:
            raise PermissionDenied('생산 시작 권한이 없습니다.')
        
        if production_order.status != 'planned':
            raise ValidationError('계획 상태의 주문만 시작할 수 있습니다.')
        
        # 원자재 가용성 재검증
        required_materials = self._calculate_required_materials(production_order)
        
        for material_code, required_qty in required_materials.items():
            available_qty = self._get_available_material_quantity(material_code)
            if available_qty < required_qty:
                raise ValidationError(
                    f'원자재 부족: {material_code} (필요: {required_qty}, 가용: {available_qty})'
                )
        
        # 원자재 할당 및 재고 차감
        for material_code, required_qty in required_materials.items():
            self._allocate_materials(material_code, required_qty, production_order)
        
        # 생산 주문 상태 업데이트
        production_order.status = 'in_progress'
        production_order.actual_start_date = timezone.now()
        
        # 운영자가 시작하는 경우 자동 배정
        if user.role == 'operator':
            production_order.assigned_operator = user
        
        production_order.save()
        
        return production_order

    @transaction.atomic
    def complete_production(self, production_order, produced_quantity, user):
        """
        생산 완료 처리
        - 생산량 기록 및 검증
        - HACCP 로그 완료 확인
        - 품질 검사 결과 확인
        """
        if user.role not in ['admin', 'quality_manager', 'operator']:
            raise PermissionDenied('생산 완료 권한이 없습니다.')
        
        if production_order.status != 'in_progress':
            raise ValidationError('진행 중인 주문만 완료할 수 있습니다.')
        
        if produced_quantity <= 0:
            raise ValidationError('생산량은 0보다 커야 합니다.')
        
        if produced_quantity > production_order.planned_quantity * 1.1:  # 10% 초과 방지
            raise ValidationError('계획 수량을 10% 이상 초과할 수 없습니다.')
        
        # HACCP 로그 완료 확인
        incomplete_ccp_logs = CCPLog.objects.filter(
            production_order=production_order,
            verified_by__isnull=True
        ).count()
        
        if incomplete_ccp_logs > 0:
            raise ValidationError(f'미검증 HACCP 로그 {incomplete_ccp_logs}건이 있습니다.')
        
        # 생산 완료 처리
        production_order.status = 'completed'
        production_order.produced_quantity = produced_quantity
        production_order.actual_end_date = timezone.now()
        production_order.save()
        
        return production_order

    def get_production_efficiency(self, production_order):
        """
        생산 효율성 지표 계산
        - 계획 대비 실제 생산량
        - 계획 대비 실제 소요 시간
        - HACCP 준수율
        """
        if production_order.status not in ['completed']:
            return None
        
        # 수량 효율성
        quantity_efficiency = (
            production_order.produced_quantity / production_order.planned_quantity
        ) * 100
        
        # 시간 효율성
        planned_duration = (
            production_order.planned_end_date - production_order.planned_start_date
        ).total_seconds() / 3600  # 시간 단위
        
        actual_duration = (
            production_order.actual_end_date - production_order.actual_start_date
        ).total_seconds() / 3600
        
        time_efficiency = (planned_duration / actual_duration) * 100 if actual_duration > 0 else 0
        
        # HACCP 준수율
        total_ccp_logs = CCPLog.objects.filter(production_order=production_order).count()
        compliant_logs = CCPLog.objects.filter(
            production_order=production_order,
            is_within_limits=True
        ).count()
        
        haccp_compliance = (compliant_logs / total_ccp_logs) * 100 if total_ccp_logs > 0 else 100
        
        return {
            'quantity_efficiency': round(quantity_efficiency, 2),
            'time_efficiency': round(time_efficiency, 2),
            'haccp_compliance': round(haccp_compliance, 2),
            'overall_efficiency': round((quantity_efficiency + time_efficiency + haccp_compliance) / 3, 2)
        }

    def _calculate_required_materials(self, production_order):
        """
        생산 주문에 필요한 원자재 계산
        (실제로는 BOM - Bill of Materials 테이블이 필요하지만, 임시로 간단한 로직 구현)
        """
        # TODO: BOM 테이블 구현 후 실제 계산 로직 적용
        # 현재는 샘플 데이터로 대체
        return {
            f'RM-{production_order.finished_product.code}-001': production_order.planned_quantity * 0.5,
            f'RM-{production_order.finished_product.code}-002': production_order.planned_quantity * 0.3,
        }

    def _get_available_material_quantity(self, material_code):
        """지정된 원자재 코드의 가용 수량 조회"""
        try:
            material = RawMaterial.objects.get(code=material_code)
            available_lots = MaterialLot.objects.filter(
                raw_material=material,
                status='in_storage',
                quantity_current__gt=0
            )
            return available_lots.aggregate(
                total=Sum('quantity_current')
            )['total'] or 0
        except RawMaterial.DoesNotExist:
            return 0

    def _allocate_materials(self, material_code, required_qty, production_order):
        """
        원자재 할당 및 재고 차감 (FIFO 방식)
        """
        try:
            material = RawMaterial.objects.get(code=material_code)
            available_lots = MaterialLot.objects.filter(
                raw_material=material,
                status='in_storage',
                quantity_current__gt=0
            ).order_by('received_date')  # FIFO
            
            remaining_qty = required_qty
            
            for lot in available_lots:
                if remaining_qty <= 0:
                    break
                
                if lot.quantity_current >= remaining_qty:
                    # 이 로트에서 모든 수량 충당 가능
                    lot.quantity_current -= remaining_qty
                    if lot.quantity_current == 0:
                        lot.status = 'used'
                    remaining_qty = 0
                else:
                    # 이 로트를 모두 사용하고 다음 로트로
                    remaining_qty -= lot.quantity_current
                    lot.quantity_current = 0
                    lot.status = 'used'
                
                lot.save()
        
        except RawMaterial.DoesNotExist:
            raise ValidationError(f'원자재 코드 {material_code}를 찾을 수 없습니다.')


class ProductionQueryService:
    """생산 관련 데이터 조회 최적화 서비스"""

    def get_production_orders_for_user(self, user, **filters):
        """사용자 역할에 따른 생산 주문 조회"""
        queryset = ProductionOrder.objects.select_related(
            'finished_product', 'assigned_operator', 'created_by'
        )
        
        # 역할별 필터링
        if user.role == 'operator':
            # 운영자는 자신이 배정된 주문만 조회
            queryset = queryset.filter(assigned_operator=user)
        elif user.role not in ['admin', 'quality_manager', 'production_manager']:
            # 권한 없는 사용자는 빈 결과
            return ProductionOrder.objects.none()
        
        # 추가 필터 적용
        if 'status' in filters:
            queryset = queryset.filter(status=filters['status'])
        if 'priority' in filters:
            queryset = queryset.filter(priority=filters['priority'])
        if 'date_from' in filters:
            queryset = queryset.filter(planned_start_date__gte=filters['date_from'])
        if 'date_to' in filters:
            queryset = queryset.filter(planned_end_date__lte=filters['date_to'])
        
        return queryset.order_by('-created_at')

    def get_production_dashboard_data(self, user):
        """생산 대시보드용 요약 데이터"""
        if user.role not in ['admin', 'quality_manager', 'production_manager']:
            raise PermissionDenied('대시보드 조회 권한이 없습니다.')
        
        today = timezone.now().date()
        
        # 오늘 생산 현황
        today_orders = ProductionOrder.objects.filter(
            planned_start_date__date=today
        )
        
        # 주간 통계 (최근 7일)
        week_ago = timezone.now() - timedelta(days=7)
        week_orders = ProductionOrder.objects.filter(
            created_at__gte=week_ago
        )
        
        return {
            'today_stats': {
                'total_orders': today_orders.count(),
                'in_progress': today_orders.filter(status='in_progress').count(),
                'completed': today_orders.filter(status='completed').count(),
                'planned': today_orders.filter(status='planned').count()
            },
            'week_stats': {
                'total_orders': week_orders.count(),
                'completed_orders': week_orders.filter(status='completed').count(),
                'avg_efficiency': self._calculate_avg_efficiency(week_orders.filter(status='completed'))
            },
            'urgent_orders': ProductionOrder.objects.filter(
                priority='urgent',
                status__in=['planned', 'in_progress']
            ).count(),
            'overdue_orders': ProductionOrder.objects.filter(
                planned_end_date__lt=timezone.now(),
                status__in=['planned', 'in_progress']
            ).count()
        }

    def _calculate_avg_efficiency(self, completed_orders):
        """완료된 주문들의 평균 효율성 계산"""
        if not completed_orders.exists():
            return 0
        
        production_service = ProductionService()
        efficiencies = []
        
        for order in completed_orders:
            efficiency_data = production_service.get_production_efficiency(order)
            if efficiency_data:
                efficiencies.append(efficiency_data['overall_efficiency'])
        
        return round(sum(efficiencies) / len(efficiencies), 2) if efficiencies else 0


class MaterialTraceabilityService:
    """원자재 추적성 관리 서비스"""

    def get_material_traceability(self, material_lot_id):
        """
        원자재 로트의 완전한 추적성 정보 조회
        - 공급업체 정보
        - 사용된 생산 주문
        - 품질 검사 이력
        """
        try:
            lot = MaterialLot.objects.select_related(
                'raw_material', 'supplier', 'created_by'
            ).get(id=material_lot_id)
            
            # 이 로트가 사용된 생산 주문 조회 (임시 로직)
            # TODO: 실제로는 MaterialUsage 중간 테이블이 필요
            related_orders = ProductionOrder.objects.filter(
                created_at__gte=lot.received_date,
                status__in=['completed', 'in_progress']
            )
            
            return {
                'lot_info': {
                    'lot_number': lot.lot_number,
                    'material_name': lot.raw_material.name,
                    'material_code': lot.raw_material.code,
                    'received_date': lot.received_date,
                    'expiry_date': lot.expiry_date,
                    'current_quantity': lot.quantity_current,
                    'original_quantity': lot.quantity_received,
                    'status': lot.get_status_display()
                },
                'supplier_info': {
                    'name': lot.supplier.name,
                    'code': lot.supplier.code,
                    'contact': lot.supplier.contact_email
                },
                'quality_info': {
                    'test_passed': lot.quality_test_passed,
                    'test_date': lot.quality_test_date,
                    'test_notes': lot.quality_test_notes
                },
                'usage_history': [
                    {
                        'order_number': order.order_number,
                        'product_name': order.finished_product.name,
                        'start_date': order.actual_start_date,
                        'status': order.get_status_display()
                    }
                    for order in related_orders
                ]
            }
            
        except MaterialLot.DoesNotExist:
            raise ValidationError('존재하지 않는 원자재 로트입니다.')

    def get_forward_traceability(self, production_order_id):
        """
        전방 추적성: 사용된 원자재 → 완성품
        """
        try:
            order = ProductionOrder.objects.select_related(
                'finished_product'
            ).get(id=production_order_id)
            
            # TODO: MaterialUsage 테이블 구현 후 실제 사용된 로트 조회
            # 현재는 시간 기반 추정
            used_materials = MaterialLot.objects.filter(
                raw_material__code__contains=order.finished_product.code[:3],
                status='used',
                updated_at__gte=order.actual_start_date,
                updated_at__lte=order.actual_end_date or timezone.now()
            )
            
            return {
                'production_info': {
                    'order_number': order.order_number,
                    'product_name': order.finished_product.name,
                    'produced_quantity': order.produced_quantity,
                    'production_date': order.actual_start_date
                },
                'used_materials': [
                    {
                        'lot_number': lot.lot_number,
                        'material_name': lot.raw_material.name,
                        'supplier': lot.supplier.name,
                        'received_date': lot.received_date
                    }
                    for lot in used_materials
                ]
            }
            
        except ProductionOrder.DoesNotExist:
            raise ValidationError('존재하지 않는 생산 주문입니다.')