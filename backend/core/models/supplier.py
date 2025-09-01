from django.db import models
from .user import User
import uuid


class Supplier(models.Model):
    """공급업체 관리 모델"""
    
    STATUS_CHOICES = [
        ('active', '활성'),
        ('inactive', '비활성'),
        ('suspended', '정지'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    certification = models.TextField(blank=True, help_text='HACCP, ISO 등 인증 정보')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_suppliers')
    
    class Meta:
        db_table = 'suppliers'
        
    def __str__(self):
        return f"{self.name} ({self.code})"