import React, { useState } from 'react';
import { formatDateTime, formatDate } from '../../utils/dateFormatter';

const ProductionControls = ({ 
  order, 
  onClose, 
  onStartProduction, 
  onCompleteProduction, 
  onPauseProduction, 
  onResumeProduction 
}) => {
  const [showCompleteForm, setShowCompleteForm] = useState(false);
  const [showPauseForm, setShowPauseForm] = useState(false);
  const [completionData, setCompletionData] = useState({
    produced_quantity: order.planned_quantity || '',
    notes: ''
  });
  const [pauseReason, setPauseReason] = useState('');

  // 생산 완료 처리
  const handleComplete = () => {
    onCompleteProduction(order.id, completionData.produced_quantity, completionData.notes);
    setShowCompleteForm(false);
    onClose();
  };

  // 일시정지 처리
  const handlePause = () => {
    onPauseProduction(order.id, pauseReason);
    setShowPauseForm(false);
    onClose();
  };

  // 상태별 배지 스타일
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
      <span className={`px-2 py-1 text-sm font-medium rounded-full ${statusStyles[status] || 'bg-gray-100 text-gray-800'}`}>
        {statusLabels[status] || status}
      </span>
    );
  };

  // 진행률 계산
  const getProgressPercentage = () => {
    if (order.status === 'completed') return 100;
    if (order.status === 'planned') return 0;
    if (order.produced_quantity && order.planned_quantity) {
      return Math.min((order.produced_quantity / order.planned_quantity) * 100, 100);
    }
    return order.status === 'in_progress' ? 50 : 0;
  };

  const progress = getProgressPercentage();

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-10 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-gray-900">
            생산 주문 제어판
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        {/* 주문 정보 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-3">주문 정보</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">주문번호:</span>
                <span className="font-medium">{order.order_number}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">제품:</span>
                <span className="font-medium">{order.finished_product?.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">상태:</span>
                {getStatusBadge(order.status)}
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">담당자:</span>
                <span className="font-medium">{order.assigned_operator?.username || '미배정'}</span>
              </div>
            </div>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-3">생산 현황</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">계획 수량:</span>
                <span className="font-medium">{order.planned_quantity?.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">생산 수량:</span>
                <span className="font-medium">{order.produced_quantity?.toLocaleString() || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">계획 기간:</span>
                <span className="font-medium">
                  {formatDate(order.planned_start_date)} ~ {formatDate(order.planned_end_date)}
                </span>
              </div>
              {order.actual_start_date && (
                <div className="flex justify-between">
                  <span className="text-gray-600">실제 시작:</span>
                  <span className="font-medium text-green-600">
                    {formatDateTime(order.actual_start_date)}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* 진행률 표시 */}
        <div className="mb-6">
          <div className="flex justify-between text-sm text-gray-600 mb-1">
            <span>생산 진행률</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className={`h-3 rounded-full transition-all duration-300 ${
                progress === 100 ? 'bg-green-500' :
                progress > 50 ? 'bg-blue-500' :
                progress > 0 ? 'bg-yellow-500' :
                'bg-gray-300'
              }`}
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* 제어 버튼들 */}
        <div className="flex justify-center space-x-4 mb-6">
          {order.status === 'planned' && (
            <button
              onClick={() => {
                onStartProduction(order.id);
                onClose();
              }}
              className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors"
            >
              생산 시작
            </button>
          )}

          {order.status === 'in_progress' && (
            <>
              <button
                onClick={() => setShowCompleteForm(true)}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                생산 완료
              </button>
              <button
                onClick={() => setShowPauseForm(true)}
                className="bg-yellow-600 text-white px-6 py-2 rounded-lg hover:bg-yellow-700 transition-colors"
              >
                일시정지
              </button>
            </>
          )}

          {order.status === 'on_hold' && (
            <button
              onClick={() => {
                onResumeProduction(order.id);
                onClose();
              }}
              className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors"
            >
              생산 재개
            </button>
          )}
        </div>

        {/* 생산 완료 폼 */}
        {showCompleteForm && (
          <div className="bg-blue-50 p-4 rounded-lg mb-4">
            <h4 className="font-semibold text-blue-900 mb-3">생산 완료 처리</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  실제 생산량 *
                </label>
                <input
                  type="number"
                  value={completionData.produced_quantity}
                  onChange={(e) => setCompletionData(prev => ({
                    ...prev,
                    produced_quantity: parseInt(e.target.value) || ''
                  }))}
                  min="1"
                  max={Math.floor(order.planned_quantity * 1.1)} // 10% 초과 방지
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="실제로 생산된 수량"
                />
                <p className="text-xs text-gray-500 mt-1">
                  최대: {Math.floor(order.planned_quantity * 1.1).toLocaleString()} (계획량의 110%)
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  완료 메모
                </label>
                <textarea
                  value={completionData.notes}
                  onChange={(e) => setCompletionData(prev => ({
                    ...prev,
                    notes: e.target.value
                  }))}
                  rows="3"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="생산 완료에 대한 메모사항"
                />
              </div>
            </div>
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => setShowCompleteForm(false)}
                className="px-4 py-2 text-sm text-gray-600 bg-gray-100 rounded hover:bg-gray-200 transition-colors"
              >
                취소
              </button>
              <button
                onClick={handleComplete}
                disabled={!completionData.produced_quantity || completionData.produced_quantity <= 0}
                className="px-4 py-2 text-sm text-white bg-blue-600 rounded hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                완료 처리
              </button>
            </div>
          </div>
        )}

        {/* 일시정지 폼 */}
        {showPauseForm && (
          <div className="bg-yellow-50 p-4 rounded-lg mb-4">
            <h4 className="font-semibold text-yellow-900 mb-3">생산 일시정지</h4>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                일시정지 사유 *
              </label>
              <textarea
                value={pauseReason}
                onChange={(e) => setPauseReason(e.target.value)}
                rows="3"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500"
                placeholder="일시정지 사유를 입력해주세요"
                required
              />
            </div>
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => setShowPauseForm(false)}
                className="px-4 py-2 text-sm text-gray-600 bg-gray-100 rounded hover:bg-gray-200 transition-colors"
              >
                취소
              </button>
              <button
                onClick={handlePause}
                disabled={!pauseReason.trim()}
                className="px-4 py-2 text-sm text-white bg-yellow-600 rounded hover:bg-yellow-700 transition-colors disabled:opacity-50"
              >
                일시정지
              </button>
            </div>
          </div>
        )}

        {/* 메모 표시 */}
        {order.notes && (
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-gray-900 mb-2">메모</h4>
            <p className="text-sm text-gray-700 whitespace-pre-line">{order.notes}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProductionControls;