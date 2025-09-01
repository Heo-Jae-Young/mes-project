from django.db import models
from .user import User
from .supplier import Supplier
import uuid


class RawMaterial(models.Model):
    """원자재 카탈로그 모델"""
    
    CATEGORY_CHOICES = [
        ('ingredient', '원료'),
        ('packaging', '포장재'),
        ('additive', '첨가물'),
        ('chemical', '화학물질'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=10, default='kg')
    storage_temp_min = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    storage_temp_max = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    shelf_life_days = models.IntegerField(null=True, blank=True)
    allergens = models.TextField(blank=True, help_text='알레르기 유발 요소')
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='raw_materials')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_raw_materials')
    
    class Meta:
        db_table = 'raw_materials'
        
    def __str__(self):
        return f"{self.name} ({self.code})"


class MaterialLot(models.Model):
    """원자재 로트 추적 모델 - 완전한 이력 추적을 위한 핵심 모델"""
    
    STATUS_CHOICES = [
        ('received', '입고'),
        ('in_storage', '보관중'),
        ('in_use', '사용중'),
        ('used', '사용완료'),
        ('expired', '유통기한만료'),
        ('rejected', '반품'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lot_number = models.CharField(max_length=100, unique=True)
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.PROTECT, related_name='lots')
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='material_lots')
    received_date = models.DateTimeField()
    expiry_date = models.DateField(null=True, blank=True)
    quantity_received = models.DecimalField(max_digits=10, decimal_places=3)
    quantity_current = models.DecimalField(max_digits=10, decimal_places=3)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received')
    quality_test_passed = models.BooleanField(null=True, blank=True)
    quality_test_date = models.DateTimeField(null=True, blank=True)
    quality_test_notes = models.TextField(blank=True)
    storage_location = models.CharField(max_length=100, blank=True)
    temperature_at_receipt = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_material_lots')
    
    class Meta:
        db_table = 'material_lots'
        
    def __str__(self):
        return f"{self.raw_material.name} - {self.lot_number}"