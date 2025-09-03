from datetime import datetime, timedelta
from decimal import Decimal
from django.db import models
from django.db.models import Count, Q, Avg
from django.utils import timezone
from rest_framework.exceptions import ValidationError, PermissionDenied

from core.models import CCP, CCPLog, ProductionOrder
from core.constants import (
    DUPLICATE_MEASUREMENT_THRESHOLD_MINUTES,
    VERIFICATION_REQUIRED_HOURS,
    CRITICAL_ALERT_HOURS,
    CONSECUTIVE_VIOLATION_DETECTION_HOURS,
    CONSECUTIVE_VIOLATION_THRESHOLD
)


class HaccpService:
    """HACCP 7원칙 준수를 위한 핵심 비즈니스 로직"""

    def validate_ccp_log_creation(self, ccp_id, measured_value, measured_at, created_by):
        """
        CCP 로그 생성 전 검증 (비즈니스 로직 처리)
        - CCP 존재 및 활성 상태 확인
        - 측정값 유효성 검증  
        - 권한 확인 (operator 이상)
        - 중복 측정 방지
        
        Returns:
            CCP: 검증된 CCP 인스턴스
        """
        # CCP 조회 및 활성 상태 확인
        try:
            ccp = CCP.objects.get(id=ccp_id, is_active=True)
        except CCP.DoesNotExist:
            raise ValidationError('존재하지 않거나 비활성화된 CCP입니다.')
        
        # 권한 확인
        if created_by.role not in ['admin', 'quality_manager', 'operator']:
            raise PermissionDenied('CCP 로그 기록 권한이 없습니다.')
        
        # 시간 검증
        if measured_at > timezone.now():
            raise ValidationError('미래 시점의 측정 시간은 입력할 수 없습니다.')
        
        # 중복 측정 방지 (같은 CCP, 같은 시간대)
        time_threshold = measured_at - timedelta(minutes=DUPLICATE_MEASUREMENT_THRESHOLD_MINUTES)
        existing_log = CCPLog.objects.filter(
            ccp=ccp,
            measured_at__gte=time_threshold,
            measured_at__lte=measured_at + timedelta(minutes=DUPLICATE_MEASUREMENT_THRESHOLD_MINUTES)
        ).exists()
        
        if existing_log:
            raise ValidationError('동일 시간대에 이미 측정 기록이 존재합니다.')
            
        return ccp

    def calculate_compliance_score(self, production_order=None, ccp=None, date_from=None, date_to=None):
        """
        HACCP 컴플라이언스 점수 계산
        - 기준 내 측정값 비율
        - 개선조치 적시성
        - 검증 완료율
        """
        queryset = CCPLog.objects.all()
        
        if production_order:
            queryset = queryset.filter(production_order=production_order)
        if ccp:
            queryset = queryset.filter(ccp=ccp)
        if date_from:
            queryset = queryset.filter(measured_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(measured_at__lte=date_to)
        
        total_logs = queryset.count()
        if total_logs == 0:
            return {
                'compliance_score': 100,
                'total_measurements': 0,
                'within_limits_count': 0,
                'out_of_limits_count': 0,
                'verification_rate': 0
            }
        
        within_limits_count = queryset.filter(is_within_limits=True).count()
        out_of_limits_count = total_logs - within_limits_count
        verified_count = queryset.filter(verified_by__isnull=False).count()
        
        compliance_rate = (within_limits_count / total_logs) * 100
        verification_rate = (verified_count / total_logs) * 100
        
        # 가중 점수 계산 (컴플라이언스 70%, 검증률 30%)
        compliance_score = (compliance_rate * 0.7) + (verification_rate * 0.3)
        
        return {
            'compliance_score': round(compliance_score, 2),
            'total_measurements': total_logs,
            'within_limits_count': within_limits_count,
            'out_of_limits_count': out_of_limits_count,
            'compliance_rate': round(compliance_rate, 2),
            'verification_rate': round(verification_rate, 2)
        }

    def get_critical_alerts(self, user=None, hours=CRITICAL_ALERT_HOURS):
        """
        중요 알림 목록 조회
        - 기준 이탈 미조치 항목
        - 검증 대기 항목
        - 연속 이탈 패턴
        """
        if user.role not in ['admin', 'quality_manager']:
            raise PermissionDenied('중요 알림 조회 권한이 없습니다.')
        
        alerts = []
        
        # 1. 기준 이탈 미조치 항목
        unresolved_deviations = CCPLog.objects.filter(
            is_within_limits=False,
            corrective_action_taken__isnull=True,
            measured_at__gte=timezone.now() - timedelta(hours=hours)
        ).select_related('ccp', 'production_order')
        
        for log in unresolved_deviations:
            alerts.append({
                'type': 'deviation',
                'severity': 'high',
                'message': f'{log.ccp.name} 기준 이탈 - 개선조치 필요',
                'ccp_code': log.ccp.code,
                'measured_at': log.measured_at,
                'log_id': str(log.id)
            })
        
        # 2. 검증 대기 항목 (설정 시간 경과)
        pending_verification = CCPLog.objects.filter(
            verified_by__isnull=True,
            measured_at__lte=timezone.now() - timedelta(hours=VERIFICATION_REQUIRED_HOURS)
        ).select_related('ccp')
        
        for log in pending_verification:
            alerts.append({
                'type': 'verification_pending',
                'severity': 'medium',
                'message': f'{log.ccp.name} 검증 대기 중',
                'ccp_code': log.ccp.code,
                'measured_at': log.measured_at,
                'log_id': str(log.id)
            })
        
        # 3. 연속 이탈 패턴 감지 (같은 CCP에서 설정 횟수 연속)
        recent_logs = CCPLog.objects.filter(
            measured_at__gte=timezone.now() - timedelta(hours=CONSECUTIVE_VIOLATION_DETECTION_HOURS)
        ).order_by('ccp', '-measured_at')
        
        ccp_consecutive_count = {}
        for log in recent_logs:
            ccp_id = log.ccp.id
            if ccp_id not in ccp_consecutive_count:
                ccp_consecutive_count[ccp_id] = {'count': 0, 'ccp': log.ccp}
            
            if not log.is_within_limits:
                ccp_consecutive_count[ccp_id]['count'] += 1
            else:
                ccp_consecutive_count[ccp_id]['count'] = 0
        
        for ccp_id, data in ccp_consecutive_count.items():
            if data['count'] >= CONSECUTIVE_VIOLATION_THRESHOLD:
                alerts.append({
                    'type': 'consecutive_deviation',
                    'severity': 'critical',
                    'message': f'{data["ccp"].name} 연속 {data["count"]}회 기준 이탈',
                    'ccp_code': data['ccp'].code,
                    'consecutive_count': data['count']
                })
        
        result = {
            'alert_period': f'최근 {hours}시간',
            'critical_alerts': sorted(alerts, key=lambda x: {'critical': 0, 'high': 1, 'medium': 2}[x['severity']]),
            'total_alerts': len(alerts)
        }
        return result

    def generate_compliance_report(self, date_from, date_to, user):
        """
        HACCP 컴플라이언스 보고서 생성
        """
        if user.role not in ['admin', 'quality_manager']:
            raise PermissionDenied('컴플라이언스 보고서 생성 권한이 없습니다.')
        
        # 기간 내 전체 통계
        overall_stats = self.calculate_compliance_score(
            date_from=date_from,
            date_to=date_to
        )
        
        # CCP별 상세 통계
        ccp_stats = []
        active_ccps = CCP.objects.filter(is_active=True)
        
        for ccp in active_ccps:
            ccp_compliance = self.calculate_compliance_score(
                ccp=ccp,
                date_from=date_from,
                date_to=date_to
            )
            
            # 평균 측정값 계산
            avg_value = CCPLog.objects.filter(
                ccp=ccp,
                measured_at__gte=date_from,
                measured_at__lte=date_to
            ).aggregate(avg_value=Avg('measured_value'))['avg_value']
            
            ccp_stats.append({
                'ccp_name': ccp.name,
                'ccp_code': ccp.code,
                'ccp_type': ccp.get_ccp_type_display(),
                'critical_limit_min': ccp.critical_limit_min,
                'critical_limit_max': ccp.critical_limit_max,
                'avg_measured_value': round(float(avg_value) if avg_value else 0, 3),
                **ccp_compliance
            })
        
        # 트렌드 분석 (주간 단위)
        trend_data = []
        current_date = date_from
        
        while current_date <= date_to:
            week_end = min(current_date + timedelta(days=6), date_to)
            
            week_stats = self.calculate_compliance_score(
                date_from=current_date,
                date_to=week_end
            )
            
            trend_data.append({
                'week_start': current_date,
                'week_end': week_end,
                'compliance_score': week_stats['compliance_score'],
                'total_measurements': week_stats['total_measurements']
            })
            
            current_date += timedelta(days=7)
        
        return {
            'report_period': {
                'from': date_from,
                'to': date_to
            },
            'overall_statistics': overall_stats,
            'ccp_statistics': ccp_stats,
            'trend_analysis': trend_data,
            'generated_at': timezone.now(),
            'generated_by': user.username
        }


class HaccpQueryService:
    """HACCP 데이터 조회 최적화 서비스"""

    def get_ccp_logs_for_user(self, user, **filters):
        """사용자 역할에 따른 CCP 로그 조회"""
        queryset = CCPLog.objects.select_related('ccp', 'created_by', 'production_order')
        
        # 역할별 필터링
        if user.role == 'operator':
            # 운영자는 자신이 생성한 로그만 조회
            queryset = queryset.filter(created_by=user)
        elif user.role not in ['admin', 'quality_manager']:
            # 기타 역할은 접근 불가
            return CCPLog.objects.none()
        
        # 추가 필터 적용
        if 'ccp_id' in filters:
            queryset = queryset.filter(ccp_id=filters['ccp_id'])
        if 'production_order_id' in filters:
            queryset = queryset.filter(production_order_id=filters['production_order_id'])
        if 'date_from' in filters:
            queryset = queryset.filter(measured_at__gte=filters['date_from'])
        if 'date_to' in filters:
            queryset = queryset.filter(measured_at__lte=filters['date_to'])
        if 'is_within_limits' in filters:
            queryset = queryset.filter(is_within_limits=filters['is_within_limits'])
        
        return queryset.order_by('-measured_at')

    def get_ccps_for_user(self, user):
        """사용자가 접근 가능한 CCP 목록"""
        if user.role in ['admin', 'quality_manager']:
            return CCP.objects.filter(is_active=True)
        elif user.role == 'operator':
            # 운영자는 자신이 담당하는 CCP만 (담당자 필드 기반)
            return CCP.objects.filter(
                is_active=True,
                responsible_person__icontains=user.username
            )
        else:
            return CCP.objects.none()