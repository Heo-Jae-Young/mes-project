from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Prefetch
from core.models import BOM, FinishedProduct, RawMaterial
from core.serializers.bom_serializers import (
    BOMCreateSerializer, BOMUpdateSerializer, BOMListSerializer, 
    BOMDetailSerializer, ProductBOMSummarySerializer
)


class BOMViewSet(viewsets.ModelViewSet):
    """BOM (Bill of Materials) 관리 ViewSet"""
    
    queryset = BOM.objects.select_related(
        'finished_product', 'raw_material', 'created_by'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['finished_product', 'raw_material', 'is_active']
    search_fields = [
        'finished_product__name', 'finished_product__code',
        'raw_material__name', 'raw_material__code'
    ]
    ordering_fields = ['created_at', 'quantity_per_unit']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BOMCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return BOMUpdateSerializer
        elif self.action == 'retrieve':
            return BOMDetailSerializer
        return BOMListSerializer
    
    def get_queryset(self):
        """역할별 BOM 조회 권한"""
        user = self.request.user
        
        # 작업자는 활성 BOM만 조회 가능
        if user.role == 'operator':
            return self.queryset.filter(is_active=True)
            
        return self.queryset
    
    @action(detail=False, methods=['get'])
    def by_product(self, request):
        """제품별 BOM 목록 조회"""
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response(
                {'error': 'product_id 파라미터가 필요합니다'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = FinishedProduct.objects.get(id=product_id)
        except FinishedProduct.DoesNotExist:
            return Response(
                {'error': '존재하지 않는 제품입니다'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        bom_items = self.get_queryset().filter(finished_product=product)
        
        # 생산 수량이 제공된 경우 총 소요량 계산
        production_quantity = request.query_params.get('production_quantity', 1)
        
        serializer = ProductBOMSummarySerializer(bom_items, many=True)
        
        # 총 소요량 계산
        bom_with_totals = []
        for item, bom_data in zip(bom_items, serializer.data):
            bom_data['total_required_quantity'] = item.calculate_total_required_quantity(
                int(production_quantity)
            )
            bom_with_totals.append(bom_data)
        
        return Response({
            'product_name': product.name,
            'product_code': product.code,
            'production_quantity': int(production_quantity),
            'bom_items': bom_with_totals,
            'total_items': len(bom_with_totals)
        })
    
    @action(detail=False, methods=['get'])
    def calculate_requirements(self, request):
        """특정 제품의 생산 수량에 따른 원자재 소요량 계산"""
        product_id = request.query_params.get('product_id')
        production_quantity = request.query_params.get('production_quantity', 1)
        
        if not product_id:
            return Response(
                {'error': 'product_id 파라미터가 필요합니다'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = FinishedProduct.objects.get(id=product_id)
            production_quantity = int(production_quantity)
        except FinishedProduct.DoesNotExist:
            return Response(
                {'error': '존재하지 않는 제품입니다'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError:
            return Response(
                {'error': '유효한 생산 수량을 입력해주세요'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        bom_items = self.get_queryset().filter(
            finished_product=product, 
            is_active=True
        )
        
        requirements = []
        total_cost_estimate = 0
        
        for bom in bom_items:
            required_quantity = bom.calculate_total_required_quantity(production_quantity)
            
            requirements.append({
                'raw_material': {
                    'id': str(bom.raw_material.id),
                    'name': bom.raw_material.name,
                    'code': bom.raw_material.code,
                    'category': bom.raw_material.category
                },
                'quantity_per_unit': bom.quantity_per_unit,
                'unit': bom.unit,
                'total_required_quantity': required_quantity,
                'notes': bom.notes
            })
        
        return Response({
            'product': {
                'id': str(product.id),
                'name': product.name,
                'code': product.code
            },
            'production_quantity': production_quantity,
            'material_requirements': requirements,
            'total_material_types': len(requirements)
        })
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """제품의 BOM을 일괄 등록"""
        product_id = request.data.get('product_id')
        bom_items = request.data.get('bom_items', [])
        
        if not product_id or not bom_items:
            return Response(
                {'error': 'product_id와 bom_items가 필요합니다'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = FinishedProduct.objects.get(id=product_id)
        except FinishedProduct.DoesNotExist:
            return Response(
                {'error': '존재하지 않는 제품입니다'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        created_items = []
        errors = []
        
        for idx, item_data in enumerate(bom_items):
            item_data['finished_product'] = product_id
            serializer = BOMCreateSerializer(data=item_data, context={'request': request})
            
            if serializer.is_valid():
                bom_item = serializer.save()
                created_items.append(BOMDetailSerializer(bom_item).data)
            else:
                errors.append({
                    'index': idx,
                    'errors': serializer.errors
                })
        
        return Response({
            'created_items': created_items,
            'errors': errors,
            'success_count': len(created_items),
            'error_count': len(errors)
        }, status=status.HTTP_201_CREATED if created_items else status.HTTP_400_BAD_REQUEST)
    
    def perform_destroy(self, instance):
        """BOM 삭제 시 추가 검증"""
        # 현재 생산 중인 주문이 있는지 확인 (진행 중인 상태만 체크)
        active_orders = instance.finished_product.production_orders.filter(
            status='in_progress'  # planned 상태는 제외하고 실제 진행 중인 것만 체크
        )
        
        if active_orders.exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                "detail": f"현재 생산 중인 주문이 있는 제품의 BOM은 삭제할 수 없습니다. (생산 중인 주문: {active_orders.count()}개)"
            })
        
        super().perform_destroy(instance)