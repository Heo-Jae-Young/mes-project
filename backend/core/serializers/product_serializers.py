from rest_framework import serializers
from core.models import FinishedProduct
from .user_serializers import UserSerializer


class FinishedProductSerializer(serializers.ModelSerializer):
    """완제품 조회용 Serializer"""
    
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = FinishedProduct
        fields = [
            'id', 'name', 'code', 'description', 'version', 'shelf_life_days',
            'storage_temp_min', 'storage_temp_max', 'net_weight', 'packaging_type',
            'allergen_info', 'nutrition_facts', 'is_active',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']


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
        """영양성분표 JSON 형식 검증"""
        if value is not None:
            required_keys = ['calories', 'protein', 'fat', 'carbohydrates', 'sodium']
            if not isinstance(value, dict):
                raise serializers.ValidationError("영양성분표는 JSON 객체 형태여야 합니다.")
            
            missing_keys = [key for key in required_keys if key not in value]
            if missing_keys:
                raise serializers.ValidationError(
                    f"필수 영양성분 정보가 누락되었습니다: {', '.join(missing_keys)}"
                )
                
            # 숫자값 검증
            for key, val in value.items():
                if key in required_keys and not isinstance(val, (int, float)):
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
            'name', 'description', 'version', 'shelf_life_days',
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
        """영양성분표 JSON 형식 검증"""
        if value is not None:
            required_keys = ['calories', 'protein', 'fat', 'carbohydrates', 'sodium']
            if not isinstance(value, dict):
                raise serializers.ValidationError("영양성분표는 JSON 객체 형태여야 합니다.")
            
            missing_keys = [key for key in required_keys if key not in value]
            if missing_keys:
                raise serializers.ValidationError(
                    f"필수 영양성분 정보가 누락되었습니다: {', '.join(missing_keys)}"
                )
                
            # 숫자값 검증
            for key, val in value.items():
                if key in required_keys and not isinstance(val, (int, float)):
                    raise serializers.ValidationError(f"{key}는 숫자값이어야 합니다.")
                    
        return value