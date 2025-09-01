from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """HACCP MES 사용자 모델 - 역할 기반 접근 제어"""
    
    ROLE_CHOICES = [
        ('admin', '관리자'),
        ('quality_manager', '품질관리자'),
        ('production_manager', '생산관리자'),
        ('operator', '작업자'),
        ('auditor', '감사자'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='operator')
    employee_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.role})"
    
    class Meta:
        db_table = 'users'