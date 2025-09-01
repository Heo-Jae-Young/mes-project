
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied, ValidationError

User = get_user_model()


class UserService:
    """사용자 관련 비즈니스 로직을 처리하는 서비스 클래스"""

    def change_password(self, user_to_change, old_password, new_password, new_password_confirm, acting_user):
        """
        사용자 비밀번호를 변경합니다.
        - 관리자는 모든 사용자의 비밀번호를 변경할 수 있습니다.
        - 일반 사용자는 자신의 비밀번호만 변경할 수 있으며, 기존 비밀번호를 확인해야 합니다.
        """
        # 1. 권한 확인
        if acting_user.id != user_to_change.id and acting_user.role != 'admin':
            raise PermissionDenied('본인의 비밀번호만 변경할 수 있습니다.')

        # 2. 입력 데이터 검증
        if not all([old_password, new_password, new_password_confirm]) and acting_user.role != 'admin':
            raise ValidationError('모든 비밀번호 필드를 입력해주세요.')
        
        if not new_password or not new_password_confirm:
             raise ValidationError('새 비밀번호 필드를 입력해주세요.')

        # 3. 기존 비밀번호 확인 (관리자가 아닌 경우)
        if acting_user.role != 'admin' and not user_to_change.check_password(old_password):
            raise ValidationError('기존 비밀번호가 일치하지 않습니다.')

        # 4. 새 비밀번호 일치 여부 확인
        if new_password != new_password_confirm:
            raise ValidationError('새 비밀번호가 일치하지 않습니다.')

        # 5. 비밀번호 설정 및 저장
        user_to_change.set_password(new_password)
        user_to_change.save(update_fields=['password'])


class UserQueryService:
    """사용자 조회 관련 로직을 처리하는 서비스 클래스"""

    def get_queryset_for_user(self, user):
        """
        요청 사용자의 역할에 따라 필터링된 쿼리셋을 반환합니다.
        - 관리자/품질관리자는 모든 사용자를 조회할 수 있습니다.
        - 그 외 역할은 자신의 정보만 조회할 수 있습니다.
        """
        queryset = User.objects.all()
        if user.role not in ['admin', 'quality_manager']:
            return queryset.filter(id=user.id)
        return queryset


class UserStatsService:
    """사용자 통계 및 메타 데이터 관련 로직을 처리하는 서비스 클래스"""

    def get_user_statistics(self, acting_user):
        """
        사용자 통계 정보를 반환합니다.
        - 관리자/품질관리자만 접근 가능합니다.
        """
        if acting_user.role not in ['admin', 'quality_manager']:
            raise PermissionDenied('통계 정보를 조회할 권한이 없습니다.')

        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        
        role_distribution = {
            role_name: User.objects.filter(role=role_key).count()
            for role_key, role_name in User.ROLE_CHOICES
        }

        return {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users,
            'role_distribution': role_distribution
        }

    def get_role_choices(self):
        """사용 가능한 역할 목록을 반환합니다."""
        return [{'key': key, 'value': value} for key, value in User.ROLE_CHOICES]

