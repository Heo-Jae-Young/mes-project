from django.contrib import admin
from .models import (
    User, Supplier, RawMaterial, MaterialLot,
    FinishedProduct, ProductionOrder, CCP, CCPLog
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'department', 'is_active', 'date_joined')
    list_filter = ('role', 'department', 'is_active')
    search_fields = ('username', 'email', 'employee_id')
    ordering = ('username',)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'contact_person', 'email', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'code', 'contact_person')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(RawMaterial)
class RawMaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'supplier', 'unit', 'is_active')
    list_filter = ('category', 'supplier', 'is_active')
    search_fields = ('name', 'code')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(MaterialLot)
class MaterialLotAdmin(admin.ModelAdmin):
    list_display = ('lot_number', 'raw_material', 'supplier', 'status', 'received_date', 'expiry_date')
    list_filter = ('status', 'supplier', 'quality_test_passed', 'received_date')
    search_fields = ('lot_number', 'raw_material__name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'received_date'


@admin.register(FinishedProduct)
class FinishedProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'version', 'net_weight', 'shelf_life_days', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(ProductionOrder)
class ProductionOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'finished_product', 'planned_quantity', 'produced_quantity', 'status', 'priority')
    list_filter = ('status', 'priority', 'planned_start_date')
    search_fields = ('order_number', 'finished_product__name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'planned_start_date'


@admin.register(CCP)
class CCPAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'ccp_type', 'process_step', 'finished_product', 'is_active')
    list_filter = ('ccp_type', 'is_active', 'finished_product')
    search_fields = ('name', 'code', 'process_step')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(CCPLog)
class CCPLogAdmin(admin.ModelAdmin):
    list_display = ('ccp', 'measured_value', 'unit', 'status', 'measured_at', 'is_within_limits')
    list_filter = ('status', 'is_within_limits', 'ccp', 'measured_at')
    search_fields = ('ccp__name', 'production_order__order_number')
    readonly_fields = ('id', 'created_at')
    date_hierarchy = 'measured_at'
    
    def has_change_permission(self, request, obj=None):
        # CCP 로그는 불변 데이터로 수정 불가
        return False
    
    def has_delete_permission(self, request, obj=None):
        # CCP 로그는 삭제 불가 (HACCP 규정 준수)
        return False
