import React, { useContext, useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import Header from '../components/layout/Header';
import InventorySummary from '../components/inventory/InventorySummary';
import InventoryAlerts from '../components/inventory/InventoryAlerts';
import apiClient from '../services/apiClient';
import { toast } from 'react-hot-toast';

const DashboardPage = () => {
  const { user } = useContext(AuthContext);
  const [stats, setStats] = useState(null);
  const [recentCcpLogs, setRecentCcpLogs] = useState([]);
  const [activeProductionOrders, setActiveProductionOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        // 여러 API를 병렬로 호출
        const [statsRes, ccpLogsRes, prodOrdersRes] = await Promise.all([
          apiClient.get('/statistics/'),
          apiClient.get('/ccp-logs/?limit=5'), // 최근 5개만
          apiClient.get('/production-orders/?status=in_progress'),
        ]);

        setStats(statsRes.data);
        setRecentCcpLogs(ccpLogsRes.data.results);
        setActiveProductionOrders(prodOrdersRes.data.results);

      } catch (error) {
        toast.error('대시보드 데이터를 불러오는 중 오류가 발생했습니다.');
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

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

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p>대시보드 데이터를 불러오는 중입니다...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
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
          {/* 재고 현황 요약 */}
          <InventorySummary />
          
          {/* 재고 알림 */}
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-6">재고 알림</h2>
            <InventoryAlerts />
          </div>

          {/* 시스템 현황 카드들 */}
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-6">시스템 현황</h2>
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
                        HACCP 준수율
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {stats ? `${stats.compliance_rate}%` : '로딩 중...'}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-5 py-3">
                <div className="text-sm">
                  <Link to="/ccp-logs" className="font-medium text-blue-600 hover:text-blue-500">
                    CCP 로그 보기
                  </Link>
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
                        진행중인 생산 오더
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {activeProductionOrders ? `${activeProductionOrders.length} 건` : '로딩 중...'}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-5 py-3">
                <div className="text-sm">
                  <Link to="/production" className="font-medium text-green-600 hover:text-green-500">
                    생산 주문 보기
                  </Link>
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
                        최근 중요 이탈
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {stats ? `${stats.critical_issues_count} 건` : '로딩 중...'}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-5 py-3">
                <div className="text-sm">
                  <button className="font-medium text-yellow-600 hover:text-yellow-500">
                    이슈 목록 보기
                  </button>
                </div>
              </div>
            </div>
          </div>
          </div>

          {/* 최근 활동 */}
          <div className="mt-8">
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900">
                  최근 CCP 로그
                </h3>
                <div className="mt-5">
                  <div className="flow-root">
                    {recentCcpLogs.length > 0 ? (
                      <ul className="-my-5 divide-y divide-gray-200">
                        {recentCcpLogs.map((log) => (
                          <li key={log.id} className="py-5">
                            <div className="relative focus-within:ring-2 focus-within:ring-indigo-500">
                              <h3 className="text-sm font-semibold text-gray-800">
                                {log.ccp.name} - {log.measured_value}{log.unit}
                              </h3>
                              <p className={`mt-1 text-sm ${log.is_within_limits ? 'text-green-600' : 'text-red-600'}`}>
                                {log.is_within_limits ? '정상' : '이탈'} - {log.status}
                              </p>
                              <p className="mt-1 text-xs text-gray-500">
                                {new Date(log.created_at).toLocaleString()}
                              </p>
                            </div>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-sm text-gray-500">최근 활동이 없습니다.</p>
                    )}
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
