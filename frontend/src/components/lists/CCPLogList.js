import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import ccpService from '../../services/ccpService';

const CCPLogList = ({ ccpId = null, refreshTrigger = 0 }) => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    start_date: '',
    end_date: '',
    status: ''
  });
  const [pagination, setPagination] = useState({
    count: 0,
    next: null,
    previous: null,
    current_page: 1
  });

  const statusLabels = {
    'within_limits': '기준 내',
    'out_of_limits': '기준 이탈',
    'corrective_action': '개선조치'
  };

  const statusColors = {
    'within_limits': 'bg-green-100 text-green-800',
    'out_of_limits': 'bg-red-100 text-red-800',
    'corrective_action': 'bg-yellow-100 text-yellow-800'
  };

  // CCP 로그 조회
  const loadLogs = async (page = 1) => {
    try {
      setLoading(true);
      
      const params = {
        page,
        ...filters
      };
      
      // ccpId가 지정된 경우 특정 CCP의 로그만 조회
      if (ccpId) {
        params.ccp = ccpId;
      }

      const response = await ccpService.getCCPLogs(params);
      setLogs(response.results || []);
      setPagination({
        count: response.count,
        next: response.next,
        previous: response.previous,
        current_page: page
      });

    } catch (error) {
      console.error('CCP 로그 조회 실패:', error);
      toast.error('CCP 로그를 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 초기 로딩 및 필터/새로고침 시 재로딩
  useEffect(() => {
    loadLogs();
  }, [ccpId, filters, refreshTrigger]);

  // 필터 변경 핸들러
  const handleFilterChange = (name, value) => {
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // 필터 초기화
  const resetFilters = () => {
    setFilters({
      start_date: '',
      end_date: '',
      status: ''
    });
  };

  // 페이지 변경
  const handlePageChange = (page) => {
    loadLogs(page);
  };

  // 날짜/시간 포맷팅
  const formatDateTime = (dateTime) => {
    return new Date(dateTime).toLocaleString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // 측정값과 한계기준 비교 표시
  const renderMeasurementStatus = (log) => {
    const { measured_value, unit, ccp } = log;
    const { critical_limit_min, critical_limit_max } = ccp;
    
    let limitInfo = '';
    if (critical_limit_min && critical_limit_max) {
      limitInfo = `(${critical_limit_min}~${critical_limit_max} ${unit})`;
    } else if (critical_limit_min) {
      limitInfo = `(≥${critical_limit_min} ${unit})`;
    } else if (critical_limit_max) {
      limitInfo = `(≤${critical_limit_max} ${unit})`;
    }

    return (
      <div>
        <span className="font-medium">{measured_value} {unit}</span>
        {limitInfo && (
          <div className="text-xs text-gray-500">{limitInfo}</div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">
          {ccpId ? 'CCP 모니터링 로그' : '전체 CCP 로그'}
        </h3>
        <div className="text-sm text-gray-500">
          총 {pagination.count}건
        </div>
      </div>

      {/* 필터 영역 */}
      <div className="mb-4 p-4 bg-gray-50 rounded-lg">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              시작일
            </label>
            <input
              type="date"
              value={filters.start_date}
              onChange={(e) => handleFilterChange('start_date', e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              종료일
            </label>
            <input
              type="date"
              value={filters.end_date}
              onChange={(e) => handleFilterChange('end_date', e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              상태
            </label>
            <select
              value={filters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">전체</option>
              <option value="within_limits">기준 내</option>
              <option value="out_of_limits">기준 이탈</option>
              <option value="corrective_action">개선조치</option>
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={resetFilters}
              className="w-full bg-gray-200 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              필터 초기화
            </button>
          </div>
        </div>
      </div>

      {/* 로그 테이블 */}
      {logs.length > 0 ? (
        <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  CCP
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  측정값
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  측정시간
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  상태
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  작업자
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  비고
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {logs.map(log => (
                <tr key={log.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {log.ccp.name}
                      </div>
                      <div className="text-sm text-gray-500">
                        {log.ccp.code} - {log.ccp.process_step}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {renderMeasurementStatus(log)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatDateTime(log.measured_at)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusColors[log.status]}`}>
                      {statusLabels[log.status]}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {log.created_by?.username || '-'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900 max-w-xs">
                    <div className="truncate">
                      {log.deviation_notes || '-'}
                    </div>
                    {log.corrective_action_taken && (
                      <div className="text-xs text-blue-600 mt-1">
                        개선조치: {log.corrective_action_taken}
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          </div>
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          조건에 맞는 CCP 로그가 없습니다.
        </div>
      )}

      {/* 페이지네이션 */}
      {logs.length > 0 && (pagination.next || pagination.previous) && (
        <div className="flex justify-between items-center mt-4">
          <button
            onClick={() => handlePageChange(pagination.current_page - 1)}
            disabled={!pagination.previous}
            className="bg-gray-200 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            이전
          </button>
          
          <span className="text-sm text-gray-700">
            페이지 {pagination.current_page}
          </span>
          
          <button
            onClick={() => handlePageChange(pagination.current_page + 1)}
            disabled={!pagination.next}
            className="bg-gray-200 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            다음
          </button>
        </div>
      )}
    </div>
  );
};

export default CCPLogList;