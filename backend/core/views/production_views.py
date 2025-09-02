from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Avg, Q, F
from django.utils import timezone
from datetime import timedelta
from core.models import ProductionOrder, CCPLog
from core.serializers import ProductionOrderSerializer, ProductionOrderCreateSerializer, ProductionOrderUpdateSerializer
from core.services.production_service import ProductionService, ProductionQueryService, MaterialTraceabilityService
from core.services.haccp_service import HaccpService


class ProductionOrderViewSet(viewsets.ModelViewSet):
    """생산오더 관리 ViewSet"""
    
    queryset = ProductionOrder.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'finished_product', 'assigned_operator']
    search_fields = ['order_number', 'finished_product__name', 'notes']
    ordering_fields = ['planned_start_date', 'priority', 'created_at']
    ordering = ['-created_at']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.production_service = ProductionService()
        self.production_query_service = ProductionQueryService()
        self.traceability_service = MaterialTraceabilityService()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProductionOrderCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ProductionOrderUpdateSerializer
        return ProductionOrderSerializer
    
    def get_queryset(self):
        """역할별 생산오더 조회 권한"""
        # Service를 통해 사용자별 권한 필터링된 queryset 가져오기
        queryset = self.production_query_service.get_production_orders_for_user(self.request.user)
        
        # 날짜 범위 필터
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(planned_start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(planned_end_date__lte=end_date)
            
        return queryset
    
    @action(detail=True, methods=['post'])
    def start_production(self, request, pk=None):
        """생산 시작"""
        order = self.get_object()
        
        try:
            # Service를 통한 생산 시작 처리
            updated_order = self.production_service.start_production(order, request.user)
            serializer = ProductionOrderSerializer(updated_order)
            return Response({
                'detail': '생산이 시작되었습니다.',
                'order': serializer.data
            })
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def complete_production(self, request, pk=None):
        """생산 완료"""
        order = self.get_object()
        produced_quantity = request.data.get('produced_quantity')
        completion_notes = request.data.get('notes', '')
        
        try:
            # Service를 통한 생산 완료 처리
            updated_order = self.production_service.complete_production(
                order=order,
                produced_quantity=produced_quantity,
                completion_notes=completion_notes
            )
            serializer = ProductionOrderSerializer(updated_order)
            return Response({
                'detail': '생산이 완료되었습니다.',
                'order': serializer.data
            })
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def pause_production(self, request, pk=None):
        """생산 일시정지"""
        order = self.get_object()
        
        if order.status != 'in_progress':
            return Response(
                {'detail': '진행 중인 오더만 일시정지할 수 있습니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        pause_reason = request.data.get('reason', '')
        
        order.status = 'on_hold'
        if pause_reason:
            order.notes = f"{order.notes}\n일시정지: {pause_reason}".strip()
        
        order.save()
        
        return Response({
            'detail': '생산이 일시정지되었습니다.',
            'order': ProductionOrderSerializer(order).data
        })
    
    @action(detail=True, methods=['post'])
    def resume_production(self, request, pk=None):
        """생산 재개"""
        order = self.get_object()
        
        if order.status != 'on_hold':
            return Response(
                {'detail': '일시정지 상태의 오더만 재개할 수 있습니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'in_progress'
        order.notes = f"{order.notes}\n생산 재개".strip()
        order.save()
        
        return Response({
            'detail': '생산이 재개되었습니다.',
            'order': ProductionOrderSerializer(order).data
        })
    
    @action(detail=True, methods=['get'])
    def ccp_logs(self, request, pk=None):
        """생산오더와 연결된 CCP 로그"""
        order = self.get_object()
        
        ccp_logs = order.ccp_logs.select_related('ccp', 'created_by').order_by('-measured_at')[:50]
        
        logs_data = []
        for log in ccp_logs:
            logs_data.append({
                'id': log.id,
                'ccp_name': log.ccp.name,
                'ccp_type': log.ccp.get_ccp_type_display(),
                'measured_value': log.measured_value,
                'unit': log.unit,
                'measured_at': log.measured_at,
                'status': log.get_status_display(),
                'is_within_limits': log.is_within_limits,
                'deviation_notes': log.deviation_notes,
                'created_by': log.created_by.username
            })
        
        return Response({
            'order_number': order.order_number,
            'product_name': order.finished_product.name,
            'ccp_logs': logs_data,
            'total_logs': order.ccp_logs.count()
        })
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """생산 대시보드 데이터"""
        # 오늘 생산 현황
        today = timezone.now().date()
        today_orders = ProductionOrder.objects.filter(
            planned_start_date__date=today
        )
        
        # 전체 현황
        all_orders = ProductionOrder.objects.all()
        
        # 상태별 분포
        status_counts = {}
        for status_key, status_name in ProductionOrder.STATUS_CHOICES:
            count = all_orders.filter(status=status_key).count()
            status_counts[status_name] = count
        
        # 우선순위별 분포
        priority_counts = {}
        for priority_key, priority_name in ProductionOrder.PRIORITY_CHOICES:
            count = all_orders.filter(priority=priority_key).count()
            priority_counts[priority_name] = count
        
        # 지연된 오더 (계획 종료일이 지났지만 완료되지 않은 것)
        overdue_orders = all_orders.filter(
            planned_end_date__lt=timezone.now(),
            status__in=['planned', 'in_progress', 'on_hold']
        ).count()
        
        # 최근 7일 완료 오더
        week_ago = timezone.now() - timedelta(days=7)
        recent_completed = all_orders.filter(
            status='completed',
            actual_end_date__gte=week_ago
        ).count()
        
        # 평균 완료율
        completed_orders = all_orders.filter(status='completed')
        if completed_orders.exists():
            avg_completion_rate = completed_orders.aggregate(
                avg_rate=Avg('produced_quantity') * 100 / Avg('planned_quantity')
            )['avg_rate'] or 0
        else:
            avg_completion_rate = 0
        
        return Response({
            'today_summary': {
                'total_orders': today_orders.count(),
                'in_progress': today_orders.filter(status='in_progress').count(),
                'completed': today_orders.filter(status='completed').count(),
                'planned': today_orders.filter(status='planned').count()
            },
            'overall_summary': {
                'total_orders': all_orders.count(),
                'overdue_orders': overdue_orders,
                'recent_completed': recent_completed,
                'avg_completion_rate': round(avg_completion_rate, 2)
            },
            'status_distribution': status_counts,
            'priority_distribution': priority_counts
        })
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """예정된 생산오더"""
        days_ahead = int(request.query_params.get('days', '7'))
        end_date = timezone.now() + timedelta(days=days_ahead)
        
        upcoming_orders = ProductionOrder.objects.filter(
            planned_start_date__gte=timezone.now(),
            planned_start_date__lte=end_date,
            status='planned'
        ).select_related('finished_product', 'assigned_operator').order_by('planned_start_date')
        
        serializer = ProductionOrderSerializer(upcoming_orders, many=True)
        return Response({
            'period_days': days_ahead,
            'upcoming_orders': serializer.data,
            'total_count': upcoming_orders.count()
        })
    
    @action(detail=False, methods=['get'])
    def performance(self, request):
        """생산 성과 분석"""
        # 최근 30일 성과
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_orders = ProductionOrder.objects.filter(
            actual_end_date__gte=thirty_days_ago,
            status='completed'
        )
        
        if not recent_orders.exists():
            return Response({
                'message': '최근 30일간 완료된 생산오더가 없습니다.'
            })
        
        # 생산량 통계
        total_planned = recent_orders.aggregate(Sum('planned_quantity'))['planned_quantity__sum'] or 0
        total_produced = recent_orders.aggregate(Sum('produced_quantity'))['produced_quantity__sum'] or 0
        
        # 일정 준수율
        on_time_orders = recent_orders.filter(
            actual_end_date__lte=F('planned_end_date')
        ).count()
        
        schedule_adherence = (on_time_orders / recent_orders.count() * 100) if recent_orders.count() > 0 else 0
        
        # 제품별 성과
        product_performance = recent_orders.values(
            'finished_product__name',
            'finished_product__code'
        ).annotate(
            total_orders=Count('id'),
            total_produced=Sum('produced_quantity'),
            avg_completion_rate=Avg('produced_quantity') * 100 / Avg('planned_quantity')
        ).order_by('-total_produced')[:10]
        
        return Response({
            'analysis_period': '최근 30일',
            'production_summary': {
                'total_orders': recent_orders.count(),
                'total_planned': total_planned,
                'total_produced': total_produced,
                'production_efficiency': round((total_produced / total_planned * 100), 2) if total_planned > 0 else 0,
                'schedule_adherence': round(schedule_adherence, 2)
            },
            'top_products': list(product_performance)
        })

class StatisticsAPIView(APIView):
    """대시보드 통계 데이터 API"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        haccp_service = HaccpService()
        
        # HACCP 준수율 (최근 30일)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        compliance_stats = haccp_service.calculate_compliance_score(
            date_from=thirty_days_ago,
            date_to=timezone.now()
        )
        compliance_rate = compliance_stats.get('compliance_score', 0)
        
        # 중요 이탈 건수 (최근 7일)
        seven_days_ago = timezone.now() - timedelta(days=7)
        critical_issues_count = CCPLog.objects.filter(
            is_within_limits=False,
            created_at__gte=seven_days_ago
        ).count()
        
        # 진행중인 생산 오더 수
        active_orders_count = ProductionOrder.objects.filter(status='in_progress').count()

        data = {
            'compliance_rate': round(compliance_rate, 2),
            'critical_issues_count': critical_issues_count,
            'active_production_orders': active_orders_count,
        }
        
        return Response(data)
