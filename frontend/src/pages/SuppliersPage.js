import React from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/layout/Header';
import SupplierForm from '../components/suppliers/SupplierForm';
import SupplierList from '../components/suppliers/SupplierList';
import LoadingCard from '../components/common/LoadingCard';
import useEntityPage, { createServiceAdapter } from '../hooks/useEntityPage';
import supplierService from '../services/supplierService';

const SuppliersPage = () => {
  const navigate = useNavigate();
  
  // supplierService를 useEntityPage 훅과 호환되도록 어댑터 생성
  const supplierServiceAdapter = createServiceAdapter(supplierService, {
    getAll: 'getSuppliers',
    create: 'createSupplier',
    update: 'updateSupplier',
    delete: 'deleteSupplier'
  });

  // useEntityPage 훅 사용
  const {
    items: suppliers,
    loading,
    showForm,
    editingItem: editingSupplier,
    filters,
    fetchItems: fetchSuppliers,
    handleCreate: handleCreateSupplier,
    handleUpdate: handleUpdateSupplier,
    handleDelete: handleDeleteSupplier,
    handleEdit,
    handleFormClose,
    handleFilterChange,
    setShowForm
  } = useEntityPage(supplierServiceAdapter, '공급업체', {
    initialFilters: {
      search: '',
      status: ''
    }
  });

  // fetchSuppliers는 useEntityPage 훅에서 제공됨 (삭제됨)

  // fetchSuppliers useEffect는 useEntityPage 훅에서 자동 처리됨 (삭제됨)

  // handleCreateSupplier은 useEntityPage 훅에서 제공됨 (삭제됨)

  // handleUpdateSupplier은 useEntityPage 훅에서 제공됨 (삭제됨)

  // handleDeleteSupplier은 useEntityPage 훅에서 제공됨 (삭제됨)

  // handleEdit은 useEntityPage 훅에서 제공됨 (삭제됨)

  // handleFormClose는 useEntityPage 훅에서 제공됨 (삭제됨)

  // handleFilterChange는 useEntityPage 훅에서 제공됨 (삭제됨)

  // 공급업체 클릭 핸들러
  const handleSupplierClick = (supplier) => {
    navigate(`/suppliers/${supplier.id}`);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 페이지 헤더 */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">공급업체 관리</h1>
              <p className="mt-1 text-sm text-gray-500">
                공급업체 등록, 수정, 조회 및 성과 관리
              </p>
            </div>
            <button
              onClick={() => setShowForm(true)}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
            >
              공급업체 등록
            </button>
          </div>
        </div>

        {/* 필터 영역 */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                상태
              </label>
              <select
                value={filters.status}
                onChange={(e) => handleFilterChange('status', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
              >
                <option value="">전체</option>
                <option value="active">활성</option>
                <option value="inactive">비활성</option>
                <option value="suspended">정지</option>
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
                placeholder="공급업체명, 코드, 담당자로 검색"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
              />
            </div>

            <div className="flex items-end">
              <button
                onClick={fetchSuppliers}
                disabled={loading}
                className="w-full bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors disabled:opacity-50"
              >
                {loading ? '로딩중...' : '새로고침'}
              </button>
            </div>
          </div>
        </div>

        {/* 공급업체 목록 */}
        <div className="bg-white rounded-lg shadow">
          <LoadingCard loading={loading} className="p-8 text-center">
            <SupplierList
              suppliers={suppliers}
              loading={loading}
              onEdit={handleEdit}
              onDelete={handleDeleteSupplier}
              onSupplierClick={handleSupplierClick}
            />
          </LoadingCard>
        </div>

        {/* 공급업체 폼 모달 */}
        {showForm && (
          <SupplierForm
            isOpen={showForm}
            onClose={handleFormClose}
            onSubmit={editingSupplier ? handleUpdateSupplier : handleCreateSupplier}
            supplier={editingSupplier}
          />
        )}
      </div>
    </div>
  );
};

export default SuppliersPage;