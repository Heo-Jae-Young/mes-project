from django.db import models
from .user import User
import uuid


class FinishedProduct(models.Model):
    """완제품 정의 모델"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    version = models.CharField(max_length=20, default='1.0')
    shelf_life_days = models.IntegerField()
    storage_temp_min = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    storage_temp_max = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    net_weight = models.DecimalField(max_digits=8, decimal_places=3)
    packaging_type = models.CharField(max_length=100)
    allergen_info = models.TextField(blank=True)
    nutrition_facts = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_finished_products')
    
    class Meta:
        db_table = 'finished_products'
        
    def __str__(self):
        return f"{self.name} ({self.code}) v{self.version}"