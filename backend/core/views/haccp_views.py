from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from core.models import CCP, CCPLog
from core.serializers import (
    CCPSerializer, CCPCreateSerializer,
    CCPLogSerializer, CCPLogCreateSerializer, CCPLogUpdateSerializer
)
from core.services.haccp_service import HaccpService, HaccpQueryService


class CCPViewSet(viewsets.ModelViewSet):
    """중요 관리점(CCP) 관리 ViewSet"""
    
    queryset = CCP.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['ccp_type', 'finished_product', 'is_active']
    search_fields = ['name', 'code', 'description', 'process_step']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['-created_at']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.haccp_service = HaccpService()
        self.haccp_query_service = HaccpQueryService()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CCPCreateSerializer
        return CCPSerializer
    
    def get_queryset(self):
        """역할별 CCP 조회 권한"""
        return self.haccp_query_service.get_ccps_for_user(self.request.user)
    
    def perform_destroy(self, instance):
        """CCP 삭제 시 로그 존재 확인"""
        if instance.logs.exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError("모니터링 로그가 존재하는 CCP는 삭제할 수 없습니다. 비활성화하세요.")
        
        super().perform_destroy(instance)
    
    @action(detail=True, methods=['get'])
    def monitoring_logs(self, request, pk=None):
        """특정 CCP의 모니터링 로그"""
        ccp = self.get_object()
        
        # 날짜 범위 필터
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        status_filter = request.query_params.get('status')
        
        queryset = ccp.logs.all()
        
        if start_date:
            queryset = queryset.filter(measured_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(measured_at__lte=end_date)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # 최근 100개 제한
        logs = queryset.order_by('-measured_at')[:100]
        serializer = CCPLogSerializer(logs, many=True)
        
        return Response({
            'ccp_info': {
                'name': ccp.name,
                'code': ccp.code,
                'type': ccp.get_ccp_type_display(),
                'process_step': ccp.process_step
            },
            'logs': serializer.data,
            'total_logs': ccp.logs.count()
        })
    
    @action(detail=True, methods=['get'])
    def compliance_report(self, request, pk=None):
        """CCP 규정 준수 보고서 (개별 CCP)"""
        ccp = self.get_object()
        days = int(request.query_params.get('days', '30'))
        
        # TODO: Service에 개별 CCP 보고서 메소드 추가 후 리팩토링 예정
        from datetime import timedelta
        start_date = timezone.now() - timedelta(days=days)
        
        logs = ccp.logs.filter(measured_at__gte=start_date)
        
        if not logs.exists():
            return Response({
                'ccp_name': ccp.name,
                'analysis_period': f'최근 {days}일',
                'message': '해당 기간에 모니터링 로그가 없습니다.'
            })
        
        # 기본 통계
        total_logs = logs.count()
        within_limits = logs.filter(status='within_limits').count()
        compliance_rate = (within_limits / total_logs * 100) if total_logs > 0 else 0
        
        return Response({
            'ccp_info': {
                'name': ccp.name,
                'code': ccp.code,
                'type': ccp.get_ccp_type_display()
            },
            'analysis_period': f'최근 {days}일',
            'compliance_summary': {
                'total_measurements': total_logs,
                'within_limits': within_limits,
                'compliance_rate': round(compliance_rate, 2)
            }
        })
    
    @action(detail=False, methods=['get'])
    def types(self, request):
        """CCP 타입 목록"""
        types = [{'key': key, 'value': value} for key, value in CCP.CCP_TYPE_CHOICES]
        return Response(types)
    
    @action(detail=False, methods=['get'])
    def critical_alerts(self, request):
        """중요 알림 - 최근 기준 이탈 CCP"""
        hours = int(request.query_params.get('hours', '24'))
        alerts = self.haccp_service.get_critical_alerts(user=request.user, hours=hours)
        return Response(alerts)


class CCPLogViewSet(viewsets.ModelViewSet):
    """CCP 모니터링 로그 ViewSet - 불변 데이터"""
    
    queryset = CCPLog.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'ccp', 'production_order', 'is_within_limits']
    search_fields = ['ccp__name', 'deviation_notes', 'corrective_action_taken']
    ordering_fields = ['measured_at', 'created_at']
    ordering = ['-measured_at']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.haccp_service = HaccpService()
        self.haccp_query_service = HaccpQueryService()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CCPLogCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CCPLogUpdateSerializer  # 개선조치 정보만 수정 가능
        return CCPLogSerializer
    
    def get_queryset(self):
        """로그 조회 필터링"""
        # Service를 통해 사용자별 권한 필터링된 queryset 가져오기
        queryset = self.haccp_query_service.get_ccp_logs_for_user(self.request.user)
        
        # 날짜 범위 필터
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(measured_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(measured_at__lte=end_date)
        
        # 작업자는 자신이 생성한 로그만 수정 가능
        if self.action in ['update', 'partial_update'] and self.request.user.role == 'operator':
            queryset = queryset.filter(created_by=self.request.user)
            
        return queryset
    
    def perform_create(self, serializer):
        """CCP 로그 생성 시 Service를 통한 검증"""
        validated_data = serializer.validated_data
        ccp = validated_data['ccp']
        measured_value = validated_data['measured_value']
        measured_at = validated_data['measured_at']
        
        # Service를 통한 검증
        self.haccp_service.validate_ccp_log_creation(
            ccp=ccp,
            measured_value=measured_value,
            measured_at=measured_at,
            created_by=self.request.user
        )
        
        # 검증 통과 시 생성
        serializer.save(created_by=self.request.user)
    
    def perform_destroy(self, instance):
        """CCP 로그는 삭제 불가 (HACCP 규정 준수)"""
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied("CCP 모니터링 로그는 삭제할 수 없습니다. (HACCP 규정 준수)")
    
    @action(detail=False, methods=['get'])
    def recent_violations(self, request):
        """최근 기준 이탈 로그"""
        hours = int(request.query_params.get('hours', '24'))
        start_time = timezone.now() - timedelta(hours=hours)
        
        violations = CCPLog.objects.filter(
            measured_at__gte=start_time,
            status='out_of_limits'
        ).select_related('ccp', 'created_by').order_by('-measured_at')
        
        serializer = CCPLogSerializer(violations, many=True)
        return Response({
            'period': f'최근 {hours}시간',
            'violations': serializer.data,
            'total_count': violations.count()
        })
    
    @action(detail=False, methods=['get'])
    def pending_actions(self, request):
        """개선조치 필요한 로그"""
        pending_logs = CCPLog.objects.filter(
            status='out_of_limits',
            corrective_action_taken__isnull=True
        ).select_related('ccp', 'created_by').order_by('-measured_at')[:50]
        
        serializer = CCPLogSerializer(pending_logs, many=True)
        return Response({
            'pending_logs': serializer.data,
            'total_count': pending_logs.count()
        })
    
    @action(detail=False, methods=['get'])
    def verification_needed(self, request):
        """검증 필요한 로그"""
        verification_needed = CCPLog.objects.filter(
            status='corrective_action',
            verified_by__isnull=True
        ).select_related('ccp', 'corrective_action_by').order_by('-measured_at')[:50]
        
        serializer = CCPLogSerializer(verification_needed, many=True)
        return Response({
            'verification_needed': serializer.data,
            'total_count': verification_needed.count()
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """CCP 로그 통계"""
        # 최근 30일 통계
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_logs = CCPLog.objects.filter(measured_at__gte=thirty_days_ago)
        
        total_logs = recent_logs.count()
        within_limits = recent_logs.filter(status='within_limits').count()
        out_of_limits = recent_logs.filter(status='out_of_limits').count()
        corrective_actions = recent_logs.filter(status='corrective_action').count()
        
        # CCP 타입별 위반 현황
        violation_by_type = recent_logs.filter(
            status='out_of_limits'
        ).values(
            'ccp__ccp_type'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        # 가장 많이 위반되는 CCP
        frequent_violations = recent_logs.filter(
            status='out_of_limits'
        ).values(
            'ccp__name',
            'ccp__code'
        ).annotate(
            violation_count=Count('id')
        ).order_by('-violation_count')[:10]
        
        return Response({
            'analysis_period': '최근 30일',
            'overall_statistics': {
                'total_measurements': total_logs,
                'within_limits': within_limits,
                'out_of_limits': out_of_limits,
                'corrective_actions': corrective_actions,
                'compliance_rate': round((within_limits / total_logs * 100), 2) if total_logs > 0 else 0
            },
            'violations_by_type': list(violation_by_type),
            'frequent_violation_ccps': list(frequent_violations)
        })