import apiClient from './apiClient';

class AuthService {
  // 로그인
  async login(credentials) {
    try {
      const response = await apiClient.post('/api/token/', credentials);
      const { access, refresh } = response.data;
      
      // 토큰을 로컬스토리지에 저장
      localStorage.setItem('accessToken', access);
      localStorage.setItem('refreshToken', refresh);
      
      // 사용자 정보 조회 및 저장
      const userResponse = await apiClient.get('/api/users/me/');
      const user = userResponse.data;
      localStorage.setItem('user', JSON.stringify(user));
      
      return { success: true, user, tokens: { access, refresh } };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || '로그인에 실패했습니다.'
      };
    }
  }
  
  // 로그아웃
  logout() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
  }
  
  // 현재 로그인 상태 확인
  isAuthenticated() {
    const accessToken = localStorage.getItem('accessToken');
    const user = localStorage.getItem('user');
    return !!(accessToken && user);
  }
  
  // 현재 사용자 정보 조회
  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }
  
  // 토큰 검증
  async verifyToken() {
    try {
      const accessToken = localStorage.getItem('accessToken');
      if (!accessToken) return false;
      
      await apiClient.post('/api/token/verify/', { token: accessToken });
      return true;
    } catch (error) {
      return false;
    }
  }
  
  // 사용자 역할 확인
  hasRole(role) {
    const user = this.getCurrentUser();
    return user?.role === role;
  }
  
  // 관리자 권한 확인
  isAdmin() {
    return this.hasRole('admin');
  }
  
  // 품질관리자 권한 확인
  isQualityManager() {
    return this.hasRole('quality_manager');
  }
  
  // 작업자 권한 확인
  isOperator() {
    return this.hasRole('operator');
  }
}

const authServiceInstance = new AuthService();
export default authServiceInstance;