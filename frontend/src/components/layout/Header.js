import React, { useContext } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';

const Header = () => {
  const { user, logout } = useContext(AuthContext);
  const location = useLocation();

  const getRoleDisplayName = (role) => {
    switch (role) {
      case 'admin':
        return '관리자';
      case 'quality_manager':
        return '품질관리자';
      case 'operator':
        return '작업자';
      default:
        return role;
    }
  };

  const handleLogout = () => {
    if (window.confirm('로그아웃 하시겠습니까?')) {
      logout();
    }
  };

  return (
    <header className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Link to="/dashboard" className="text-xl font-bold text-gray-900 hover:text-gray-700">
                HACCP MES
              </Link>
            </div>
            
            {/* 네비게이션 메뉴 */}
            <nav className="hidden md:ml-8 md:flex md:space-x-8">
              <Link
                to="/dashboard"
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  location.pathname === '/dashboard'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                }`}
              >
                대시보드
              </Link>
              <Link
                to="/materials"
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  location.pathname === '/materials'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                }`}
              >
                원자재 관리
              </Link>
              <Link
                to="/production"
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  location.pathname === '/production'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                }`}
              >
                생산 관리
              </Link>
              <Link
                to="/ccp-logs"
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  location.pathname === '/ccp-logs'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                }`}
              >
                품질 관리
              </Link>
            </nav>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-700">
              <span className="font-medium">{user?.username}</span>
              <span className="ml-1 text-gray-500">
                ({getRoleDisplayName(user?.role)})
              </span>
            </div>
            
            <button
              onClick={handleLogout}
              className="bg-gray-800 text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-white"
            >
              로그아웃
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;