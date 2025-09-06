import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import Header from '../components/layout/Header';
import ProductForm from '../components/products/ProductForm';
import ProductList from '../components/products/ProductList';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ProductBOMManager from '../components/bom/ProductBOMManager';
import productService from '../services/productService';

const ProductsPage = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [showBOMManager, setShowBOMManager] = useState(false);
  const [selectedProductForBOM, setSelectedProductForBOM] = useState(null);
  const [filters, setFilters] = useState({
    search: '',
    is_active: ''
  });

  // 제품 목록 조회
  const fetchProducts = async () => {
    try {
      setLoading(true);
      const data = await productService.getProducts(filters);
      const productsList = data.results || data;
      setProducts(productsList);
    } catch (error) {
      toast.error('제품 목록을 불러오는데 실패했습니다');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, [filters]);

  // 제품 생성 처리
  const handleCreateProduct = async (productData) => {
    try {
      await productService.createProduct(productData);
      toast.success('제품이 성공적으로 생성되었습니다');
      setShowForm(false);
      fetchProducts();
    } catch (error) {
      const errorMessage = error.response?.data?.non_field_errors?.[0] || 
                          error.response?.data?.message || 
                          '제품 생성에 실패했습니다';
      toast.error(errorMessage);
    }
  };

  // 제품 수정 처리
  const handleUpdateProduct = async (productData) => {
    try {
      await productService.updateProduct(editingProduct.id, productData);
      toast.success('제품이 성공적으로 수정되었습니다');
      setShowForm(false);
      setEditingProduct(null);
      fetchProducts();
    } catch (error) {
      const errorMessage = error.response?.data?.non_field_errors?.[0] || 
                          error.response?.data?.message || 
                          '제품 수정에 실패했습니다';
      toast.error(errorMessage);
    }
  };

  // 제품 삭제 처리
  const handleDeleteProduct = async (productId) => {
    if (!window.confirm('정말로 이 제품을 삭제하시겠습니까?')) {
      return;
    }

    try {
      await productService.deleteProduct(productId);
      toast.success('제품이 성공적으로 삭제되었습니다');
      fetchProducts();
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          '제품 삭제에 실패했습니다';
      toast.error(errorMessage);
    }
  };

  // 제품 수정 모드로 전환
  const handleEditProduct = (product) => {
    setEditingProduct(product);
    setShowForm(true);
  };

  // BOM 관리 모드로 전환
  const handleManageBOM = (product) => {
    setSelectedProductForBOM(product);
    setShowBOMManager(true);
  };

  // 필터 변경 처리
  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value
    }));
  };

  // 폼 취소 처리
  const handleFormCancel = () => {
    setShowForm(false);
    setEditingProduct(null);
  };

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

        {/* 필터 영역 */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
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

            {/* 빈 공간 */}
            <div></div>
            
            {/* 통계 정보 */}
            <div className="flex items-end">
              <div className="text-sm text-gray-600">
                총 제품 수: <span className="font-semibold text-gray-900">{products.length}</span>개
              </div>
            </div>
          </div>
        </div>

        {/* 제품 목록 또는 로딩 */}
        {loading ? (
          <LoadingSpinner />
        ) : (
          <ProductList
            products={products}
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