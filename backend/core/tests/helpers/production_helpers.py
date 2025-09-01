"""Production 관련 테스트 헬퍼 함수들"""
from datetime import timedelta
from django.utils import timezone
from core.models import ProductionOrder, FinishedProduct
from .user_helpers import create_test_user


def create_test_finished_product(**kwargs):
    """테스트용 완성품 생성"""
    user = kwargs.pop('created_by', None)
    if not user:
        user = create_test_user(role='admin')
    
    import random
    random_num = random.randint(1000, 9999)
    defaults = {
        'name': 'Test Product',
        'code': f'TP{random_num}',
        'description': 'Test product for unit testing',
        'version': '1.0',
        'shelf_life_days': 30,
        'net_weight': 100.000,
        'packaging_type': 'Plastic Container',
        'created_by': user
    }
    defaults.update(kwargs)
    return FinishedProduct.objects.create(**defaults)


def create_test_production_order(**kwargs):
    """테스트용 생산 주문 생성"""
    user = kwargs.pop('created_by', None)
    if not user:
        user = create_test_user(role='admin')
    
    finished_product = kwargs.pop('finished_product', None)
    if not finished_product:
        finished_product = create_test_finished_product(created_by=user)
    
    now = timezone.now()
    defaults = {
        'order_number': f'PO-{now.strftime("%Y%m%d")}-001',
        'finished_product': finished_product,
        'planned_quantity': 100,
        'planned_start_date': now + timedelta(hours=1),
        'planned_end_date': now + timedelta(hours=8),
        'status': 'planned',
        'priority': 'normal',
        'created_by': user
    }
    defaults.update(kwargs)
    return ProductionOrder.objects.create(**defaults)


def create_production_orders_batch(count=3, **kwargs):
    """여러 생산 주문 일괄 생성"""
    orders = []
    user = kwargs.get('created_by') or create_test_user(role='admin')
    finished_product = kwargs.get('finished_product') or create_test_finished_product(created_by=user)
    
    for i in range(count):
        order_kwargs = kwargs.copy()
        order_kwargs.update({
            'order_number': f'PO-TEST-{i+1:03d}',
            'finished_product': finished_product,
            'created_by': user
        })
        orders.append(create_test_production_order(**order_kwargs))
    return orders


def create_in_progress_production_order(**kwargs):
    """진행 중인 생산 주문 생성"""
    defaults = {
        'status': 'in_progress',
        'actual_start_date': timezone.now() - timedelta(hours=2)
    }
    defaults.update(kwargs)
    return create_test_production_order(**defaults)


def create_completed_production_order(**kwargs):
    """완료된 생산 주문 생성"""
    now = timezone.now()
    defaults = {
        'status': 'completed',
        'actual_start_date': now - timedelta(hours=8),
        'actual_end_date': now - timedelta(hours=1),
        'produced_quantity': kwargs.get('planned_quantity', 100)
    }
    defaults.update(kwargs)
    return create_test_production_order(**defaults)