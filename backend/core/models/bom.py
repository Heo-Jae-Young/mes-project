from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator
import uuid


class BOM(models.Model):
    """BOM (Bill of Materials) - 제품별 원자재 소요량 정의"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    finished_product = models.ForeignKey(
        'FinishedProduct', 
        on_delete=models.CASCADE, 
        related_name='bom_items',
        verbose_name='완제품'
    )
    raw_material = models.ForeignKey(
        'RawMaterial', 
        on_delete=models.CASCADE, 
        related_name='bom_usages',
        verbose_name='원자재'
    )
    quantity_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        verbose_name='단위당 소요량',
        help_text='제품 1개 생산에 필요한 원자재 수량 (kg, L 등 원자재 단위 기준)'
    )
    unit = models.CharField(
        max_length=20, 
        verbose_name='단위',
        help_text='원자재의 단위 (kg, L, 개 등)'
    )
    is_active = models.BooleanField(default=True, verbose_name='활성 상태')
    notes = models.TextField(blank=True, verbose_name='비고')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'User', 
        on_delete=models.PROTECT, 
        related_name='created_bom_items'
    )
    
    class Meta:
        db_table = 'bom'
        unique_together = ['finished_product', 'raw_material']
        indexes = [
            models.Index(fields=['finished_product']),
            models.Index(fields=['raw_material']),
        ]
        verbose_name = 'BOM (자재명세서)'
        verbose_name_plural = 'BOM (자재명세서)'
        
    def __str__(self):
        return f"{self.finished_product.name} - {self.raw_material.name} ({self.quantity_per_unit}{self.unit})"
    
    def calculate_total_required_quantity(self, production_quantity):
        """생산 수량에 따른 총 원자재 소요량 계산"""
        return self.quantity_per_unit * Decimal(str(production_quantity))
    
    @property
    def material_info(self):
        """원자재 정보 요약"""
        return {
            'id': str(self.raw_material.id),
            'name': self.raw_material.name,
            'code': self.raw_material.code,
            'category': self.raw_material.category,
            'unit': self.unit,
            'quantity_per_unit': self.quantity_per_unit
        }
    
    @property
    def product_info(self):
        """제품 정보 요약"""
        return {
            'id': str(self.finished_product.id),
            'name': self.finished_product.name,
            'code': self.finished_product.code,
            'version': self.finished_product.version
        }