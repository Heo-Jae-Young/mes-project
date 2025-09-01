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


class CCPViewSet(viewsets.ModelViewSet):
    """중요 관리점(CCP) 관리 ViewSet"""
    
    queryset = CCP.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['ccp_type', 'finished_product', 'is_active']
    search_fields = ['name', 'code', 'description', 'process_step']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CCPCreateSerializer
        return CCPSerializer
    
    def get_queryset(self):
        """역할별 CCP 조회 권한"""
        user = self.request.user
        
        # 감사자는 모든 CCP 조회 가능
        if user.role == 'auditor':
            return CCP.objects.all()
        
        # 작업자는 활성 CCP만 조회
        if user.role == 'operator':
            return CCP.objects.filter(is_active=True)
            
        return CCP.objects.all()
    
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
        """CCP 규정 준수 보고서"""
        ccp = self.get_object()
        
        # 분석 기간 (기본 30일)
        days = int(request.query_params.get('days', '30'))
        start_date = timezone.now() - timedelta(days=days)
        
        logs = ccp.logs.filter(measured_at__gte=start_date)
        
        if not logs.exists():
            return Response({
                'ccp_name': ccp.name,
                'analysis_period': f'최근 {days}일',
                'message': '해당 기간에 모니터링 로그가 없습니다.'
            })
        
        total_logs = logs.count()
        within_limits = logs.filter(status='within_limits').count()
        out_of_limits = logs.filter(status='out_of_limits').count()
        corrective_action = logs.filter(status='corrective_action').count()
        
        compliance_rate = (within_limits / total_logs * 100) if total_logs > 0 else 0
        
        # 일별 로그 수 분포
        daily_logs = logs.extra({
            'date': 'DATE(measured_at)'
        }).values('date').annotate(
            count=Count('id'),
            out_of_limits_count=Count('id', filter=Q(status='out_of_limits'))
        ).order_by('date')
        
        # 편차 분석
        deviation_analysis = []
        if ccp.critical_limit_min or ccp.critical_limit_max:
            out_of_limit_logs = logs.filter(status='out_of_limits')
            for log in out_of_limit_logs:
                measured = float(log.measured_value)
                deviation = 0
                
                if ccp.critical_limit_min and measured < float(ccp.critical_limit_min):
                    deviation = measured - float(ccp.critical_limit_min)
                elif ccp.critical_limit_max and measured > float(ccp.critical_limit_max):
                    deviation = measured - float(ccp.critical_limit_max)
                
                deviation_analysis.append({
                    'measured_at': log.measured_at,
                    'measured_value': measured,
                    'deviation': deviation,
                    'corrective_action': log.corrective_action_taken
                })
        
        return Response({
            'ccp_info': {
                'name': ccp.name,
                'code': ccp.code,
                'type': ccp.get_ccp_type_display(),
                'critical_limits': {
                    'min': ccp.critical_limit_min,
                    'max': ccp.critical_limit_max
                }
            },
            'analysis_period': f'최근 {days}일',
            'compliance_summary': {
                'total_measurements': total_logs,
                'within_limits': within_limits,
                'out_of_limits': out_of_limits,
                'corrective_actions': corrective_action,
                'compliance_rate': round(compliance_rate, 2)
            },
            'daily_monitoring': list(daily_logs),
            'deviation_incidents': deviation_analysis[:10]  # 최근 10건만
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
        start_time = timezone.now() - timedelta(hours=hours)
        
        # 최근 기준 이탈 로그가 있는 CCP들
        critical_ccps = CCP.objects.filter(
            logs__measured_at__gte=start_time,
            logs__status='out_of_limits',
            is_active=True
        ).distinct()
        
        alerts = []
        for ccp in critical_ccps:
            recent_violations = ccp.logs.filter(
                measured_at__gte=start_time,
                status='out_of_limits'
            ).order_by('-measured_at')[:5]
            
            alerts.append({
                'ccp_id': ccp.id,
                'ccp_name': ccp.name,
                'ccp_code': ccp.code,
                'process_step': ccp.process_step,
                'violation_count': recent_violations.count(),
                'latest_violation': {
                    'measured_at': recent_violations.first().measured_at,
                    'measured_value': recent_violations.first().measured_value,
                    'deviation_notes': recent_violations.first().deviation_notes
                } if recent_violations.exists() else None
            })
        
        return Response({
            'alert_period': f'최근 {hours}시간',
            'critical_ccps': alerts,
            'total_alerts': len(alerts)
        })


class CCPLogViewSet(viewsets.ModelViewSet):
    """CCP 모니터링 로그 ViewSet - 불변 데이터"""
    
    queryset = CCPLog.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'ccp', 'production_order', 'is_within_limits']
    search_fields = ['ccp__name', 'deviation_notes', 'corrective_action_taken']
    ordering_fields = ['measured_at', 'created_at']
    ordering = ['-measured_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CCPLogCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CCPLogUpdateSerializer  # 개선조치 정보만 수정 가능
        return CCPLogSerializer
    
    def get_queryset(self):
        """로그 조회 필터링"""
        queryset = CCPLog.objects.select_related(
            'ccp', 'production_order', 'created_by'
        )
        
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