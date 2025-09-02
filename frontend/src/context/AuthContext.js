import React, { createContext, useState, useEffect } from 'react';
import authService from '../services/authService';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const handleLogout = () => {
    authService.logout();
    setUser(null);
    // 필요시 로그인 페이지로 리디렉션
    if (window.location.pathname !== '/login') {
      window.location.href = '/login';
    }
  };

  // 초기화: 로컬스토리지에서 사용자 정보 불러오기
  useEffect(() => {
    const initAuth = async () => {
      if (authService.isAuthenticated()) {
        const currentUser = authService.getCurrentUser();
        setUser(currentUser);

        // 토큰 유효성 검증
        const isValid = await authService.verifyToken();
        if (!isValid) {
          // 토큰이 만료된 경우 로그아웃
          handleLogout();
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (credentials) => {
    const result = await authService.login(credentials);
    if (result.success) {
      setUser(result.user);
    }
    return result;
  };


  const value = {
    user,
    login,
    logout: handleLogout,
    isAuthenticated: !!user,
    loading,
    // 권한 관련 헬퍼 메소드들
    hasRole: (role) => user?.role === role,
    isAdmin: () => user?.role === 'admin',
    isQualityManager: () => user?.role === 'quality_manager',
    isOperator: () => user?.role === 'operator',
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};