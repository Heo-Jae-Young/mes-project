import pytest
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied, ValidationError

from core.services.user_service import UserService, UserQueryService, UserStatsService

User = get_user_model()


@pytest.mark.unit
@pytest.mark.django_db
class TestUserService:
    """User Service 단위 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.user_service = UserService()
        
        # Test Users
        self.admin_user = User.objects.create_user(
            username='admin_user_test',
            password='test123',
            role='admin'
        )
        
        self.quality_manager = User.objects.create_user(
            username='quality_user_test',
            password='test123',
            role='quality_manager'
        )
        
        self.operator = User.objects.create_user(
            username='operator_user_test',
            password='test123',
            role='operator'
        )
        
        self.regular_user = User.objects.create_user(
            username='regular_user_test',
            password='test123',
            role='operator'
        )

    def test_change_password_success_self(self):
        """자신의 비밀번호 변경 성공 테스트"""
        self.user_service.change_password(
            user_to_change=self.operator,
            old_password='test123',
            new_password='newpass456',
            new_password_confirm='newpass456',
            acting_user=self.operator
        )
        
        # 비밀번호가 변경되었는지 확인
        self.operator.refresh_from_db()
        assert self.operator.check_password('newpass456')
        assert not self.operator.check_password('test123')

    def test_change_password_success_admin(self):
        """관리자가 다른 사용자 비밀번호 변경 성공 테스트"""
        self.user_service.change_password(
            user_to_change=self.operator,
            old_password='',  # 관리자는 기존 비밀번호 불필요
            new_password='adminchange789',
            new_password_confirm='adminchange789',
            acting_user=self.admin_user
        )
        
        # 비밀번호가 변경되었는지 확인
        self.operator.refresh_from_db()
        assert self.operator.check_password('adminchange789')

    def test_change_password_permission_denied(self):
        """권한 없는 사용자의 타인 비밀번호 변경 시도 테스트"""
        with pytest.raises(PermissionDenied, match='본인의 비밀번호만 변경할 수 있습니다'):
            self.user_service.change_password(
                user_to_change=self.admin_user,
                old_password='test123',
                new_password='hackpass123',
                new_password_confirm='hackpass123',
                acting_user=self.operator
            )

    def test_change_password_wrong_old_password(self):
        """잘못된 기존 비밀번호로 변경 시도 테스트"""
        with pytest.raises(ValidationError, match='기존 비밀번호가 일치하지 않습니다'):
            self.user_service.change_password(
                user_to_change=self.operator,
                old_password='wrongpass',
                new_password='newpass456',
                new_password_confirm='newpass456',
                acting_user=self.operator
            )

    def test_change_password_mismatch_new_passwords(self):
        """새 비밀번호 불일치 테스트"""
        with pytest.raises(ValidationError, match='새 비밀번호가 일치하지 않습니다'):
            self.user_service.change_password(
                user_to_change=self.operator,
                old_password='test123',
                new_password='newpass456',
                new_password_confirm='differentpass789',
                acting_user=self.operator
            )

    def test_change_password_missing_fields(self):
        """필수 필드 누락 테스트"""
        with pytest.raises(ValidationError, match='모든 비밀번호 필드를 입력해주세요'):
            self.user_service.change_password(
                user_to_change=self.operator,
                old_password='',  # 누락
                new_password='newpass456',
                new_password_confirm='newpass456',
                acting_user=self.operator
            )

    def test_change_password_missing_new_password_fields(self):
        """새 비밀번호 필드 누락 테스트"""
        with pytest.raises(ValidationError, match='새 비밀번호 필드를 입력해주세요'):
            self.user_service.change_password(
                user_to_change=self.operator,
                old_password='',  # 이 경우 먼저 다른 에러가 발생하므로 관리자로 테스트
                new_password='',  # 누락
                new_password_confirm='newpass456',
                acting_user=self.admin_user  # 관리자로 변경
            )

    def test_change_password_admin_minimal_fields(self):
        """관리자는 최소 필드만으로도 변경 가능 테스트"""
        self.user_service.change_password(
            user_to_change=self.operator,
            old_password='',  # 관리자는 불필요
            new_password='adminpass123',
            new_password_confirm='adminpass123',
            acting_user=self.admin_user
        )
        
        self.operator.refresh_from_db()
        assert self.operator.check_password('adminpass123')


@pytest.mark.unit
@pytest.mark.django_db
class TestUserQueryService:
    """User Query Service 단위 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.query_service = UserQueryService()
        
        # Test Users
        self.admin_user = User.objects.create_user(
            username='admin_query_test',
            password='test123',
            role='admin'
        )
        
        self.quality_manager = User.objects.create_user(
            username='quality_query_test',
            password='test123',
            role='quality_manager'
        )
        
        self.production_manager = User.objects.create_user(
            username='production_query_test',
            password='test123',
            role='production_manager'
        )
        
        self.operator = User.objects.create_user(
            username='operator_query_test',
            password='test123',
            role='operator'
        )

    def test_get_queryset_for_admin(self):
        """관리자는 모든 사용자 조회 가능 테스트"""
        queryset = self.query_service.get_queryset_for_user(self.admin_user)
        
        # 모든 사용자가 포함되어야 함
        assert queryset.count() >= 4  # 최소 4명 (생성한 사용자들)
        
        user_ids = list(queryset.values_list('id', flat=True))
        assert self.admin_user.id in user_ids
        assert self.quality_manager.id in user_ids
        assert self.production_manager.id in user_ids
        assert self.operator.id in user_ids

    def test_get_queryset_for_quality_manager(self):
        """품질관리자는 모든 사용자 조회 가능 테스트"""
        queryset = self.query_service.get_queryset_for_user(self.quality_manager)
        
        # 모든 사용자가 포함되어야 함
        assert queryset.count() >= 4
        
        user_ids = list(queryset.values_list('id', flat=True))
        assert self.admin_user.id in user_ids
        assert self.quality_manager.id in user_ids

    def test_get_queryset_for_production_manager(self):
        """생산관리자는 자신만 조회 가능 테스트"""
        queryset = self.query_service.get_queryset_for_user(self.production_manager)
        
        # 자신만 조회 가능
        assert queryset.count() == 1
        assert queryset.first().id == self.production_manager.id

    def test_get_queryset_for_operator(self):
        """운영자는 자신만 조회 가능 테스트"""
        queryset = self.query_service.get_queryset_for_user(self.operator)
        
        # 자신만 조회 가능
        assert queryset.count() == 1
        assert queryset.first().id == self.operator.id

    def test_get_queryset_excludes_other_users_for_restricted_roles(self):
        """제한된 역할은 다른 사용자를 볼 수 없음을 확인"""
        operator_queryset = self.query_service.get_queryset_for_user(self.operator)
        production_queryset = self.query_service.get_queryset_for_user(self.production_manager)
        
        # 운영자는 관리자나 품질관리자를 볼 수 없음
        operator_user_ids = list(operator_queryset.values_list('id', flat=True))
        assert self.admin_user.id not in operator_user_ids
        assert self.quality_manager.id not in operator_user_ids
        
        # 생산관리자는 다른 사용자들을 볼 수 없음
        production_user_ids = list(production_queryset.values_list('id', flat=True))
        assert self.admin_user.id not in production_user_ids
        assert self.operator.id not in production_user_ids


@pytest.mark.unit
@pytest.mark.django_db
class TestUserStatsService:
    """User Stats Service 단위 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.stats_service = UserStatsService()
        
        # Test Users with various roles and active status
        self.admin_user = User.objects.create_user(
            username='admin_stats_test',
            password='test123',
            role='admin',
            is_active=True
        )
        
        self.quality_manager = User.objects.create_user(
            username='quality_stats_test',
            password='test123',
            role='quality_manager',
            is_active=True
        )
        
        self.operator_active = User.objects.create_user(
            username='operator_active_test',
            password='test123',
            role='operator',
            is_active=True
        )
        
        self.operator_inactive = User.objects.create_user(
            username='operator_inactive_test',
            password='test123',
            role='operator',
            is_active=False
        )
        
        self.production_manager = User.objects.create_user(
            username='production_stats_test',
            password='test123',
            role='production_manager',
            is_active=True
        )

    def test_get_user_statistics_success_admin(self):
        """관리자의 사용자 통계 조회 성공 테스트"""
        result = self.stats_service.get_user_statistics(self.admin_user)
        
        assert 'total_users' in result
        assert 'active_users' in result
        assert 'inactive_users' in result
        assert 'role_distribution' in result
        
        # 생성한 사용자 수 확인
        assert result['total_users'] >= 5  # 최소 5명
        assert result['active_users'] >= 4  # 활성 사용자 4명
        assert result['inactive_users'] >= 1  # 비활성 사용자 1명
        
        # 역할별 분포 확인
        role_dist = result['role_distribution']
        assert role_dist['관리자'] >= 1  # 관리자 1명
        assert role_dist['품질관리자'] >= 1  # 품질관리자 1명
        assert role_dist['작업자'] >= 2  # 작업자 2명 (활성/비활성)
        assert role_dist['생산관리자'] >= 1  # 생산관리자 1명

    def test_get_user_statistics_success_quality_manager(self):
        """품질관리자의 사용자 통계 조회 성공 테스트"""
        result = self.stats_service.get_user_statistics(self.quality_manager)
        
        assert isinstance(result, dict)
        assert 'total_users' in result
        assert 'role_distribution' in result

    def test_get_user_statistics_permission_denied_operator(self):
        """운영자의 통계 조회 권한 거부 테스트"""
        with pytest.raises(PermissionDenied, match='통계 정보를 조회할 권한이 없습니다'):
            self.stats_service.get_user_statistics(self.operator_active)

    def test_get_user_statistics_permission_denied_production_manager(self):
        """생산관리자의 통계 조회 권한 거부 테스트"""
        with pytest.raises(PermissionDenied, match='통계 정보를 조회할 권한이 없습니다'):
            self.stats_service.get_user_statistics(self.production_manager)

    def test_get_role_choices_success(self):
        """역할 선택지 조회 테스트"""
        result = self.stats_service.get_role_choices()
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        # 각 항목이 올바른 형식인지 확인
        for role_item in result:
            assert 'key' in role_item
            assert 'value' in role_item
            assert isinstance(role_item['key'], str)
            assert isinstance(role_item['value'], str)
        
        # 주요 역할들이 포함되어 있는지 확인
        role_keys = [item['key'] for item in result]
        assert 'admin' in role_keys
        assert 'quality_manager' in role_keys
        assert 'operator' in role_keys
        assert 'production_manager' in role_keys

    def test_user_statistics_counts_consistency(self):
        """통계 수치의 일관성 검증"""
        result = self.stats_service.get_user_statistics(self.admin_user)
        
        # total_users = active_users + inactive_users
        assert result['total_users'] == result['active_users'] + result['inactive_users']
        
        # 역할별 분포의 합이 전체 사용자 수와 일치하는지 확인
        role_total = sum(result['role_distribution'].values())
        assert role_total == result['total_users']

    def test_get_user_statistics_empty_database(self):
        """데이터베이스에 사용자가 없을 때의 통계 테스트"""
        # 모든 테스트 사용자 삭제
        User.objects.all().delete()
        
        # 통계 조회를 위한 새 관리자 생성
        admin = User.objects.create_user(
            username='admin_empty_test',
            password='test123',
            role='admin'
        )
        
        result = self.stats_service.get_user_statistics(admin)
        
        # 관리자만 1명 있어야 함
        assert result['total_users'] == 1
        assert result['active_users'] == 1
        assert result['inactive_users'] == 0
        assert result['role_distribution']['관리자'] == 1