from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import Http404
from decimal import Decimal

from ..services.cost_calculation_service import CostCalculationService


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def calculate_product_cost(request, product_id):
    """
    특정 제품의 원가 계산
    
    Query Parameters:
    - quantity: 생산 수량 (기본값: 1)
    """
    try:
        # 생산 수량 파라미터 처리
        quantity = request.GET.get('quantity', '1')
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return Response(
                    {'error': '생산 수량은 1 이상이어야 합니다.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response(
                {'error': '잘못된 생산 수량입니다.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 원가 계산
        cost_info = CostCalculationService.calculate_product_cost(product_id, quantity)
        
        # Decimal을 문자열로 변환 (JSON 직렬화를 위해)
        def decimal_to_str(obj):
            if isinstance(obj, dict):
                return {k: decimal_to_str(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [decimal_to_str(item) for item in obj]
            elif isinstance(obj, Decimal):
                return str(obj)
            return obj
        
        cost_info = decimal_to_str(cost_info)
        
        return Response(cost_info, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'원가 계산 중 오류가 발생했습니다: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def products_cost_summary(request):
    """
    모든 제품의 원가 요약 정보 조회
    """
    try:
        cost_summaries = CostCalculationService.get_products_cost_summary()
        
        # Decimal을 문자열로 변환
        def decimal_to_str(obj):
            if isinstance(obj, dict):
                return {k: decimal_to_str(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [decimal_to_str(item) for item in obj]
            elif isinstance(obj, Decimal):
                return str(obj)
            return obj
        
        cost_summaries = decimal_to_str(cost_summaries)
        
        return Response(cost_summaries, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'원가 요약 조회 중 오류가 발생했습니다: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def material_price_info(request, material_id):
    """
    특정 원자재의 가격 정보 조회
    """
    try:
        from ..models import RawMaterial, MaterialLot
        from django.db.models import Avg, Min, Max, Count
        from django.utils import timezone
        from datetime import timedelta
        
        try:
            material = RawMaterial.objects.get(id=material_id)
        except RawMaterial.DoesNotExist:
            return Response(
                {'error': '원자재를 찾을 수 없습니다.'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 현재 재고 정보
        current_lots = MaterialLot.objects.filter(
            raw_material=material,
            status__in=['received', 'in_storage'],
            quality_test_passed=True,
            quantity_current__gt=0
        )
        
        # 가격 통계
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_lots = MaterialLot.objects.filter(
            raw_material=material,
            received_date__gte=thirty_days_ago
        )
        
        all_lots = MaterialLot.objects.filter(raw_material=material)
        
        price_info = {
            'material': {
                'id': str(material.id),
                'name': material.name,
                'code': material.code,
                'category': material.category,
                'unit': material.unit
            },
            'current_inventory': {
                'total_lots': current_lots.count(),
                'total_quantity': sum(lot.quantity_current for lot in current_lots),
                'price_range': {
                    'min': str(current_lots.aggregate(min_price=Min('unit_price'))['min_price'] or 0),
                    'max': str(current_lots.aggregate(max_price=Max('unit_price'))['max_price'] or 0),
                    'avg': str(current_lots.aggregate(avg_price=Avg('unit_price'))['avg_price'] or 0)
                }
            },
            'price_history': {
                'recent_30days': {
                    'avg_price': str(recent_lots.aggregate(avg_price=Avg('unit_price'))['avg_price'] or 0),
                    'lot_count': recent_lots.count()
                },
                'historical': {
                    'avg_price': str(all_lots.aggregate(avg_price=Avg('unit_price'))['avg_price'] or 0),
                    'lot_count': all_lots.count(),
                    'price_range': {
                        'min': str(all_lots.aggregate(min_price=Min('unit_price'))['min_price'] or 0),
                        'max': str(all_lots.aggregate(max_price=Max('unit_price'))['max_price'] or 0)
                    }
                }
            }
        }
        
        return Response(price_info, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'원자재 가격 정보 조회 중 오류가 발생했습니다: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )