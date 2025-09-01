from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from core.models import User
from core.serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """사용자 관리 ViewSet"""
    
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active', 'department']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'employee_id']
    ordering_fields = ['username', 'created_at', 'last_login']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """액션에 따라 다른 Serializer 사용"""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_queryset(self):
        """사용자 역할에 따른 쿼리셋 필터링"""
        user = self.request.user
        queryset = User.objects.all()
        
        # 관리자가 아닌 경우 자신의 정보만 조회 가능
        if user.role not in ['admin', 'quality_manager']:
            return queryset.filter(id=user.id)
        
        return queryset
    
    def perform_create(self, serializer):
        """사용자 생성 시 생성자 정보 자동 설정"""
        serializer.save()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """현재 로그인한 사용자 정보 조회"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """사용자 비밀번호 변경"""
        user = self.get_object()
        
        # 자신의 비밀번호만 변경 가능 (관리자 제외)
        if request.user.id != user.id and request.user.role != 'admin':
            return Response(
                {'detail': '본인의 비밀번호만 변경할 수 있습니다.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        new_password_confirm = request.data.get('new_password_confirm')
        
        if not all([old_password, new_password, new_password_confirm]):
            return Response(
                {'detail': '모든 비밀번호 필드를 입력해주세요.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 관리자가 아닌 경우 기존 비밀번호 확인
        if request.user.role != 'admin' and not user.check_password(old_password):
            return Response(
                {'detail': '기존 비밀번호가 일치하지 않습니다.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_password != new_password_confirm:
            return Response(
                {'detail': '새 비밀번호가 일치하지 않습니다.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        return Response({'detail': '비밀번호가 성공적으로 변경되었습니다.'})
    
    @action(detail=False, methods=['get'])
    def roles(self, request):
        """사용 가능한 사용자 역할 목록"""
        roles = [{'key': key, 'value': value} for key, value in User.ROLE_CHOICES]
        return Response(roles)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """사용자 통계 정보"""
        if request.user.role not in ['admin', 'quality_manager']:
            return Response(
                {'detail': '권한이 없습니다.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        role_distribution = {}
        
        for role_key, role_name in User.ROLE_CHOICES:
            count = User.objects.filter(role=role_key).count()
            role_distribution[role_name] = count
        
        return Response({
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users,
            'role_distribution': role_distribution
        })