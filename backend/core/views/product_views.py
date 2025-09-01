from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from core.models import FinishedProduct, ProductionOrder
from core.serializers import FinishedProductSerializer, FinishedProductCreateSerializer, FinishedProductUpdateSerializer


class FinishedProductViewSet(viewsets.ModelViewSet):
    """완제품 관리 ViewSet"""
    
    queryset = FinishedProduct.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FinishedProductCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return FinishedProductUpdateSerializer
        return FinishedProductSerializer
    
    def get_queryset(self):
        """역할별 제품 조회 권한"""
        user = self.request.user
        
        # 작업자는 활성 제품만 조회 가능
        if user.role == 'operator':
            return FinishedProduct.objects.filter(is_active=True)
            
        return FinishedProduct.objects.all()
    
    def perform_destroy(self, instance):
        """제품 삭제 시 생산오더 확인"""
        if instance.production_orders.exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError("생산오더가 존재하는 제품은 삭제할 수 없습니다.")
        
        super().perform_destroy(instance)
    
    @action(detail=True, methods=['get'])
    def production_history(self, request, pk=None):
        """제품 생산 이력"""
        product = self.get_object()
        
        # 최근 생산오더 조회
        limit = int(request.query_params.get('limit', '20'))
        orders = product.production_orders.order_by('-created_at')[:limit]
        
        production_data = []
        for order in orders:
            production_data.append({
                'id': order.id,
                'order_number': order.order_number,
                'planned_quantity': order.planned_quantity,
                'produced_quantity': order.produced_quantity,
                'status': order.status,
                'planned_start_date': order.planned_start_date,
                'planned_end_date': order.planned_end_date,
                'actual_start_date': order.actual_start_date,
                'actual_end_date': order.actual_end_date,
                'completion_rate': (order.produced_quantity / order.planned_quantity * 100) if order.planned_quantity > 0 else 0
            })
        
        return Response({
            'product_name': product.name,
            'product_code': product.code,
            'production_history': production_data,
            'total_orders': product.production_orders.count()
        })
    
    @action(detail=True, methods=['get'])
    def production_statistics(self, request, pk=None):
        """제품 생산 통계"""
        product = self.get_object()
        
        # 전체 생산 통계
        all_orders = product.production_orders.all()
        total_orders = all_orders.count()
        completed_orders = all_orders.filter(status='completed').count()
        
        # 총 생산량
        total_produced = sum([order.produced_quantity for order in all_orders])
        total_planned = sum([order.planned_quantity for order in all_orders])
        
        # 평균 완료율
        avg_completion = (completed_orders / total_orders * 100) if total_orders > 0 else 0
        
        # 상태별 분포
        status_distribution = {}
        for choice in ProductionOrder.STATUS_CHOICES:
            status_key = choice[0]
            status_name = choice[1]
            count = all_orders.filter(status=status_key).count()
            status_distribution[status_name] = count
        
        # 최근 30일 생산 성과
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_orders = all_orders.filter(created_at__gte=thirty_days_ago)
        
        recent_produced = sum([order.produced_quantity for order in recent_orders])
        recent_completed = recent_orders.filter(status='completed').count()
        
        return Response({
            'product_info': {
                'name': product.name,
                'code': product.code,
                'version': product.version
            },
            'overall_statistics': {
                'total_orders': total_orders,
                'completed_orders': completed_orders,
                'completion_rate': round(avg_completion, 2),
                'total_produced': total_produced,
                'total_planned': total_planned,
                'production_efficiency': round((total_produced / total_planned * 100), 2) if total_planned > 0 else 0
            },
            'status_distribution': status_distribution,
            'recent_30_days': {
                'orders_count': recent_orders.count(),
                'completed_orders': recent_completed,
                'total_produced': recent_produced
            }
        })
    
    @action(detail=True, methods=['get'])
    def ccps(self, request, pk=None):
        """제품별 중요 관리점(CCP) 목록"""
        product = self.get_object()
        
        ccps = product.ccps.filter(is_active=True)
        
        ccp_data = []
        for ccp in ccps:
            # 최근 로그 통계
            recent_logs = ccp.logs.filter(
                measured_at__gte=datetime.now() - timedelta(days=30)
            )
            
            ccp_data.append({
                'id': ccp.id,
                'name': ccp.name,
                'code': ccp.code,
                'ccp_type': ccp.get_ccp_type_display(),
                'process_step': ccp.process_step,
                'critical_limits': {
                    'min': ccp.critical_limit_min,
                    'max': ccp.critical_limit_max
                },
                'monitoring_frequency': ccp.monitoring_frequency,
                'recent_performance': {
                    'total_logs': recent_logs.count(),
                    'out_of_limits': recent_logs.filter(status='out_of_limits').count(),
                    'compliance_rate': round(
                        (recent_logs.filter(status='within_limits').count() / recent_logs.count() * 100), 2
                    ) if recent_logs.count() > 0 else 0
                }
            })
        
        return Response({
            'product_name': product.name,
            'ccps': ccp_data,
            'total_ccps': len(ccp_data)
        })
    
    @action(detail=False, methods=['get'])
    def active_products(self, request):
        """활성 제품 목록 (간단 버전)"""
        products = FinishedProduct.objects.filter(is_active=True).only(
            'id', 'name', 'code', 'version', 'net_weight', 'packaging_type'
        )
        
        simple_products = []
        for product in products:
            simple_products.append({
                'id': product.id,
                'name': product.name,
                'code': product.code,
                'version': product.version,
                'net_weight': product.net_weight,
                'packaging_type': product.packaging_type
            })
        
        return Response(simple_products)
    
    @action(detail=False, methods=['get'])
    def product_catalog(self, request):
        """제품 카탈로그 (상세 정보 포함)"""
        products = FinishedProduct.objects.filter(is_active=True)
        
        catalog = []
        for product in products:
            # 최근 생산 정보
            latest_order = product.production_orders.order_by('-created_at').first()
            
            catalog.append({
                'id': product.id,
                'name': product.name,
                'code': product.code,
                'version': product.version,
                'description': product.description,
                'specifications': {
                    'net_weight': product.net_weight,
                    'packaging_type': product.packaging_type,
                    'shelf_life_days': product.shelf_life_days,
                    'storage_temp': {
                        'min': product.storage_temp_min,
                        'max': product.storage_temp_max
                    }
                },
                'allergen_info': product.allergen_info,
                'nutrition_facts': product.nutrition_facts,
                'latest_production': {
                    'order_number': latest_order.order_number if latest_order else None,
                    'date': latest_order.created_at if latest_order else None,
                    'quantity': latest_order.produced_quantity if latest_order else 0
                } if latest_order else None,
                'total_production_orders': product.production_orders.count(),
                'ccp_count': product.ccps.filter(is_active=True).count()
            })
        
        return Response(catalog)