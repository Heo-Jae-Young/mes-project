from rest_framework import serializers
from core.models import FinishedProduct
from .user_serializers import UserSerializer


class FinishedProductSerializer(serializers.ModelSerializer):
    """완제품 조회용 Serializer"""
    
    created_by = UserSerializer(read_only=True)
    has_bom = serializers.SerializerMethodField()
    estimated_unit_cost = serializers.SerializerMethodField()
    cost_calculation_status = serializers.SerializerMethodField()
    
    class Meta:
        model = FinishedProduct
        fields = [
            'id', 'name', 'code', 'description', 'version', 'shelf_life_days',
            'storage_temp_min', 'storage_temp_max', 'net_weight', 'packaging_type',
            'allergen_info', 'nutrition_facts', 'is_active',
            'created_at', 'updated_at', 'created_by', 'has_bom',
            'estimated_unit_cost', 'cost_calculation_status'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'created_by', 'has_bom',
            'estimated_unit_cost', 'cost_calculation_status'
        ]
    
    def get_has_bom(self, obj):
        """BOM 설정 여부 확인"""
        return obj.bom_items.filter(is_active=True).exists()
    
    def get_estimated_unit_cost(self, obj):
        """예상 단위 원가 계산"""
        try:
            from ..services.cost_calculation_service import CostCalculationService
            cost_info = CostCalculationService.calculate_product_cost(str(obj.id))
            return str(cost_info['unit_cost'])
        except Exception:
            return "0"
    
    def get_cost_calculation_status(self, obj):
        """원가 계산 상태 정보"""
        try:
            from ..services.cost_calculation_service import CostCalculationService
            cost_info = CostCalculationService.calculate_product_cost(str(obj.id))
            return {
                'bom_missing': cost_info['bom_missing'],
                'calculation_method': cost_info['calculation_method'],
                'has_warnings': len(cost_info['warnings']) > 0
            }
        except Exception:
            return {
                'bom_missing': True,
                'calculation_method': 'error',
                'has_warnings': True
            }


class FinishedProductCreateSerializer(serializers.ModelSerializer):
    """완제품 생성용 Serializer"""
    
    class Meta:
        model = FinishedProduct
        fields = [
            'name', 'code', 'description', 'version', 'shelf_life_days',
            'storage_temp_min', 'storage_temp_max', 'net_weight', 'packaging_type',
            'allergen_info', 'nutrition_facts', 'is_active'
        ]
        
    def validate_code(self, value):
        if FinishedProduct.objects.filter(code=value).exists():
            raise serializers.ValidationError("이미 존재하는 제품 코드입니다.")
        return value
    
    def validate_shelf_life_days(self, value):
        if value <= 0:
            raise serializers.ValidationError("유통기한은 0일보다 커야 합니다.")
        return value
    
    def validate_net_weight(self, value):
        if value <= 0:
            raise serializers.ValidationError("순중량은 0보다 커야 합니다.")
        return value
    
    def validate(self, attrs):
        temp_min = attrs.get('storage_temp_min')
        temp_max = attrs.get('storage_temp_max')
        
        if temp_min is not None and temp_max is not None:
            if temp_min > temp_max:
                raise serializers.ValidationError({
                    'storage_temp_min': '최소 보관온도는 최대 보관온도보다 낮아야 합니다.'
                })
        return attrs
    
    def validate_nutrition_facts(self, value):
        """영양성분표 JSON 형식 검증 (선택사항)"""
        if value is not None and value != {}:
            if not isinstance(value, dict):
                raise serializers.ValidationError("영양성분표는 JSON 객체 형태여야 합니다.")
                
            # 숫자값 검증 (입력된 값만)
            for key, val in value.items():
                if val is not None and val != '' and not isinstance(val, (int, float)):
                    try:
                        float(val)
                    except (ValueError, TypeError):
                        raise serializers.ValidationError(f"{key}는 숫자값이어야 합니다.")
                    
        return value
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class FinishedProductUpdateSerializer(serializers.ModelSerializer):
    """완제품 수정용 Serializer"""
    
    class Meta:
        model = FinishedProduct
        fields = [
            'name', 'code', 'description', 'version', 'shelf_life_days',
            'storage_temp_min', 'storage_temp_max', 'net_weight', 'packaging_type',
            'allergen_info', 'nutrition_facts', 'is_active'
        ]
        
    def validate_code(self, value):
        """수정시 자기 자신 제외하고 코드 중복 검증"""
        if self.instance and self.instance.code == value:
            return value
        if FinishedProduct.objects.filter(code=value).exists():
            raise serializers.ValidationError("이미 존재하는 제품 코드입니다.")
        return value
    
    def validate_shelf_life_days(self, value):
        if value <= 0:
            raise serializers.ValidationError("유통기한은 0일보다 커야 합니다.")
        return value
    
    def validate_net_weight(self, value):
        if value <= 0:
            raise serializers.ValidationError("순중량은 0보다 커야 합니다.")
        return value
    
    def validate(self, attrs):
        temp_min = attrs.get('storage_temp_min')
        temp_max = attrs.get('storage_temp_max')
        
        if temp_min is not None and temp_max is not None:
            if temp_min > temp_max:
                raise serializers.ValidationError({
                    'storage_temp_min': '최소 보관온도는 최대 보관온도보다 낮아야 합니다.'
                })
        return attrs
    
    def validate_nutrition_facts(self, value):
        """영양성분표 JSON 형식 검증 (선택사항)"""
        if value is not None and value != {}:
            if not isinstance(value, dict):
                raise serializers.ValidationError("영양성분표는 JSON 객체 형태여야 합니다.")
                
            # 숫자값 검증 (입력된 값만)
            for key, val in value.items():
                if val is not None and val != '' and not isinstance(val, (int, float)):
                    try:
                        float(val)
                    except (ValueError, TypeError):
                        raise serializers.ValidationError(f"{key}는 숫자값이어야 합니다.")
                    
        return value