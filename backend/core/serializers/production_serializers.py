from rest_framework import serializers
from django.utils import timezone
from core.models import ProductionOrder
from .user_serializers import UserSerializer
from .product_serializers import FinishedProductSerializer


class ProductionOrderSerializer(serializers.ModelSerializer):
    """생산오더 조회용 Serializer"""
    
    finished_product = FinishedProductSerializer(read_only=True)
    assigned_operator = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    
    # 계산 필드
    completion_rate = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    duration_planned = serializers.SerializerMethodField()
    duration_actual = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductionOrder
        fields = [
            'id', 'order_number', 'finished_product', 'planned_quantity', 'produced_quantity',
            'planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date',
            'status', 'priority', 'notes', 'assigned_operator', 'completion_rate', 
            'is_overdue', 'duration_planned', 'duration_actual',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
    
    def get_completion_rate(self, obj):
        """생산 완료율 계산"""
        if obj.planned_quantity == 0:
            return 0
        return round((obj.produced_quantity / obj.planned_quantity) * 100, 2)
    
    def get_is_overdue(self, obj):
        """일정 지연 여부"""
        if obj.status in ['completed', 'cancelled']:
            return False
        return timezone.now() > obj.planned_end_date
    
    def get_duration_planned(self, obj):
        """계획 소요시간 (시간 단위)"""
        if obj.planned_start_date and obj.planned_end_date:
            duration = obj.planned_end_date - obj.planned_start_date
            return round(duration.total_seconds() / 3600, 2)
        return None
    
    def get_duration_actual(self, obj):
        """실제 소요시간 (시간 단위)"""
        if obj.actual_start_date and obj.actual_end_date:
            duration = obj.actual_end_date - obj.actual_start_date
            return round(duration.total_seconds() / 3600, 2)
        return None


class ProductionOrderCreateSerializer(serializers.ModelSerializer):
    """생산오더 생성용 Serializer"""
    
    finished_product_id = serializers.UUIDField(write_only=True)
    assigned_operator_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = ProductionOrder
        fields = [
            'order_number', 'finished_product_id', 'planned_quantity',
            'planned_start_date', 'planned_end_date', 'status', 'priority',
            'notes', 'assigned_operator_id'
        ]
        
    def validate_order_number(self, value):
        if ProductionOrder.objects.filter(order_number=value).exists():
            raise serializers.ValidationError("이미 존재하는 주문번호입니다.")
        return value
    
    def validate_planned_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("계획 수량은 0보다 커야 합니다.")
        return value
    
    def validate(self, attrs):
        planned_start = attrs.get('planned_start_date')
        planned_end = attrs.get('planned_end_date')
        
        if planned_start and planned_end:
            if planned_start >= planned_end:
                raise serializers.ValidationError({
                    'planned_end_date': '계획 종료일은 시작일보다 늦어야 합니다.'
                })
                
            # 과거 날짜 체크
            if planned_start < timezone.now():
                raise serializers.ValidationError({
                    'planned_start_date': '계획 시작일은 현재 시간 이후여야 합니다.'
                })
                
        return attrs
    
    def create(self, validated_data):
        finished_product_id = validated_data.pop('finished_product_id')
        assigned_operator_id = validated_data.pop('assigned_operator_id', None)
        
        validated_data['finished_product_id'] = finished_product_id
        if assigned_operator_id:
            validated_data['assigned_operator_id'] = assigned_operator_id
            
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
            
        return super().create(validated_data)


class ProductionOrderUpdateSerializer(serializers.ModelSerializer):
    """생산오더 수정용 Serializer"""
    
    assigned_operator_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = ProductionOrder
        fields = [
            'planned_quantity', 'produced_quantity', 'planned_start_date', 'planned_end_date',
            'actual_start_date', 'actual_end_date', 'status', 'priority', 'notes',
            'assigned_operator_id'
        ]
        
    def validate_planned_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("계획 수량은 0보다 커야 합니다.")
        return value
    
    def validate_produced_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("생산 수량은 0 이상이어야 합니다.")
        return value
    
    def validate(self, attrs):
        planned_start = attrs.get('planned_start_date', self.instance.planned_start_date)
        planned_end = attrs.get('planned_end_date', self.instance.planned_end_date)
        actual_start = attrs.get('actual_start_date', self.instance.actual_start_date)
        actual_end = attrs.get('actual_end_date', self.instance.actual_end_date)
        status = attrs.get('status', self.instance.status)
        
        # 계획 날짜 검증
        if planned_start and planned_end and planned_start >= planned_end:
            raise serializers.ValidationError({
                'planned_end_date': '계획 종료일은 시작일보다 늦어야 합니다.'
            })
        
        # 실제 날짜 검증
        if actual_start and actual_end and actual_start >= actual_end:
            raise serializers.ValidationError({
                'actual_end_date': '실제 종료일은 시작일보다 늦어야 합니다.'
            })
        
        # 상태별 필수 필드 검증
        if status == 'in_progress' and not actual_start:
            if 'actual_start_date' not in attrs:
                raise serializers.ValidationError({
                    'actual_start_date': '생산중 상태에서는 실제 시작일이 필요합니다.'
                })
        
        if status == 'completed':
            if not actual_start or not actual_end:
                missing_fields = []
                if not actual_start and 'actual_start_date' not in attrs:
                    missing_fields.append('actual_start_date')
                if not actual_end and 'actual_end_date' not in attrs:
                    missing_fields.append('actual_end_date')
                
                if missing_fields:
                    raise serializers.ValidationError({
                        field: '완료 상태에서는 실제 시작일과 종료일이 모두 필요합니다.'
                        for field in missing_fields
                    })
                    
        return attrs
    
    def update(self, instance, validated_data):
        assigned_operator_id = validated_data.pop('assigned_operator_id', None)
        
        if 'assigned_operator_id' in self.initial_data:
            instance.assigned_operator_id = assigned_operator_id
            
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        instance.save()
        return instance