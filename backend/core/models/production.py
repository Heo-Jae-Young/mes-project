from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from .user import User
from .product import FinishedProduct
import uuid


class ProductionOrder(models.Model):
    """생산 주문 모델"""
    
    STATUS_CHOICES = [
        ('planned', '계획'),
        ('in_progress', '생산중'),
        ('completed', '완료'),
        ('cancelled', '취소'),
        ('on_hold', '보류'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', '낮음'),
        ('normal', '보통'),
        ('high', '높음'),
        ('urgent', '긴급'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=50, unique=True)
    finished_product = models.ForeignKey(FinishedProduct, on_delete=models.PROTECT, related_name='production_orders')
    planned_quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=3, 
        validators=[MinValueValidator(Decimal('0.001'))]
    )
    produced_quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=3, 
        default=Decimal('0.000')
    )
    planned_start_date = models.DateTimeField()
    planned_end_date = models.DateTimeField()
    actual_start_date = models.DateTimeField(null=True, blank=True)
    actual_end_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    notes = models.TextField(blank=True)
    assigned_operator = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_production_orders'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_production_orders')
    
    class Meta:
        db_table = 'production_orders'
        
    def __str__(self):
        return f"{self.order_number} - {self.finished_product.name}"