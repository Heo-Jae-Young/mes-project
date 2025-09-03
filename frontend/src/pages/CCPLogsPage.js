import React, { useState } from 'react';
import Header from '../components/layout/Header';
import CCPLogForm from '../components/forms/CCPLogForm';
import CCPLogList from '../components/lists/CCPLogList';

const CCPLogsPage = () => {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [activeTab, setActiveTab] = useState('logs'); // 'logs' | 'new'

  const handleLogSubmitSuccess = () => {
    // 새로운 로그가 생성되면 목록을 새로고침
    setRefreshTrigger(prev => prev + 1);
    // 로그 목록 탭으로 자동 전환
    setActiveTab('logs');
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">CCP 모니터링 로그</h1>
          <p className="mt-1 text-sm text-gray-600">
            중요 관리점(CCP) 모니터링 데이터를 입력하고 조회합니다.
          </p>
        </div>

        {/* 탭 메뉴 */}
        <div className="mb-6">
          <nav className="flex space-x-8" aria-label="Tabs">
            <button
              onClick={() => setActiveTab('logs')}
              className={`whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'logs'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              로그 목록
            </button>
            <button
              onClick={() => setActiveTab('new')}
              className={`whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'new'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              새 로그 입력
            </button>
          </nav>
        </div>

        {/* 탭 내용 */}
        <div>
          {activeTab === 'logs' && (
            <CCPLogList refreshTrigger={refreshTrigger} />
          )}
          
          {activeTab === 'new' && (
            <CCPLogForm onSubmitSuccess={handleLogSubmitSuccess} />
          )}
        </div>
      </div>
    </div>
  );
};

export default CCPLogsPage;