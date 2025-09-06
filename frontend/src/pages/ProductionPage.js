import React, { useState } from 'react';
import { toast } from 'react-hot-toast';
import Header from '../components/layout/Header';
import productionService from '../services/productionService';
import ProductionOrderList from '../components/lists/ProductionOrderList';
import ProductionOrderForm from '../components/forms/ProductionOrderForm';
import ProductionControls from '../components/production/ProductionControls';
import LoadingCard from '../components/common/LoadingCard';
import useEntityPage, { createServiceAdapter } from '../hooks/useEntityPage';

const ProductionPage = () => {
  // productionService를 useEntityPage 훅과 호환되도록 어댑터 생성 (삭제 기능 없음)
  const productionServiceAdapter = createServiceAdapter(productionService, {
    getAll: 'getProductionOrders',
    create: 'createProductionOrder',
    update: 'updateProductionOrder',
    delete: null // 삭제 기능 없음
  });

  // useEntityPage 훅 사용 (기본 CRUD - 삭제 제외)
  const {
    items: orders,
    loading,
    showForm: showCreateForm,
    filters,
    fetchItems: fetchOrders,
    handleCreate: handleCreateOrder,
    handleFilterChange,
    setShowForm: setShowCreateForm
  } = useEntityPage(productionServiceAdapter, '생산 주문', {
    initialFilters: {
      status: '',
      priority: '',
      search: ''
    }
  });

  // 생산 제어 전용 상태 (기존 유지)
  const [selectedOrder, setSelectedOrder] = useState(null);

  // fetchOrders는 useEntityPage 훅에서 제공됨 (삭제됨)

  // fetchOrders useEffect는 useEntityPage 훅에서 자동 처리됨 (삭제됨)

  // 생산 시작 처리
  const handleStartProduction = async (orderId) => {
    try {
      await productionService.startProduction(orderId);
      toast.success('생산이 시작되었습니다');
      fetchOrders();
    } catch (error) {
      console.error('생산 시작 에러:', error.response?.data);
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.non_field_errors?.[0] ||
                          error.response?.data?.message ||
                          '생산 시작에 실패했습니다';
      toast.error(errorMessage);
    }
  };

  // 생산 완료 처리
  const handleCompleteProduction = async (orderId, producedQuantity, notes) => {
    try {
      await productionService.completeProduction(orderId, {
        produced_quantity: producedQuantity,
        notes
      });
      toast.success('생산이 완료되었습니다');
      fetchOrders();
    } catch (error) {
      console.error('생산 완료 에러:', error.response?.data);
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.non_field_errors?.[0] ||
                          error.response?.data?.message ||
                          '생산 완료에 실패했습니다';
      toast.error(errorMessage);
    }
  };

  // 생산 일시정지 처리
  const handlePauseProduction = async (orderId, reason) => {
    try {
      await productionService.pauseProduction(orderId, reason);
      toast.success('생산이 일시정지되었습니다');
      fetchOrders();
    } catch (error) {
      toast.error(error.response?.data?.detail || '생산 일시정지에 실패했습니다');
    }
  };

  // 생산 재개 처리
  const handleResumeProduction = async (orderId) => {
    try {
      await productionService.resumeProduction(orderId);
      toast.success('생산이 재개되었습니다');
      fetchOrders();
    } catch (error) {
      toast.error(error.response?.data?.detail || '생산 재개에 실패했습니다');
    }
  };

  // handleCreateOrder는 useEntityPage 훅에서 제공됨 (삭제됨)

  // handleFilterChange는 useEntityPage 훅에서 제공됨 (삭제됨)

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 페이지 헤더 */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">생산 관리</h1>
              <p className="mt-1 text-sm text-gray-500">
                생산 주문 생성, 진행 관리 및 상태 모니터링
              </p>
            </div>
            <button
              onClick={() => setShowCreateForm(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              새 생산 주문
            </button>
          </div>
        </div>

        {/* 필터 영역 */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                상태
              </label>
              <select
                value={filters.status}
                onChange={(e) => handleFilterChange('status', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">전체</option>
                <option value="planned">계획</option>
                <option value="in_progress">생산중</option>
                <option value="completed">완료</option>
                <option value="on_hold">보류</option>
                <option value="cancelled">취소</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                우선순위
              </label>
              <select
                value={filters.priority}
                onChange={(e) => handleFilterChange('priority', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">전체</option>
                <option value="low">낮음</option>
                <option value="normal">보통</option>
                <option value="high">높음</option>
                <option value="urgent">긴급</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                검색
              </label>
              <input
                type="text"
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                placeholder="주문번호, 제품명 검색"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div className="flex items-end">
              <button
                onClick={fetchOrders}
                disabled={loading}
                className="w-full bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors disabled:opacity-50"
              >
                {loading ? '로딩중...' : '새로고침'}
              </button>
            </div>
          </div>
        </div>

        {/* 생산 주문 목록 */}
        <LoadingCard loading={loading} className="p-8 text-center">
          <ProductionOrderList
            orders={orders}
            onStartProduction={handleStartProduction}
            onCompleteProduction={handleCompleteProduction}
            onPauseProduction={handlePauseProduction}
            onResumeProduction={handleResumeProduction}
            onSelectOrder={setSelectedOrder}
          />
        </LoadingCard>

        {/* 생산 주문 생성 모달 */}
        {showCreateForm && (
          <ProductionOrderForm
            onClose={() => setShowCreateForm(false)}
            onSubmit={handleCreateOrder}
          />
        )}

        {/* 생산 제어 패널 */}
        {selectedOrder && (
          <ProductionControls
            order={selectedOrder}
            onClose={() => setSelectedOrder(null)}
            onStartProduction={handleStartProduction}
            onCompleteProduction={handleCompleteProduction}
            onPauseProduction={handlePauseProduction}
            onResumeProduction={handleResumeProduction}
          />
        )}
      </div>
    </div>
  );
};

export default ProductionPage;