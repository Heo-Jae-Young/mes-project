import React, { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

const DashboardPage = () => {
  const { user } = useContext(AuthContext);

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

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* 헤더 */}
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h1 className="text-2xl font-bold text-gray-900">
                HACCP MES 대시보드
              </h1>
              <p className="mt-1 text-sm text-gray-600">
                환영합니다, {user?.username}님 ({getRoleDisplayName(user?.role)})
              </p>
            </div>
          </div>
        </div>

        {/* 메인 컨텐츠 */}
        <div className="px-4 py-6 sm:px-0">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* CCP 모니터링 카드 */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                      <span className="text-white text-sm font-semibold">CCP</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        중요관리점 모니터링
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        실시간 모니터링 중
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-5 py-3">
                <div className="text-sm">
                  <button className="font-medium text-blue-600 hover:text-blue-500">
                    CCP 로그 보기
                  </button>
                </div>
              </div>
            </div>

            {/* 생산 현황 카드 */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                      <span className="text-white text-sm font-semibold">생산</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        생산 현황
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        정상 운영 중
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-5 py-3">
                <div className="text-sm">
                  <button className="font-medium text-green-600 hover:text-green-500">
                    생산 주문 보기
                  </button>
                </div>
              </div>
            </div>

            {/* 품질 관리 카드 */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center">
                      <span className="text-white text-sm font-semibold">품질</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        품질 관리
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        검사 대기 중
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-5 py-3">
                <div className="text-sm">
                  <button className="font-medium text-yellow-600 hover:text-yellow-500">
                    품질 검사 보기
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* 최근 활동 */}
          <div className="mt-8">
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900">
                  최근 활동
                </h3>
                <div className="mt-5">
                  <div className="flow-root">
                    <ul className="-my-5 divide-y divide-gray-200">
                      <li className="py-5">
                        <div className="relative focus-within:ring-2 focus-within:ring-indigo-500">
                          <h3 className="text-sm font-semibold text-gray-800">
                            CCP-001 온도 측정 완료
                          </h3>
                          <p className="mt-1 text-sm text-gray-600">
                            냉장고 온도: 4.2°C (정상 범위)
                          </p>
                          <p className="mt-1 text-xs text-gray-500">
                            5분 전
                          </p>
                        </div>
                      </li>
                      <li className="py-5">
                        <div className="relative focus-within:ring-2 focus-within:ring-indigo-500">
                          <h3 className="text-sm font-semibold text-gray-800">
                            생산 주문 #PO-2025-001 시작
                          </h3>
                          <p className="mt-1 text-sm text-gray-600">
                            제품: 프리미엄 소시지, 수량: 1000개
                          </p>
                          <p className="mt-1 text-xs text-gray-500">
                            1시간 전
                          </p>
                        </div>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;