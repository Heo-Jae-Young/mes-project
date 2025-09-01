from rest_framework import serializers
from django.utils import timezone
from core.models import CCP, CCPLog
from .user_serializers import UserSerializer
from .product_serializers import FinishedProductSerializer
from .production_serializers import ProductionOrderSerializer


class CCPSerializer(serializers.ModelSerializer):
    """중요 관리점(CCP) 조회용 Serializer"""
    
    finished_product = FinishedProductSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    
    # 통계 정보
    total_logs = serializers.SerializerMethodField()
    out_of_limits_count = serializers.SerializerMethodField()
    compliance_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = CCP
        fields = [
            'id', 'name', 'code', 'ccp_type', 'description', 'process_step',
            'critical_limit_min', 'critical_limit_max', 'monitoring_frequency',
            'corrective_action', 'responsible_person', 'monitoring_method',
            'verification_method', 'record_keeping', 'finished_product', 'is_active',
            'total_logs', 'out_of_limits_count', 'compliance_rate',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
    
    def get_total_logs(self, obj):
        """총 로그 수"""
        return obj.logs.count()
    
    def get_out_of_limits_count(self, obj):
        """기준 이탈 로그 수 (최근 30일)"""
        from datetime import timedelta
        thirty_days_ago = timezone.now() - timedelta(days=30)
        return obj.logs.filter(
            measured_at__gte=thirty_days_ago,
            status='out_of_limits'
        ).count()
    
    def get_compliance_rate(self, obj):
        """규정 준수율 (최근 30일, 백분율)"""
        from datetime import timedelta
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        total_logs = obj.logs.filter(measured_at__gte=thirty_days_ago).count()
        if total_logs == 0:
            return None
            
        within_limits_count = obj.logs.filter(
            measured_at__gte=thirty_days_ago,
            status='within_limits'
        ).count()
        
        return round((within_limits_count / total_logs) * 100, 2)


class CCPCreateSerializer(serializers.ModelSerializer):
    """CCP 생성용 Serializer"""
    
    finished_product_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = CCP
        fields = [
            'name', 'code', 'ccp_type', 'description', 'process_step',
            'critical_limit_min', 'critical_limit_max', 'monitoring_frequency',
            'corrective_action', 'responsible_person', 'monitoring_method',
            'verification_method', 'record_keeping', 'finished_product_id', 'is_active'
        ]
        
    def validate_code(self, value):
        if CCP.objects.filter(code=value).exists():
            raise serializers.ValidationError("이미 존재하는 CCP 코드입니다.")
        return value
    
    def validate(self, attrs):
        critical_min = attrs.get('critical_limit_min')
        critical_max = attrs.get('critical_limit_max')
        ccp_type = attrs.get('ccp_type')
        
        # 온도, pH, 압력, 중량 타입은 수치 한계 필요
        numeric_types = ['temperature', 'ph', 'pressure', 'weight']
        if ccp_type in numeric_types:
            if critical_min is None and critical_max is None:
                raise serializers.ValidationError(
                    f"{ccp_type} 타입의 CCP는 최소값 또는 최대값 중 하나는 설정해야 합니다."
                )
                
        # 최소값이 최대값보다 클 수 없음
        if critical_min is not None and critical_max is not None:
            if critical_min > critical_max:
                raise serializers.ValidationError({
                    'critical_limit_min': '최소 한계값은 최대 한계값보다 작아야 합니다.'
                })
                
        return attrs
    
    def create(self, validated_data):
        finished_product_id = validated_data.pop('finished_product_id', None)
        
        if finished_product_id:
            validated_data['finished_product_id'] = finished_product_id
            
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
            
        return super().create(validated_data)


class CCPLogSerializer(serializers.ModelSerializer):
    """CCP 모니터링 로그 조회용 Serializer"""
    
    ccp = CCPSerializer(read_only=True)
    production_order = ProductionOrderSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    corrective_action_by = UserSerializer(read_only=True)
    verified_by = UserSerializer(read_only=True)
    
    # 계산 필드
    deviation_percentage = serializers.SerializerMethodField()
    time_since_measurement = serializers.SerializerMethodField()
    
    class Meta:
        model = CCPLog
        fields = [
            'id', 'ccp', 'production_order', 'measured_value', 'unit', 'measured_at',
            'status', 'is_within_limits', 'deviation_notes', 'corrective_action_taken',
            'corrective_action_by', 'verified_by', 'verification_date',
            'measurement_device', 'environmental_conditions', 'deviation_percentage',
            'time_since_measurement', 'created_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'created_by', 'is_within_limits', 'status']
    
    def get_deviation_percentage(self, obj):
        """한계 기준 대비 편차율 계산"""
        if obj.status == 'within_limits':
            return 0
            
        ccp = obj.ccp
        measured = float(obj.measured_value)
        
        if ccp.critical_limit_min is not None and measured < float(ccp.critical_limit_min):
            deviation = ((float(ccp.critical_limit_min) - measured) / float(ccp.critical_limit_min)) * 100
            return round(-deviation, 2)  # 음수로 표시 (하한값 미달)
        elif ccp.critical_limit_max is not None and measured > float(ccp.critical_limit_max):
            deviation = ((measured - float(ccp.critical_limit_max)) / float(ccp.critical_limit_max)) * 100
            return round(deviation, 2)  # 양수로 표시 (상한값 초과)
            
        return 0
    
    def get_time_since_measurement(self, obj):
        """측정 후 경과시간 (시간 단위)"""
        time_diff = timezone.now() - obj.measured_at
        return round(time_diff.total_seconds() / 3600, 2)


class CCPLogCreateSerializer(serializers.ModelSerializer):
    """CCP 로그 생성용 Serializer - 불변 데이터이므로 생성만 가능"""
    
    ccp_id = serializers.UUIDField(write_only=True)
    production_order_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = CCPLog
        fields = [
            'ccp_id', 'production_order_id', 'measured_value', 'unit', 'measured_at',
            'deviation_notes', 'corrective_action_taken', 'measurement_device',
            'environmental_conditions'
        ]
        
    def validate_measured_value(self, value):
        if value is None:
            raise serializers.ValidationError("측정값은 필수입니다.")
        return value
    
    def validate(self, attrs):
        measured_at = attrs.get('measured_at')
        
        # 미래 시간 체크
        if measured_at and measured_at > timezone.now():
            raise serializers.ValidationError({
                'measured_at': '측정 시간은 현재 시간보다 늦을 수 없습니다.'
            })
            
        # CCP 존재 확인
        ccp_id = attrs.get('ccp_id')
        if ccp_id:
            try:
                ccp = CCP.objects.get(id=ccp_id, is_active=True)
                attrs['ccp_instance'] = ccp  # 나중에 사용하기 위해 저장
            except CCP.DoesNotExist:
                raise serializers.ValidationError({
                    'ccp_id': '존재하지 않거나 비활성화된 CCP입니다.'
                })
                
        return attrs
    
    def create(self, validated_data):
        ccp_id = validated_data.pop('ccp_id')
        production_order_id = validated_data.pop('production_order_id', None)
        ccp_instance = validated_data.pop('ccp_instance', None)
        
        validated_data['ccp_id'] = ccp_id
        if production_order_id:
            validated_data['production_order_id'] = production_order_id
            
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
            
        # CCP 모델의 save() 메서드가 자동으로 is_within_limits, status 설정
        return super().create(validated_data)


class CCPLogUpdateSerializer(serializers.ModelSerializer):
    """CCP 로그 수정용 Serializer - 개선조치 정보만 수정 가능"""
    
    corrective_action_by_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    verified_by_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = CCPLog
        fields = [
            'corrective_action_taken', 'corrective_action_by_id',
            'verified_by_id', 'verification_date'
        ]
        
    def validate(self, attrs):
        # 개선조치 정보는 기준 이탈 시에만 입력 가능
        if self.instance.status == 'within_limits':
            if attrs.get('corrective_action_taken'):
                raise serializers.ValidationError(
                    "기준 내 측정값에는 개선조치를 입력할 수 없습니다."
                )
                
        # 검증자와 검증일자는 세트로 입력
        verified_by_id = attrs.get('verified_by_id')
        verification_date = attrs.get('verification_date')
        
        if verified_by_id and not verification_date:
            raise serializers.ValidationError({
                'verification_date': '검증자를 지정할 때는 검증일자도 입력해야 합니다.'
            })
        elif verification_date and not verified_by_id:
            raise serializers.ValidationError({
                'verified_by_id': '검증일자를 입력할 때는 검증자도 지정해야 합니다.'
            })
            
        return attrs
    
    def update(self, instance, validated_data):
        corrective_action_by_id = validated_data.pop('corrective_action_by_id', None)
        verified_by_id = validated_data.pop('verified_by_id', None)
        
        if 'corrective_action_by_id' in self.initial_data:
            instance.corrective_action_by_id = corrective_action_by_id
        if 'verified_by_id' in self.initial_data:
            instance.verified_by_id = verified_by_id
            
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        # 개선조치가 완료되면 상태 업데이트
        if instance.corrective_action_taken and instance.status == 'out_of_limits':
            instance.status = 'corrective_action'
            
        instance.save()
        return instance