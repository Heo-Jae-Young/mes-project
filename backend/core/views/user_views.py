from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model

from core.models import User
from core.serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer
from core.services.user_service import UserService, UserQueryService, UserStatsService

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_service = UserService()
        self.user_query_service = UserQueryService()
        self.user_stats_service = UserStatsService()
    
    def get_serializer_class(self):
        """액션에 따라 다른 Serializer 사용"""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_queryset(self):
        """사용자 역할에 따른 쿼리셋 필터링"""
        return self.user_query_service.get_queryset_for_user(self.request.user)
    
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
        user_to_change = self.get_object()
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        new_password_confirm = request.data.get('new_password_confirm')

        try:
            self.user_service.change_password(
                user_to_change=user_to_change,
                old_password=old_password,
                new_password=new_password,
                new_password_confirm=new_password_confirm,
                acting_user=request.user
            )
            return Response({'detail': '비밀번호가 성공적으로 변경되었습니다.'})
        except (ValidationError, PermissionDenied) as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def roles(self, request):
        """사용 가능한 사용자 역할 목록"""
        roles = self.user_stats_service.get_role_choices()
        return Response(roles)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """사용자 통계 정보"""
        try:
            stats = self.user_stats_service.get_user_statistics(request.user)
            return Response(stats)
        except PermissionDenied as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)
