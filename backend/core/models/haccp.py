from django.db import models
from .user import User
from .product import FinishedProduct
from .production import ProductionOrder
import uuid


class CCP(models.Model):
    """중요 관리점 (Critical Control Point) 정의 모델"""
    
    CCP_TYPE_CHOICES = [
        ('temperature', '온도'),
        ('ph', 'pH'),
        ('time', '시간'),
        ('pressure', '압력'),
        ('visual', '육안검사'),
        ('metal_detection', '금속검출'),
        ('weight', '중량'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    ccp_type = models.CharField(max_length=20, choices=CCP_TYPE_CHOICES)
    description = models.TextField()
    process_step = models.CharField(max_length=200, help_text='어느 공정 단계의 CCP인지')
    critical_limit_min = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    critical_limit_max = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    monitoring_frequency = models.CharField(max_length=100, help_text='모니터링 주기 (예: 매 30분)')
    corrective_action = models.TextField(help_text='한계 기준 이탈 시 조치사항')
    responsible_person = models.CharField(max_length=100)
    monitoring_method = models.TextField()
    verification_method = models.TextField()
    record_keeping = models.TextField()
    finished_product = models.ForeignKey(
        FinishedProduct, 
        on_delete=models.PROTECT, 
        related_name='ccps',
        null=True,
        blank=True,
        help_text='특정 제품에만 적용되는 경우'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_ccps')
    
    class Meta:
        db_table = 'ccps'
        verbose_name = 'Critical Control Point'
        verbose_name_plural = 'Critical Control Points'
        
    def __str__(self):
        return f"{self.name} ({self.code})"


class CCPLog(models.Model):
    """CCP 모니터링 로그 - 불변 데이터로 HACCP 규정 준수"""
    
    STATUS_CHOICES = [
        ('within_limits', '기준 내'),
        ('out_of_limits', '기준 이탈'),
        ('corrective_action', '개선조치'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ccp = models.ForeignKey(CCP, on_delete=models.PROTECT, related_name='logs')
    production_order = models.ForeignKey(
        ProductionOrder, 
        on_delete=models.PROTECT, 
        related_name='ccp_logs',
        null=True,
        blank=True
    )
    measured_value = models.DecimalField(max_digits=10, decimal_places=3)
    unit = models.CharField(max_length=20)
    measured_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    is_within_limits = models.BooleanField()
    deviation_notes = models.TextField(blank=True)
    corrective_action_taken = models.TextField(blank=True)
    corrective_action_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        related_name='corrective_actions'
    )
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT,
        null=True,
        blank=True, 
        related_name='verified_ccp_logs'
    )
    verification_date = models.DateTimeField(null=True, blank=True)
    measurement_device = models.CharField(max_length=100, blank=True)
    environmental_conditions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_ccp_logs')
    
    class Meta:
        db_table = 'ccp_logs'
        verbose_name = 'CCP Monitoring Log'
        verbose_name_plural = 'CCP Monitoring Logs'
        ordering = ['-measured_at']
        
    def __str__(self):
        return f"{self.ccp.name} - {self.measured_value} {self.unit} ({self.measured_at})"
    
    def save(self, *args, **kwargs):
        """저장 시 자동으로 한계 기준 체크"""
        if self.pk is None:  # 새로 생성되는 경우만
            if self.ccp.critical_limit_min is not None and self.measured_value < self.ccp.critical_limit_min:
                self.is_within_limits = False
                self.status = 'out_of_limits'
            elif self.ccp.critical_limit_max is not None and self.measured_value > self.ccp.critical_limit_max:
                self.is_within_limits = False
                self.status = 'out_of_limits'
            else:
                self.is_within_limits = True
                self.status = 'within_limits'
        
        super().save(*args, **kwargs)