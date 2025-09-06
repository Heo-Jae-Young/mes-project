from rest_framework import serializers
from core.models import BOM, FinishedProduct, RawMaterial
from .product_serializers import FinishedProductSerializer
from .raw_material_serializers import RawMaterialSerializer


class BOMCreateSerializer(serializers.ModelSerializer):
    """BOM 생성용 Serializer"""
    
    class Meta:
        model = BOM
        fields = [
            'finished_product', 'raw_material', 'quantity_per_unit', 
            'unit', 'is_active', 'notes'
        ]
        
    def validate(self, attrs):
        """중복 체크 및 기본 유효성 검증"""
        finished_product = attrs.get('finished_product')
        raw_material = attrs.get('raw_material')
        
        # 동일 제품-원자재 조합 중복 체크
        if BOM.objects.filter(
            finished_product=finished_product, 
            raw_material=raw_material
        ).exists():
            raise serializers.ValidationError({
                'raw_material': '이미 해당 제품에 등록된 원자재입니다.'
            })
            
        return attrs
    
    def validate_quantity_per_unit(self, value):
        if value <= 0:
            raise serializers.ValidationError("단위당 소요량은 0보다 커야 합니다.")
        return value
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class BOMUpdateSerializer(serializers.ModelSerializer):
    """BOM 수정용 Serializer"""
    
    class Meta:
        model = BOM
        fields = [
            'quantity_per_unit', 'unit', 'is_active', 'notes'
        ]
        # 제품과 원자재는 수정 불가 (삭제 후 재생성)
        
    def validate_quantity_per_unit(self, value):
        if value <= 0:
            raise serializers.ValidationError("단위당 소요량은 0보다 커야 합니다.")
        return value


class BOMListSerializer(serializers.ModelSerializer):
    """BOM 목록 조회용 Serializer"""
    
    raw_material = RawMaterialSerializer(read_only=True)
    finished_product = FinishedProductSerializer(read_only=True)
    total_required_for_production = serializers.SerializerMethodField()
    
    class Meta:
        model = BOM
        fields = [
            'id', 'finished_product', 'raw_material', 'quantity_per_unit', 
            'unit', 'is_active', 'notes', 'created_at', 'updated_at',
            'total_required_for_production'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_required_for_production(self, obj):
        """특정 생산 수량에 대한 총 소요량 (컨텍스트에서 production_quantity 전달 시)"""
        production_quantity = self.context.get('production_quantity', 1)
        return obj.calculate_total_required_quantity(production_quantity)


class BOMDetailSerializer(serializers.ModelSerializer):
    """BOM 상세 조회용 Serializer"""
    
    raw_material = RawMaterialSerializer(read_only=True)
    finished_product = FinishedProductSerializer(read_only=True)
    material_info = serializers.ReadOnlyField()
    product_info = serializers.ReadOnlyField()
    
    class Meta:
        model = BOM
        fields = [
            'id', 'finished_product', 'raw_material', 'quantity_per_unit', 
            'unit', 'is_active', 'notes', 'created_at', 'updated_at',
            'material_info', 'product_info'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductBOMSummarySerializer(serializers.ModelSerializer):
    """제품별 BOM 요약 Serializer (제품 관리 페이지용)"""
    
    raw_material_name = serializers.CharField(source='raw_material.name', read_only=True)
    raw_material_code = serializers.CharField(source='raw_material.code', read_only=True)
    raw_material_category = serializers.CharField(source='raw_material.category', read_only=True)
    
    class Meta:
        model = BOM
        fields = [
            'id', 'raw_material_name', 'raw_material_code', 'raw_material_category',
            'quantity_per_unit', 'unit', 'is_active'
        ]