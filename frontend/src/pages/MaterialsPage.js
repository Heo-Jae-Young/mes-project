import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import Header from '../components/layout/Header';
import MaterialForm from '../components/materials/MaterialForm';
import MaterialList from '../components/materials/MaterialList';
import LoadingCard from '../components/common/LoadingCard';
import useEntityPage, { createServiceAdapter } from '../hooks/useEntityPage';
import materialService from '../services/materialService';
import supplierService from '../services/supplierService';

const MaterialsPage = () => {
  const navigate = useNavigate();
  
  // materialService를 useEntityPage 훅과 호환되도록 어댑터 생성
  const materialServiceAdapter = createServiceAdapter(materialService, {
    getAll: 'getMaterials',
    create: 'createMaterial',
    update: 'updateMaterial',
    delete: 'deleteMaterial'
  });

  // useEntityPage 훅 사용
  const {
    items: materials,
    loading,
    showForm,
    editingItem: editingMaterial,
    filters,
    fetchItems: fetchMaterials,
    handleCreate: handleCreateMaterial,
    handleUpdate: handleUpdateMaterial,
    handleDelete: handleDeleteMaterial,
    handleEdit,
    handleFormClose,
    handleFilterChange,
    setShowForm
  } = useEntityPage(materialServiceAdapter, '원자재', {
    initialFilters: {
      search: '',
      category: '',
      supplier: '',
      is_active: ''
    },
    transformData: (data) => {
      const materialsList = data.results || data;
      // 재고 정보 처리를 위해 setInventoryData 호출
      const inventorySummary = {};
      materialsList.forEach(material => {
        if (material.inventory_info) {
          inventorySummary[material.id] = material.inventory_info;
        }
      });
      setInventoryData(inventorySummary);
      return materialsList;
    }
  });

  // 기존 상태들 (useEntityPage로 커버되지 않는 것들)
  const [suppliers, setSuppliers] = useState([]);
  const [categories, setCategories] = useState([]);
  const [inventoryData, setInventoryData] = useState({});
  // fetchMaterials는 useEntityPage 훅에서 제공됨 (삭제됨)

  // fetchMaterials useEffect는 useEntityPage 훅에서 자동 처리됨 (삭제됨)

  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const [suppliersData, categoriesData] = await Promise.all([
          supplierService.getSuppliers(),
          materialService.getMaterialCategories()
        ]);
        
        setSuppliers(suppliersData.results || suppliersData);
        setCategories(categoriesData);
      } catch (error) {
        console.error('초기 데이터 로드 실패:', error);
        toast.error('데이터를 불러오는데 실패했습니다.');
      }
    };
    loadInitialData();
  }, []);


  // handleCreateMaterial은 useEntityPage 훅에서 제공됨 (삭제됨)

  // handleUpdateMaterial은 useEntityPage 훅에서 제공됨 (삭제됨)

  // handleDeleteMaterial은 useEntityPage 훅에서 제공됨 (삭제됨)

  // handleEdit은 useEntityPage 훅에서 제공됨 (삭제됨)

  // handleFormClose는 useEntityPage 훅에서 제공됨 (삭제됨)

  // handleFilterChange는 useEntityPage 훅에서 제공됨 (삭제됨)

  // 원자재 클릭 핸들러
  const handleMaterialClick = (material) => {
    navigate(`/materials/${material.id}`);
  };


  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 페이지 헤더 */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">원자재 관리</h1>
              <p className="mt-1 text-sm text-gray-500">
                원자재 카탈로그 등록, 수정, 조회 관리
              </p>
            </div>
            <button
              onClick={() => setShowForm(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              원자재 등록
            </button>
          </div>
        </div>

        {/* 필터 영역 */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                카테고리
              </label>
              <select
                value={filters.category}
                onChange={(e) => handleFilterChange('category', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">전체</option>
                {categories.map((category) => (
                  <option key={category.key} value={category.key}>
                    {category.value}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                공급업체
              </label>
              <select
                value={filters.supplier}
                onChange={(e) => handleFilterChange('supplier', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">전체</option>
                {suppliers.map((supplier) => (
                  <option key={supplier.id} value={supplier.id}>
                    {supplier.name}
                  </option>
                ))}
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
                placeholder="원자재명, 코드로 검색"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div className="flex items-end">
              <button
                onClick={fetchMaterials}
                disabled={loading}
                className="w-full bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors disabled:opacity-50"
              >
                {loading ? '로딩중...' : '새로고침'}
              </button>
            </div>
          </div>
        </div>

        {/* 원자재 목록 */}
        <LoadingCard loading={loading} className="p-8 text-center">
          <MaterialList
            materials={materials}
            suppliers={suppliers}
            categories={categories}
            inventoryData={inventoryData}
            loading={loading}
            onEdit={handleEdit}
            onDelete={handleDeleteMaterial}
            onMaterialClick={handleMaterialClick}
          />
        </LoadingCard>

        {/* 원자재 폼 모달 */}
        {showForm && (
          <MaterialForm
            isOpen={showForm}
            onClose={handleFormClose}
            onSubmit={editingMaterial ? handleUpdateMaterial : handleCreateMaterial}
            material={editingMaterial}
            suppliers={suppliers}
            categories={categories}
          />
        )}
      </div>
    </div>
  );
};

export default MaterialsPage;