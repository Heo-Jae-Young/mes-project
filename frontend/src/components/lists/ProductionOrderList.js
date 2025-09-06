import React from 'react';
import { formatDateTime, formatDate } from '../../utils/dateFormatter';

const ProductionOrderList = ({ 
  orders, 
  onStartProduction, 
  onCompleteProduction, 
  onPauseProduction, 
  onResumeProduction,
  onSelectOrder 
}) => {
  // 상태 배지 스타일
  const getStatusBadge = (status) => {
    const statusStyles = {
      planned: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-yellow-100 text-yellow-800',
      completed: 'bg-green-100 text-green-800',
      on_hold: 'bg-gray-100 text-gray-800',
      cancelled: 'bg-red-100 text-red-800'
    };

    const statusLabels = {
      planned: '계획',
      in_progress: '생산중',
      completed: '완료',
      on_hold: '보류',
      cancelled: '취소'
    };

    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusStyles[status] || 'bg-gray-100 text-gray-800'}`}>
        {statusLabels[status] || status}
      </span>
    );
  };

  // 우선순위 배지 스타일
  const getPriorityBadge = (priority) => {
    const priorityStyles = {
      low: 'bg-gray-100 text-gray-600',
      normal: 'bg-blue-100 text-blue-600',
      high: 'bg-orange-100 text-orange-600',
      urgent: 'bg-red-100 text-red-600'
    };

    const priorityLabels = {
      low: '낮음',
      normal: '보통',
      high: '높음',
      urgent: '긴급'
    };

    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${priorityStyles[priority] || 'bg-gray-100 text-gray-600'}`}>
        {priorityLabels[priority] || priority}
      </span>
    );
  };

  // 진행률 계산
  const getProgressPercentage = (order) => {
    if (order.status === 'completed') return 100;
    if (order.status === 'planned') return 0;
    if (order.produced_quantity && order.planned_quantity) {
      return Math.min((order.produced_quantity / order.planned_quantity) * 100, 100);
    }
    return order.status === 'in_progress' ? 50 : 0;
  };

  // 액션 버튼 렌더링
  const renderActionButtons = (order) => {
    switch (order.status) {
      case 'planned':
        return (
          <button
            onClick={() => onStartProduction(order.id)}
            className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 transition-colors"
          >
            생산 시작
          </button>
        );
      
      case 'in_progress':
        return (
          <div className="flex space-x-2">
            <button
              onClick={() => onSelectOrder(order)}
              className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 transition-colors"
            >
              완료 처리
            </button>
            <button
              onClick={() => onPauseProduction(order.id, '사용자 요청')}
              className="bg-yellow-600 text-white px-3 py-1 rounded text-sm hover:bg-yellow-700 transition-colors"
            >
              일시정지
            </button>
          </div>
        );
      
      case 'on_hold':
        return (
          <button
            onClick={() => onResumeProduction(order.id)}
            className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 transition-colors"
          >
            재개
          </button>
        );
      
      default:
        return null;
    }
  };

  if (!orders || orders.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500">
        생산 주문이 없습니다.
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              주문 정보
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              제품
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              수량
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              일정
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              상태/우선순위
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              진행률
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              작업
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {orders.map((order) => {
            const progress = getProgressPercentage(order);
            
            return (
              <tr key={order.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      {order.order_number}
                    </div>
                    <div className="text-sm text-gray-500">
                      생성: {formatDate(order.created_at)}
                    </div>
                    {order.assigned_operator && (
                      <div className="text-sm text-gray-500">
                        담당: {order.assigned_operator.username}
                      </div>
                    )}
                  </div>
                </td>
                
                <td className="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      {order.finished_product?.name || '제품명 없음'}
                    </div>
                    <div className="text-sm text-gray-500">
                      {order.finished_product?.code || ''}
                    </div>
                  </div>
                </td>
                
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    <div>계획: {order.planned_quantity?.toLocaleString()}</div>
                    {order.produced_quantity > 0 && (
                      <div>실제: {order.produced_quantity?.toLocaleString()}</div>
                    )}
                  </div>
                </td>
                
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <div>
                    <div>시작: {formatDate(order.planned_start_date)}</div>
                    <div>종료: {formatDate(order.planned_end_date)}</div>
                    {order.actual_start_date && (
                      <div className="text-green-600">
                        실제 시작: {formatDate(order.actual_start_date)}
                      </div>
                    )}
                    {order.actual_end_date && (
                      <div className="text-blue-600">
                        실제 종료: {formatDate(order.actual_end_date)}
                      </div>
                    )}
                  </div>
                </td>
                
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="space-y-2">
                    {getStatusBadge(order.status)}
                    {getPriorityBadge(order.priority)}
                  </div>
                </td>
                
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        progress === 100 ? 'bg-green-500' :
                        progress > 50 ? 'bg-blue-500' :
                        progress > 0 ? 'bg-yellow-500' :
                        'bg-gray-300'
                      }`}
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {Math.round(progress)}%
                  </div>
                </td>
                
                <td className="px-6 py-4 whitespace-nowrap">
                  {renderActionButtons(order)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      </div>
    </div>
  );
};

export default ProductionOrderList;