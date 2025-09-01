from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta, date
from core.models import RawMaterial, MaterialLot
from core.serializers import RawMaterialSerializer, MaterialLotSerializer, MaterialLotCreateSerializer


class RawMaterialViewSet(viewsets.ModelViewSet):
    """원자재 카탈로그 관리 ViewSet"""
    
    queryset = RawMaterial.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'supplier', 'is_active']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        return RawMaterialSerializer
    
    def get_queryset(self):
        """역할별 원자재 조회 권한"""
        user = self.request.user
        
        # 작업자는 활성 원자재만 조회 가능
        if user.role == 'operator':
            return RawMaterial.objects.filter(is_active=True)
            
        return RawMaterial.objects.all()
    
    @action(detail=True, methods=['get'])
    def lots(self, request, pk=None):
        """특정 원자재의 로트 목록"""
        material = self.get_object()
        
        # 상태별 필터링
        status_filter = request.query_params.get('status')
        queryset = material.lots.all()
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # 최신순 정렬, 최근 100개만
        lots = queryset.order_by('-received_date')[:100]
        
        serializer = MaterialLotSerializer(lots, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def inventory(self, request, pk=None):
        """특정 원자재의 재고 현황"""
        material = self.get_object()
        
        # 현재 보유 로트들
        current_lots = material.lots.filter(
            status__in=['received', 'in_storage', 'in_use'],
            quantity_current__gt=0
        )
        
        total_quantity = current_lots.aggregate(
            total=Sum('quantity_current')
        )['total'] or 0
        
        # 유통기한별 분류
        today = date.today()
        near_expiry = current_lots.filter(
            expiry_date__lte=today + timedelta(days=30)
        ).count()
        
        expired = current_lots.filter(
            expiry_date__lt=today
        ).count()
        
        return Response({
            'material_name': material.name,
            'material_code': material.code,
            'total_quantity': total_quantity,
            'unit': material.unit,
            'active_lots': current_lots.count(),
            'near_expiry_lots': near_expiry,
            'expired_lots': expired,
            'storage_requirements': {
                'temp_min': material.storage_temp_min,
                'temp_max': material.storage_temp_max,
                'shelf_life_days': material.shelf_life_days
            }
        })
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """원자재 카테고리 목록"""
        categories = [
            {'key': key, 'value': value} 
            for key, value in RawMaterial.CATEGORY_CHOICES
        ]
        return Response(categories)
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """재고 부족 원자재 목록"""
        # 임계값은 쿼리 파라미터로 받거나 기본값 사용
        threshold = float(request.query_params.get('threshold', '10.0'))
        
        low_stock_materials = []
        
        for material in RawMaterial.objects.filter(is_active=True):
            current_stock = material.lots.filter(
                status__in=['received', 'in_storage'],
                quantity_current__gt=0
            ).aggregate(
                total=Sum('quantity_current')
            )['total'] or 0
            
            if current_stock <= threshold:
                low_stock_materials.append({
                    'id': material.id,
                    'name': material.name,
                    'code': material.code,
                    'current_stock': current_stock,
                    'unit': material.unit,
                    'supplier': material.supplier.name,
                    'category': material.get_category_display()
                })
        
        return Response(low_stock_materials)


class MaterialLotViewSet(viewsets.ModelViewSet):
    """원자재 로트 관리 ViewSet - 추적성 핵심"""
    
    queryset = MaterialLot.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'raw_material', 'supplier', 'quality_test_passed']
    search_fields = ['lot_number', 'raw_material__name', 'supplier__name']
    ordering_fields = ['received_date', 'expiry_date', 'created_at']
    ordering = ['-received_date']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MaterialLotCreateSerializer
        return MaterialLotSerializer
    
    def get_queryset(self):
        """로트 조회 필터링"""
        queryset = MaterialLot.objects.select_related(
            'raw_material', 'supplier', 'created_by'
        )
        
        # 날짜 범위 필터
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(received_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(received_date__lte=end_date)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def consume(self, request, pk=None):
        """로트 소비/사용"""
        lot = self.get_object()
        consume_quantity = float(request.data.get('quantity', 0))
        
        if consume_quantity <= 0:
            return Response(
                {'detail': '소비 수량은 0보다 커야 합니다.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if consume_quantity > lot.quantity_current:
            return Response(
                {'detail': '소비 수량이 현재 수량을 초과합니다.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 수량 차감
        lot.quantity_current -= consume_quantity
        
        # 상태 업데이트
        if lot.quantity_current == 0:
            lot.status = 'used'
        else:
            lot.status = 'in_use'
        
        lot.save()
        
        # 사용 기록 로깅 (향후 별도 모델로 확장 가능)
        return Response({
            'detail': f'{consume_quantity}{lot.raw_material.unit} 소비 처리되었습니다.',
            'remaining_quantity': lot.quantity_current,
            'new_status': lot.status
        })
    
    @action(detail=True, methods=['get'])
    def traceability(self, request, pk=None):
        """로트 추적성 정보"""
        lot = self.get_object()
        
        # 기본 추적 정보
        trace_data = {
            'lot_info': {
                'lot_number': lot.lot_number,
                'raw_material': lot.raw_material.name,
                'supplier': lot.supplier.name,
                'received_date': lot.received_date,
                'expiry_date': lot.expiry_date
            },
            'quality_control': {
                'test_passed': lot.quality_test_passed,
                'test_date': lot.quality_test_date,
                'test_notes': lot.quality_test_notes,
                'temperature_at_receipt': lot.temperature_at_receipt
            },
            'usage_history': {
                'original_quantity': lot.quantity_received,
                'current_quantity': lot.quantity_current,
                'consumed_quantity': lot.quantity_received - lot.quantity_current,
                'usage_rate': ((lot.quantity_received - lot.quantity_current) / lot.quantity_received * 100) if lot.quantity_received > 0 else 0
            }
        }
        
        # 향후 생산오더 연결 정보도 추가 가능
        # trace_data['production_usage'] = ProductionOrder.objects.filter(...)
        
        return Response(trace_data)
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """유통기한 임박 로트"""
        days_ahead = int(request.query_params.get('days', '7'))
        threshold_date = date.today() + timedelta(days=days_ahead)
        
        expiring_lots = MaterialLot.objects.filter(
            expiry_date__lte=threshold_date,
            expiry_date__gte=date.today(),
            status__in=['received', 'in_storage', 'in_use'],
            quantity_current__gt=0
        ).select_related('raw_material', 'supplier')
        
        serializer = MaterialLotSerializer(expiring_lots, many=True)
        return Response({
            'threshold_days': days_ahead,
            'expiring_lots': serializer.data,
            'total_count': expiring_lots.count()
        })
    
    @action(detail=False, methods=['get'])
    def quality_summary(self, request):
        """품질검사 요약"""
        # 최근 30일 품질검사 현황
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        recent_lots = MaterialLot.objects.filter(
            received_date__gte=thirty_days_ago
        )
        
        total_lots = recent_lots.count()
        passed_lots = recent_lots.filter(quality_test_passed=True).count()
        failed_lots = recent_lots.filter(quality_test_passed=False).count()
        pending_lots = recent_lots.filter(quality_test_passed__isnull=True).count()
        
        pass_rate = (passed_lots / total_lots * 100) if total_lots > 0 else 0
        
        return Response({
            'period': '최근 30일',
            'total_lots': total_lots,
            'quality_results': {
                'passed': passed_lots,
                'failed': failed_lots,
                'pending': pending_lots,
                'pass_rate': round(pass_rate, 2)
            },
            'failed_suppliers': list(
                recent_lots.filter(quality_test_passed=False)
                .values('supplier__name')
                .annotate(count=Count('id'))
                .order_by('-count')[:5]
            )
        })