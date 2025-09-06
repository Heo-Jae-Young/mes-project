import React, { useState, useEffect } from 'react';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import Header from '../components/layout/Header';
import ProductForm from '../components/products/ProductForm';
import ProductList from '../components/products/ProductList';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ProductBOMManager from '../components/bom/ProductBOMManager';
import BOMAlert from '../components/products/BOMAlert';
import useEntityPage, { createServiceAdapter } from '../hooks/useEntityPage';
import productService from '../services/productService';

const ProductsPage = () => {
  // productService를 useEntityPage 훅과 호환되도록 어댑터 생성
  const productServiceAdapter = createServiceAdapter(productService, {
    getAll: 'getProducts',
    create: 'createProduct',
    update: 'updateProduct',
    delete: 'deleteProduct'
  });

  // useEntityPage 훅 사용 (기본 CRUD 기능)
  const {
    items: products,
    loading,
    showForm,
    editingItem: editingProduct,
    filters,
    fetchItems: fetchProducts,
    handleCreate: handleCreateProduct,
    handleUpdate: handleUpdateProduct,
    handleDelete: handleDeleteProduct,
    handleEdit: handleEditProduct,
    handleFormClose: handleFormCancel,
    handleFilterChange,
    setShowForm
  } = useEntityPage(productServiceAdapter, '제품', {
    initialFilters: {
      search: '',
      is_active: '',
      bom_status: ''  // 'missing', 'set', '' for all
    },
    // 데이터 변경 후 BOM 알림을 위한 전체 제품 목록 업데이트
    transformData: (data) => {
      const productsList = data.results || data;
      // CRUD 작업 후에는 전체 제품 목록도 업데이트
      fetchAllProducts();
      return productsList;
    }
  });

  // BOM 관리 및 추가 기능용 상태들 (기존 유지)
  const [allProducts, setAllProducts] = useState([]); // BOM 알림용 전체 제품 목록
  const [showBOMManager, setShowBOMManager] = useState(false);
  const [selectedProductForBOM, setSelectedProductForBOM] = useState(null);
  const [showBOMAlert, setShowBOMAlert] = useState(true);

  // 전체 제품 목록 조회 (BOM 알림용)
  const fetchAllProducts = async () => {
    try {
      const data = await productService.getProducts({}); // 필터 없이 전체 조회
      const productsList = data.results || data;
      setAllProducts(productsList);
    } catch (error) {
      console.error('전체 제품 목록 조회 실패:', error);
    }
  };

  // fetchProducts는 useEntityPage 훅에서 제공됨 (삭제됨)

  // BOM 상태에 따른 제품 필터링
  const getFilteredProducts = () => {
    if (!filters.bom_status) return products;
    
    return products.filter(product => {
      if (filters.bom_status === 'missing') {
        return !product.has_bom && product.is_active;
      } else if (filters.bom_status === 'set') {
        return product.has_bom;
      }
      return true;
    });
  };

  const filteredProducts = getFilteredProducts();

  // fetchProducts useEffect는 useEntityPage 훅에서 자동 처리됨 (삭제됨)

  // 컴포넌트 초기 로드 시 전체 제품 목록 조회 (한 번만)
  useEffect(() => {
    fetchAllProducts();
  }, []);

  // handleCreateProduct은 useEntityPage 훅에서 제공됨 (삭제됨)
  // 단, BOM 알림 업데이트를 위해 fetchAllProducts 호출 필요

  // handleUpdateProduct은 useEntityPage 훅에서 제공됨 (삭제됨)
  // 단, BOM 알림 업데이트를 위해 fetchAllProducts 호출 필요

  // handleDeleteProduct은 useEntityPage 훅에서 제공됨 (삭제됨)
  // 단, BOM 알림 업데이트를 위해 fetchAllProducts 호출 필요

  // handleEditProduct은 useEntityPage 훅에서 제공됨 (삭제됨)

  // BOM 관리 모드로 전환
  const handleManageBOM = (product) => {
    setSelectedProductForBOM(product);
    setShowBOMManager(true);
  };

  // handleFilterChange는 useEntityPage 훅에서 제공됨 (삭제됨)

  // handleFormCancel은 useEntityPage 훅에서 제공됨 (삭제됨)

  // BOM 관리 취소 처리
  const handleBOMManagerCancel = () => {
    setShowBOMManager(false);
    setSelectedProductForBOM(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 페이지 헤더 */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">제품 관리</h1>
              <p className="mt-1 text-sm text-gray-500">
                완제품 카탈로그 등록, 수정, 조회 관리
              </p>
            </div>
            <button
              onClick={() => setShowForm(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              제품 등록
            </button>
          </div>
        </div>

        {/* BOM 알림 */}
        {showBOMAlert && (
          <BOMAlert
            products={allProducts}
            onManageBOM={handleManageBOM}
            onDismiss={() => setShowBOMAlert(false)}
          />
        )}

        {/* 필터 영역 */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {/* 검색 */}
            <div className="relative">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                제품 검색
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                  placeholder="제품명, 코드로 검색..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
              </div>
            </div>

            {/* 활성 상태 필터 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                활성 상태
              </label>
              <select
                value={filters.is_active}
                onChange={(e) => handleFilterChange('is_active', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">전체</option>
                <option value="true">활성</option>
                <option value="false">비활성</option>
              </select>
            </div>

            {/* BOM 상태 필터 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                BOM 상태
              </label>
              <select
                value={filters.bom_status}
                onChange={(e) => handleFilterChange('bom_status', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">전체</option>
                <option value="missing">BOM 미설정</option>
                <option value="set">BOM 설정됨</option>
              </select>
            </div>

            {/* 빈 공간 */}
            <div></div>
            
            {/* 통계 정보 */}
            <div className="flex items-end">
              <div className="text-sm text-gray-600 space-y-1">
                <div>
                  총 제품 수: <span className="font-semibold text-gray-900">{products.length}</span>개
                </div>
                {filters.bom_status === 'missing' && (
                  <div className="text-orange-600 font-medium">
                    BOM 미설정: {filteredProducts.length}개
                  </div>
                )}
                {filters.bom_status === '' && (
                  <div className="text-orange-600">
                    BOM 미설정: {products.filter(p => !p.has_bom && p.is_active).length}개
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* 제품 목록 또는 로딩 */}
        {loading ? (
          <LoadingSpinner />
        ) : (
          <ProductList
            products={filteredProducts}
            onEdit={handleEditProduct}
            onDelete={handleDeleteProduct}
            onManageBOM={handleManageBOM}
          />
        )}
      </div>

      {/* 제품 생성/수정 폼 모달 */}
      {showForm && (
        <ProductForm
          product={editingProduct}
          onSubmit={editingProduct ? handleUpdateProduct : handleCreateProduct}
          onCancel={handleFormCancel}
          isEditing={!!editingProduct}
        />
      )}

      {/* BOM 관리 모달 */}
      {showBOMManager && selectedProductForBOM && (
        <ProductBOMManager
          product={selectedProductForBOM}
          onClose={handleBOMManagerCancel}
        />
      )}
    </div>
  );
};

export default ProductsPage;