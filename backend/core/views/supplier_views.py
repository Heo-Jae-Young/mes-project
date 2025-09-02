from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from core.models import Supplier, MaterialLot
from core.serializers import SupplierSerializer, SupplierCreateSerializer, SupplierUpdateSerializer
from core.services.supplier_service import SupplierService, SupplierQueryService, SupplierAuditService


class SupplierViewSet(viewsets.ModelViewSet):
    """공급업체 관리 ViewSet"""
    
    queryset = Supplier.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['name', 'code', 'contact_person', 'email']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['-created_at']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.supplier_service = SupplierService()
        self.supplier_query_service = SupplierQueryService()
        self.supplier_audit_service = SupplierAuditService()
    
    def get_serializer_class(self):
        """액션에 따라 다른 Serializer 사용"""
        if self.action == 'create':
            return SupplierCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return SupplierUpdateSerializer
        return SupplierSerializer
    
    def get_queryset(self):
        """역할별 공급업체 조회 권한"""
        user = self.request.user
        
        # 작업자는 활성 공급업체만 조회 가능
        if user.role == 'operator':
            return Supplier.objects.filter(status='active')
            
        return Supplier.objects.all()
    
    def perform_create(self, serializer):
        """공급업체 생성 시 생성자 자동 설정"""
        serializer.save(created_by=self.request.user)
    
    def perform_destroy(self, instance):
        """공급업체 삭제 시 연관 데이터 확인"""
        # 원자재 로트가 있는 경우 삭제 불가
        if instance.material_lots.exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError("원자재 로트가 존재하는 공급업체는 삭제할 수 없습니다.")
        
        super().perform_destroy(instance)
    
    @action(detail=True, methods=['get'])
    def materials(self, request, pk=None):
        """특정 공급업체의 원자재 목록"""
        supplier = self.get_object()
        materials = supplier.raw_materials.filter(is_active=True)
        
        # 간단한 원자재 정보만 반환
        material_data = []
        for material in materials:
            material_data.append({
                'id': material.id,
                'name': material.name,
                'code': material.code,
                'category': material.category,
                'unit': material.unit,
                'is_active': material.is_active
            })
        
        return Response(material_data)
    
    @action(detail=True, methods=['get'])
    def material_lots(self, request, pk=None):
        """특정 공급업체의 원자재 로트 목록"""
        supplier = self.get_object()
        
        # 쿼리 파라미터로 상태 필터링
        status_filter = request.query_params.get('status')
        lots = supplier.material_lots.all()
        
        if status_filter:
            lots = lots.filter(status=status_filter)
        
        # 최근 50개만 반환
        lots = lots.order_by('-created_at')[:50]
        
        lot_data = []
        for lot in lots:
            lot_data.append({
                'id': lot.id,
                'lot_number': lot.lot_number,
                'raw_material_name': lot.raw_material.name,
                'received_date': lot.received_date,
                'expiry_date': lot.expiry_date,
                'quantity_current': lot.quantity_current,
                'status': lot.status,
                'quality_test_passed': lot.quality_test_passed
            })
        
        return Response(lot_data)
    
    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        """공급업체 성과 분석"""
        supplier = self.get_object()
        
        # 최근 6개월간 로트 분석
        from datetime import datetime, timedelta
        six_months_ago = datetime.now() - timedelta(days=180)
        
        lots = MaterialLot.objects.filter(
            supplier=supplier,
            received_date__gte=six_months_ago
        )
        
        total_lots = lots.count()
        quality_passed = lots.filter(quality_test_passed=True).count()
        quality_failed = lots.filter(quality_test_passed=False).count()
        quality_pending = lots.filter(quality_test_passed__isnull=True).count()
        
        # 평균 납기일 준수율 계산 (실제로는 더 복잡한 로직 필요)
        on_time_delivery = lots.filter(status='received').count()
        delivery_rate = (on_time_delivery / total_lots * 100) if total_lots > 0 else 0
        
        # 품질 합격률
        tested_lots = quality_passed + quality_failed
        quality_rate = (quality_passed / tested_lots * 100) if tested_lots > 0 else 0
        
        return Response({
            'supplier_name': supplier.name,
            'analysis_period': '최근 6개월',
            'total_lots': total_lots,
            'quality_summary': {
                'passed': quality_passed,
                'failed': quality_failed,
                'pending': quality_pending,
                'pass_rate': round(quality_rate, 2)
            },
            'delivery_performance': {
                'on_time_deliveries': on_time_delivery,
                'delivery_rate': round(delivery_rate, 2)
            }
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """공급업체 전체 통계"""
        total_suppliers = Supplier.objects.count()
        active_suppliers = Supplier.objects.filter(status='active').count()
        inactive_suppliers = Supplier.objects.filter(status='inactive').count()
        suspended_suppliers = Supplier.objects.filter(status='suspended').count()
        
        # 공급업체별 원자재 수
        suppliers_with_materials = Supplier.objects.annotate(
            material_count=Count('raw_materials')
        ).filter(material_count__gt=0).count()
        
        return Response({
            'total_suppliers': total_suppliers,
            'status_breakdown': {
                'active': active_suppliers,
                'inactive': inactive_suppliers,
                'suspended': suspended_suppliers
            },
            'suppliers_with_materials': suppliers_with_materials,
            'suppliers_without_materials': total_suppliers - suppliers_with_materials
        })