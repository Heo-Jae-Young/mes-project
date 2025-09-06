from decimal import Decimal
from django.db.models import Avg, Min, Q
from typing import Dict, List, Optional, Tuple
from ..models import FinishedProduct, BOM, MaterialLot, RawMaterial


class CostCalculationService:
    """제품 원가 계산 서비스"""
    
    @staticmethod
    def calculate_product_cost(product_id: str, production_quantity: int = 1) -> Dict:
        """
        제품의 예상 원가 계산
        
        Args:
            product_id: 제품 ID
            production_quantity: 생산 수량 (기본값: 1)
            
        Returns:
            Dict: 원가 계산 결과
            {
                'product': {...},
                'total_cost': Decimal,
                'unit_cost': Decimal,
                'material_costs': [...],
                'bom_missing': bool,
                'calculation_method': str,
                'warnings': [...]
            }
        """
        try:
            product = FinishedProduct.objects.get(id=product_id)
        except FinishedProduct.DoesNotExist:
            raise ValueError(f"Product with id {product_id} not found")
        
        result = {
            'product': {
                'id': str(product.id),
                'name': product.name,
                'code': product.code,
                'version': product.version
            },
            'production_quantity': production_quantity,
            'total_cost': Decimal('0'),
            'unit_cost': Decimal('0'),
            'material_costs': [],
            'bom_missing': False,
            'calculation_method': 'current_lot',  # 초기값을 current_lot으로 설정
            'warnings': []
        }
        
        # BOM 확인
        bom_items = BOM.objects.filter(
            finished_product=product,
            is_active=True
        ).select_related('raw_material')
        
        if not bom_items.exists():
            result['bom_missing'] = True
            result['warnings'].append('BOM(자재명세서)가 설정되지 않았습니다.')
            return result
        
        # 각 BOM 아이템별 원가 계산
        total_cost = Decimal('0')
        calculation_methods = []
        
        for bom_item in bom_items:
            material_cost = CostCalculationService._calculate_material_cost(
                bom_item, production_quantity
            )
            result['material_costs'].append(material_cost)
            total_cost += material_cost['total_cost']
            calculation_methods.append(material_cost['price_method'])
            
            # 경고 추가
            if material_cost['warnings']:
                result['warnings'].extend(material_cost['warnings'])
        
        # 제품 레벨 계산 방법 결정 (우선순위: no_data > historical_average > recent_average > current_lot)
        if 'no_data' in calculation_methods:
            result['calculation_method'] = 'no_data'
        elif 'historical_average' in calculation_methods:
            result['calculation_method'] = 'historical_average'
        elif 'recent_average' in calculation_methods:
            result['calculation_method'] = 'recent_average'
        else:
            result['calculation_method'] = 'current_lot'
        
        result['total_cost'] = total_cost
        result['unit_cost'] = total_cost / Decimal(str(production_quantity)) if production_quantity > 0 else Decimal('0')
        
        return result
    
    @staticmethod
    def _calculate_material_cost(bom_item: BOM, production_quantity: int) -> Dict:
        """
        BOM 아이템별 원자재 원가 계산
        
        Args:
            bom_item: BOM 아이템
            production_quantity: 생산 수량
            
        Returns:
            Dict: 원자재 원가 계산 결과
        """
        material = bom_item.raw_material
        required_quantity = bom_item.calculate_total_required_quantity(production_quantity)
        
        result = {
            'material': {
                'id': str(material.id),
                'name': material.name,
                'code': material.code,
                'category': material.category,
                'unit': bom_item.unit
            },
            'required_quantity': required_quantity,
            'unit_price': Decimal('0'),
            'total_cost': Decimal('0'),
            'price_method': 'unknown',
            'lot_info': None,
            'warnings': []
        }
        
        # 가격 결정 우선순위:
        # 1. 현재 재고 중 가장 최근 단가 (FIFO 원칙)
        # 2. 최근 평균 단가 (30일 이내)
        # 3. 전체 평균 단가
        
        # 1. 현재 재고 중 FIFO 단가
        current_lots = MaterialLot.objects.filter(
            raw_material=material,
            status__in=['received', 'in_storage'],
            quality_test_passed=True,
            quantity_current__gt=0
        ).order_by('expiry_date', 'received_date')
        
        if current_lots.exists():
            # FIFO 방식으로 필요한 수량만큼의 평균 단가 계산
            unit_price = CostCalculationService._calculate_fifo_average_price(
                current_lots, required_quantity
            )
            result['unit_price'] = unit_price
            result['price_method'] = 'current_lot'
            result['lot_info'] = {
                'available_lots': current_lots.count(),
                'total_available_quantity': sum(lot.quantity_current for lot in current_lots)
            }
        else:
            # 2. 최근 30일 평균 단가
            from django.utils import timezone
            from datetime import timedelta
            
            thirty_days_ago = timezone.now() - timedelta(days=30)
            recent_lots = MaterialLot.objects.filter(
                raw_material=material,
                received_date__gte=thirty_days_ago
            )
            
            if recent_lots.exists():
                avg_price = recent_lots.aggregate(avg_price=Avg('unit_price'))['avg_price']
                result['unit_price'] = avg_price or Decimal('0')
                result['price_method'] = 'recent_average'
                result['warnings'].append('현재 재고가 부족하여 최근 30일 평균 단가로 계산했습니다.')
            else:
                # 3. 전체 평균 단가
                all_lots = MaterialLot.objects.filter(raw_material=material)
                if all_lots.exists():
                    avg_price = all_lots.aggregate(avg_price=Avg('unit_price'))['avg_price']
                    result['unit_price'] = avg_price or Decimal('0')
                    result['price_method'] = 'historical_average'
                    result['warnings'].append('최근 입고 내역이 없어 전체 평균 단가로 계산했습니다.')
                else:
                    result['warnings'].append('가격 정보를 찾을 수 없습니다.')
                    result['price_method'] = 'no_data'
        
        result['total_cost'] = result['unit_price'] * required_quantity
        
        return result
    
    @staticmethod
    def _calculate_fifo_average_price(lots_queryset, required_quantity: Decimal) -> Decimal:
        """
        FIFO 방식으로 필요한 수량에 대한 가중평균 단가 계산
        
        Args:
            lots_queryset: MaterialLot QuerySet (FIFO 순서로 정렬됨)
            required_quantity: 필요한 수량
            
        Returns:
            Decimal: 가중평균 단가
        """
        if required_quantity <= 0:
            return Decimal('0')
        
        total_cost = Decimal('0')
        remaining_quantity = required_quantity
        
        for lot in lots_queryset:
            if remaining_quantity <= 0:
                break
                
            # 이 로트에서 사용할 수량
            use_quantity = min(lot.quantity_current, remaining_quantity)
            
            # 비용 누적
            total_cost += lot.unit_price * use_quantity
            remaining_quantity -= use_quantity
        
        # 가중평균 단가
        if total_cost > 0 and required_quantity > remaining_quantity:
            used_quantity = required_quantity - remaining_quantity
            return total_cost / used_quantity
        
        # 재고가 부족한 경우 첫 번째 로트의 단가 사용
        return lots_queryset.first().unit_price if lots_queryset.exists() else Decimal('0')
    
    @staticmethod
    def get_products_cost_summary() -> List[Dict]:
        """
        모든 제품의 원가 요약 정보 조회
        
        Returns:
            List[Dict]: 제품별 원가 요약
        """
        products = FinishedProduct.objects.filter(is_active=True)
        results = []
        
        for product in products:
            try:
                cost_info = CostCalculationService.calculate_product_cost(str(product.id))
                summary = {
                    'product_id': str(product.id),
                    'product_name': product.name,
                    'product_code': product.code,
                    'unit_cost': cost_info['unit_cost'],
                    'bom_missing': cost_info['bom_missing'],
                    'calculation_method': cost_info['calculation_method'],
                    'has_warnings': len(cost_info['warnings']) > 0
                }
                results.append(summary)
            except Exception as e:
                # 개별 제품 계산 실패 시 기본값으로 처리
                results.append({
                    'product_id': str(product.id),
                    'product_name': product.name,
                    'product_code': product.code,
                    'unit_cost': Decimal('0'),
                    'bom_missing': True,
                    'calculation_method': 'error',
                    'has_warnings': True,
                    'error': str(e)
                })
        
        return results