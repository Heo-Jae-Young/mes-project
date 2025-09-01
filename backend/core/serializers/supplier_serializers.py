from rest_framework import serializers
from core.models import Supplier
from .user_serializers import UserSerializer


class SupplierSerializer(serializers.ModelSerializer):
    """공급업체 조회용 Serializer"""
    
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'code', 'contact_person', 'email', 'phone', 
            'address', 'certification', 'status', 
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']


class SupplierCreateSerializer(serializers.ModelSerializer):
    """공급업체 생성용 Serializer"""
    
    class Meta:
        model = Supplier
        fields = [
            'name', 'code', 'contact_person', 'email', 'phone', 
            'address', 'certification', 'status'
        ]
        
    def validate_code(self, value):
        """공급업체 코드 중복 검증"""
        if Supplier.objects.filter(code=value).exists():
            raise serializers.ValidationError("이미 존재하는 공급업체 코드입니다.")
        return value
    
    def create(self, validated_data):
        """생성자 정보 자동 설정"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class SupplierUpdateSerializer(serializers.ModelSerializer):
    """공급업체 수정용 Serializer"""
    
    class Meta:
        model = Supplier
        fields = [
            'name', 'contact_person', 'email', 'phone', 
            'address', 'certification', 'status'
        ]
        
    def validate_code(self, value):
        """수정시 자기 자신 제외하고 코드 중복 검증"""
        if self.instance and self.instance.code == value:
            return value
        if Supplier.objects.filter(code=value).exists():
            raise serializers.ValidationError("이미 존재하는 공급업체 코드입니다.")
        return value