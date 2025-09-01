from datetime import datetime, timedelta
from decimal import Decimal
from django.db import models
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from rest_framework.exceptions import ValidationError, PermissionDenied

from core.models import Supplier, MaterialLot, RawMaterial


class SupplierService:
    """공급업체 관리 및 평가 비즈니스 로직"""

    def validate_supplier_creation(self, supplier_data, user):
        """
        공급업체 등록 전 검증
        - 중복 확인
        - 필수 정보 검증
        - 권한 확인
        """
        if user.role not in ['admin', 'quality_manager']:
            raise PermissionDenied('공급업체 등록 권한이 없습니다.')
        
        # 공급업체 코드 중복 확인
        if Supplier.objects.filter(code=supplier_data.get('code')).exists():
            raise ValidationError('이미 존재하는 공급업체 코드입니다.')
        
        # 이메일 중복 확인
        if Supplier.objects.filter(email=supplier_data.get('email')).exists():
            raise ValidationError('이미 등록된 이메일 주소입니다.')
        
        # 필수 인증 정보 확인 (HACCP 환경에서는 중요)
        certification = supplier_data.get('certification', '')
        if not certification or 'HACCP' not in certification.upper():
            raise ValidationError('HACCP 인증 정보는 필수입니다.')

    def evaluate_supplier_performance(self, supplier, date_from=None, date_to=None):
        """
        공급업체 성과 평가
        - 품질 점수 (품질검사 통과율)
        - 납기 점수 (정시 납기율)
        - 컴플라이언스 점수 (인증 상태, 규정 준수)
        """
        if not date_from:
            date_from = timezone.now() - timedelta(days=90)  # 최근 3개월
        if not date_to:
            date_to = timezone.now()
        
        # 해당 기간 내 공급받은 로트들
        material_lots = MaterialLot.objects.filter(
            supplier=supplier,
            received_date__range=[date_from, date_to]
        )
        
        if not material_lots.exists():
            return {
                'overall_score': 0,
                'quality_score': 0,
                'delivery_score': 0,
                'compliance_score': 0,
                'total_deliveries': 0,
                'evaluation_period': {'from': date_from, 'to': date_to}
            }
        
        # 1. 품질 점수 계산
        total_lots = material_lots.count()
        quality_passed = material_lots.filter(quality_test_passed=True).count()
        quality_score = (quality_passed / total_lots) * 100 if total_lots > 0 else 0
        
        # 2. 납기 점수 계산 (임시: 유통기한 대비 빠른 납품 여부로 계산)
        on_time_deliveries = 0
        for lot in material_lots:
            # 실제로는 약속 납기일과 실제 납품일 비교가 필요
            # 현재는 유통기한 대비 충분한 여유로 납품했는지로 판단
            if lot.expiry_date:
                days_to_expiry = (lot.expiry_date - lot.received_date.date()).days
                expected_shelf_life = lot.raw_material.shelf_life_days or 365
                if days_to_expiry >= expected_shelf_life * 0.8:  # 80% 이상 잔여기한
                    on_time_deliveries += 1
        
        delivery_score = (on_time_deliveries / total_lots) * 100 if total_lots > 0 else 0
        
        # 3. 컴플라이언스 점수 계산
        compliance_factors = []
        
        # HACCP 인증 여부
        if 'HACCP' in supplier.certification.upper():
            compliance_factors.append(25)
        
        # ISO 인증 여부
        if 'ISO' in supplier.certification.upper():
            compliance_factors.append(15)
        
        # 활성 상태 유지
        if supplier.status == 'active':
            compliance_factors.append(20)
        
        # 연락처 정보 완성도
        if all([supplier.contact_person, supplier.email, supplier.phone, supplier.address]):
            compliance_factors.append(15)
        
        # 최근 정보 업데이트 (6개월 이내)
        if supplier.updated_at >= timezone.now() - timedelta(days=180):
            compliance_factors.append(25)
        
        compliance_score = sum(compliance_factors)
        
        # 전체 점수 계산 (가중 평균)
        overall_score = (quality_score * 0.4) + (delivery_score * 0.4) + (compliance_score * 0.2)
        
        return {
            'overall_score': round(overall_score, 2),
            'quality_score': round(quality_score, 2),
            'delivery_score': round(delivery_score, 2),
            'compliance_score': round(compliance_score, 2),
            'total_deliveries': total_lots,
            'quality_passed_count': quality_passed,
            'on_time_delivery_count': on_time_deliveries,
            'evaluation_period': {'from': date_from, 'to': date_to}
        }

    def get_supplier_risk_assessment(self, supplier):
        """
        공급업체 리스크 평가
        - 납품 중단 리스크
        - 품질 리스크
        - 컴플라이언스 리스크
        """
        risk_factors = []
        risk_score = 0
        
        # 1. 최근 납품 이력 확인
        recent_deliveries = MaterialLot.objects.filter(
            supplier=supplier,
            received_date__gte=timezone.now() - timedelta(days=60)
        ).count()
        
        if recent_deliveries == 0:
            risk_factors.append('최근 2개월간 납품 이력 없음')
            risk_score += 30
        elif recent_deliveries < 3:
            risk_factors.append('납품 빈도 낮음')
            risk_score += 15
        
        # 2. 품질 문제 확인
        failed_quality_lots = MaterialLot.objects.filter(
            supplier=supplier,
            quality_test_passed=False,
            received_date__gte=timezone.now() - timedelta(days=90)
        ).count()
        
        if failed_quality_lots > 0:
            risk_factors.append(f'최근 3개월간 품질검사 실패 {failed_quality_lots}건')
            risk_score += failed_quality_lots * 10
        
        # 3. 인증 만료 리스크
        if not supplier.certification or 'HACCP' not in supplier.certification.upper():
            risk_factors.append('HACCP 인증 누락')
            risk_score += 40
        
        # 4. 정보 업데이트 상태
        if supplier.updated_at < timezone.now() - timedelta(days=365):
            risk_factors.append('1년 이상 정보 미업데이트')
            risk_score += 20
        
        # 5. 상태 확인
        if supplier.status != 'active':
            risk_factors.append(f'비활성 상태: {supplier.get_status_display()}')
            risk_score += 50
        
        # 리스크 레벨 결정
        if risk_score >= 70:
            risk_level = 'high'
        elif risk_score >= 40:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return {
            'risk_level': risk_level,
            'risk_score': min(risk_score, 100),  # 최대 100점
            'risk_factors': risk_factors,
            'recommendations': self._get_risk_recommendations(risk_level, risk_factors)
        }

    def _get_risk_recommendations(self, risk_level, risk_factors):
        """리스크 레벨에 따른 권장 조치사항"""
        recommendations = []
        
        if risk_level == 'high':
            recommendations.append('즉시 대체 공급업체 확보 필요')
            recommendations.append('현재 공급업체와 긴급 회의 요청')
        
        if '품질검사 실패' in ' '.join(risk_factors):
            recommendations.append('품질 개선 계획 요구')
            recommendations.append('입고 검사 강화')
        
        if 'HACCP 인증 누락' in risk_factors:
            recommendations.append('HACCP 인증 취득 요구')
            recommendations.append('인증 취득 일정 확인')
        
        if '납품 이력 없음' in ' '.join(risk_factors):
            recommendations.append('계약 상태 점검')
            recommendations.append('소통 채널 확인')
        
        return recommendations


class SupplierQueryService:
    """공급업체 조회 최적화 서비스"""

    def get_suppliers_for_user(self, user, **filters):
        """사용자 역할에 따른 공급업체 조회"""
        if user.role not in ['admin', 'quality_manager', 'operator']:
            return Supplier.objects.none()
        
        queryset = Supplier.objects.all()
        
        # 운영자는 활성 공급업체만 조회
        if user.role == 'operator':
            queryset = queryset.filter(status='active')
        
        # 필터 적용
        if 'status' in filters:
            queryset = queryset.filter(status=filters['status'])
        if 'certification_contains' in filters:
            queryset = queryset.filter(certification__icontains=filters['certification_contains'])
        
        return queryset.order_by('name')

    def get_supplier_statistics(self, user):
        """공급업체 통계 정보"""
        if user.role not in ['admin', 'quality_manager']:
            raise PermissionDenied('통계 조회 권한이 없습니다.')
        
        total_suppliers = Supplier.objects.count()
        active_suppliers = Supplier.objects.filter(status='active').count()
        
        # 인증 현황
        haccp_certified = Supplier.objects.filter(
            certification__icontains='HACCP'
        ).count()
        
        iso_certified = Supplier.objects.filter(
            certification__icontains='ISO'
        ).count()
        
        # 최근 납품 현황
        recent_deliveries = MaterialLot.objects.filter(
            received_date__gte=timezone.now() - timedelta(days=30)
        ).values('supplier').distinct().count()
        
        return {
            'total_suppliers': total_suppliers,
            'active_suppliers': active_suppliers,
            'inactive_suppliers': total_suppliers - active_suppliers,
            'haccp_certified_count': haccp_certified,
            'iso_certified_count': iso_certified,
            'recent_active_suppliers': recent_deliveries,
            'certification_rate': round((haccp_certified / total_suppliers) * 100, 2) if total_suppliers > 0 else 0
        }


class SupplierAuditService:
    """공급업체 감사 및 모니터링 서비스"""

    def schedule_supplier_audit(self, supplier, audit_type, scheduled_date, user):
        """
        공급업체 감사 일정 등록
        - 정기 감사
        - 특별 감사 (품질 문제 발생 시)
        - 재인증 감사
        """
        if user.role not in ['admin', 'quality_manager']:
            raise PermissionDenied('감사 일정 등록 권한이 없습니다.')
        
        if scheduled_date <= timezone.now():
            raise ValidationError('감사 일정은 현재 시점 이후여야 합니다.')
        
        # TODO: SupplierAudit 모델 구현 필요
        # 현재는 로직만 구현
        
        return {
            'supplier': supplier.name,
            'audit_type': audit_type,
            'scheduled_date': scheduled_date,
            'status': 'scheduled',
            'created_by': user.username
        }

    def get_audit_checklist(self, audit_type):
        """감사 유형별 체크리스트 제공"""
        base_checklist = [
            'HACCP 인증서 유효성 확인',
            '생산 시설 위생 상태 점검',
            '품질관리 시스템 운영 확인',
            '원자재 보관 환경 점검',
            '직원 위생교육 이수 확인'
        ]
        
        if audit_type == 'quality_issue':
            base_checklist.extend([
                '품질 이슈 원인 분석 결과 확인',
                '개선 조치 계획 및 실행 상태 점검',
                '재발 방지 대책 수립 여부 확인'
            ])
        elif audit_type == 'recertification':
            base_checklist.extend([
                '인증 갱신 신청 상태 확인',
                '최신 규정 준수 여부 점검',
                '과거 감사 지적 사항 개선 여부 확인'
            ])
        
        return base_checklist