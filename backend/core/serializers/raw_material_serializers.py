from rest_framework import serializers
from decimal import Decimal
from core.models import RawMaterial, MaterialLot
from .user_serializers import UserSerializer
from .supplier_serializers import SupplierSerializer


class RawMaterialSerializer(serializers.ModelSerializer):
    """원자재 카탈로그 조회용 Serializer"""
    
    supplier = SupplierSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = RawMaterial
        fields = [
            'id', 'name', 'code', 'category', 'description', 'unit',
            'storage_temp_min', 'storage_temp_max', 'shelf_life_days', 
            'allergens', 'supplier', 'is_active',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']


class RawMaterialCreateSerializer(serializers.ModelSerializer):
    """원자재 생성용 Serializer"""
    
    supplier_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = RawMaterial
        fields = [
            'name', 'code', 'category', 'description', 'unit',
            'storage_temp_min', 'storage_temp_max', 'shelf_life_days',
            'allergens', 'supplier_id', 'is_active'
        ]
        
    def validate_code(self, value):
        if RawMaterial.objects.filter(code=value).exists():
            raise serializers.ValidationError("이미 존재하는 원자재 코드입니다.")
        return value
    
    def validate(self, attrs):
        temp_min = attrs.get('storage_temp_min')
        temp_max = attrs.get('storage_temp_max')
        
        if temp_min is not None and temp_max is not None:
            if temp_min > temp_max:
                raise serializers.ValidationError({
                    'storage_temp_min': '최소 온도는 최대 온도보다 낮아야 합니다.'
                })
        return attrs
    
    def create(self, validated_data):
        supplier_id = validated_data.pop('supplier_id')
        validated_data['supplier_id'] = supplier_id
        
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
            
        return super().create(validated_data)


class MaterialLotSerializer(serializers.ModelSerializer):
    """원자재 로트 조회용 Serializer - 추적성 정보 포함"""
    
    raw_material = RawMaterialSerializer(read_only=True)
    supplier = SupplierSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    
    # 계산 필드
    quantity_used = serializers.SerializerMethodField()
    usage_percentage = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()
    
    class Meta:
        model = MaterialLot
        fields = [
            'id', 'lot_number', 'raw_material', 'supplier',
            'received_date', 'expiry_date', 'quantity_received', 'quantity_current',
            'quantity_used', 'usage_percentage', 'unit_price', 'status',
            'quality_test_passed', 'quality_test_date', 'quality_test_notes',
            'storage_location', 'temperature_at_receipt', 'days_until_expiry',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
    
    def get_quantity_used(self, obj):
        """사용된 수량 계산"""
        return obj.quantity_received - obj.quantity_current
    
    def get_usage_percentage(self, obj):
        """사용률 계산"""
        if obj.quantity_received == 0:
            return 0
        usage_rate = (obj.quantity_received - obj.quantity_current) / obj.quantity_received * 100
        return round(float(usage_rate), 2)
    
    def get_days_until_expiry(self, obj):
        """유통기한까지 남은 일수"""
        if not obj.expiry_date:
            return None
        from datetime import date
        days_diff = (obj.expiry_date - date.today()).days
        return days_diff if days_diff >= 0 else 0


class MaterialLotCreateSerializer(serializers.ModelSerializer):
    """원자재 로트 생성용 Serializer"""
    
    raw_material_id = serializers.UUIDField(write_only=True)
    supplier_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = MaterialLot
        fields = [
            'lot_number', 'raw_material_id', 'supplier_id', 
            'received_date', 'expiry_date', 'quantity_received',
            'unit_price', 'status', 'quality_test_passed', 
            'quality_test_date', 'quality_test_notes',
            'storage_location', 'temperature_at_receipt'
        ]
        
    def validate_lot_number(self, value):
        if MaterialLot.objects.filter(lot_number=value).exists():
            raise serializers.ValidationError("이미 존재하는 로트 번호입니다.")
        return value
    
    def validate_quantity_received(self, value):
        if value <= 0:
            raise serializers.ValidationError("입고 수량은 0보다 커야 합니다.")
        return value
    
    def validate(self, attrs):
        from datetime import date
        
        # 유통기한 검증
        if attrs.get('expiry_date'):
            if attrs['expiry_date'] <= date.today():
                raise serializers.ValidationError({
                    'expiry_date': '유통기한은 오늘 날짜 이후여야 합니다.'
                })
        
        # 품질검사 날짜 검증
        if attrs.get('quality_test_date') and attrs.get('received_date'):
            if attrs['quality_test_date'].date() < attrs['received_date'].date():
                raise serializers.ValidationError({
                    'quality_test_date': '품질검사 날짜는 입고일 이후여야 합니다.'
                })
                
        return attrs
    
    def create(self, validated_data):
        raw_material_id = validated_data.pop('raw_material_id')
        supplier_id = validated_data.pop('supplier_id')
        
        validated_data['raw_material_id'] = raw_material_id
        validated_data['supplier_id'] = supplier_id
        validated_data['quantity_current'] = validated_data['quantity_received']
        
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
            
        return super().create(validated_data)