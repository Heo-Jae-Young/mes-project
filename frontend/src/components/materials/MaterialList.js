import React from 'react';
import { PencilIcon, TrashIcon } from '@heroicons/react/24/outline';
import LoadingSpinner from '../common/LoadingSpinner';

const MaterialList = ({ 
  materials = [],
  suppliers = [],
  categories = [],
  inventoryData = {}, // 원자재별 재고 정보
  loading = false,
  onEdit,
  onDelete,
  onMaterialClick
}) => {

  // 카테고리 표시명 가져오기
  const getCategoryDisplayName = (categoryKey) => {
    const category = categories.find(cat => cat.key === categoryKey);
    return category ? category.value : categoryKey;
  };

  // 공급업체명 가져오기
  const getSupplierName = (material) => {
    // material.supplier가 객체인 경우 (조회 API)
    if (material.supplier && typeof material.supplier === 'object') {
      return material.supplier.name;
    }
    
    // material.supplier가 UUID인 경우 (목록에서 찾기)
    const supplierId = material.supplier;
    const supplier = suppliers.find(sup => sup.id === supplierId);
    return supplier ? supplier.name : '알 수 없음';
  };

  // 활성 상태 배지
  const getActiveBadge = (isActive) => {
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
        isActive 
          ? 'bg-green-100 text-green-800' 
          : 'bg-red-100 text-red-800'
      }`}>
        {isActive ? '활성' : '비활성'}
      </span>
    );
  };

  // 보관 온도 표시
  const getStorageTemp = (material) => {
    if (material.storage_temp_min !== null && material.storage_temp_max !== null) {
      return `${material.storage_temp_min}°C ~ ${material.storage_temp_max}°C`;
    } else if (material.storage_temp_min !== null) {
      return `${material.storage_temp_min}°C 이상`;
    } else if (material.storage_temp_max !== null) {
      return `${material.storage_temp_max}°C 이하`;
    }
    return '상온';
  };

  // 재고 현황 표시
  const getInventoryInfo = (material) => {
    const inventory = inventoryData[material.id];
    if (!inventory) {
      return {
        totalQuantity: 0,
        activeLots: 0,
        nearExpiry: 0,
        totalValue: 0
      };
    }
    return inventory;
  };

  // 재고 수준 색상
  const getStockLevelColor = (quantity) => {
    if (quantity <= 0) return 'text-red-600';
    if (quantity <= 10) return 'text-orange-600';
    return 'text-green-600';
  };

  // 통화 포맷
  const formatCurrency = (value) => {
    if (!value || value === 0) return '-';
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW',
      minimumFractionDigits: 0,
    }).format(value);
  };

  if (loading && materials.length === 0) {
    return <LoadingSpinner size="large" />;
  }

  return (
    materials.length === 0 && !loading ? (
      <div className="text-center py-12 bg-white rounded-lg border">
        <p className="text-gray-500">등록된 원자재가 없습니다.</p>
      </div>
    ) : (
      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  기본 정보
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  카테고리/공급업체
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  보관 조건
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  재고 현황
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  상태
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  작업
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {materials.map((material) => (
                <tr 
                  key={material.id} 
                  className="hover:bg-gray-50 cursor-pointer"
                  onClick={() => onMaterialClick && onMaterialClick(material)}
                >
                  <td className="px-6 py-4">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {material.name}
                      </div>
                      <div className="text-sm text-gray-500">
                        {material.code} • {material.unit}
                      </div>
                      {material.description && (
                        <div className="text-xs text-gray-400 mt-1">
                          {material.description}
                        </div>
                      )}
                    </div>
                  </td>
                  
                  <td className="px-6 py-4">
                    <div>
                      <div className="text-sm text-gray-900">
                        {getCategoryDisplayName(material.category)}
                      </div>
                      <div className="text-sm text-gray-500">
                        {getSupplierName(material)}
                      </div>
                    </div>
                  </td>
                  
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">
                      <div>온도: {getStorageTemp(material)}</div>
                      {material.shelf_life_days && (
                        <div className="text-xs text-gray-500 mt-1">
                          유통기한: {material.shelf_life_days}일
                        </div>
                      )}
                    </div>
                  </td>
                  
                  <td className="px-6 py-4">
                    {(() => {
                      const inventory = getInventoryInfo(material);
                      return (
                        <div className="text-sm">
                          <div className={`font-medium ${getStockLevelColor(inventory.totalQuantity)}`}>
                            {inventory.totalQuantity} {material.unit}
                          </div>
                          <div className="text-xs text-gray-500">
                            {inventory.activeLots}개 로트
                          </div>
                          {inventory.nearExpiry > 0 && (
                            <div className="text-xs text-orange-600">
                              임박: {inventory.nearExpiry}건
                            </div>
                          )}
                          <div className="text-xs text-gray-500">
                            {formatCurrency(inventory.totalValue)}
                          </div>
                        </div>
                      );
                    })()}
                  </td>
                  
                  <td className="px-6 py-4">
                    {getActiveBadge(material.is_active)}
                  </td>
                  
                  <td className="px-6 py-4">
                    <div className="flex space-x-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onEdit(material);
                        }}
                        className="text-blue-600 hover:text-blue-900 transition-colors"
                        title="수정"
                      >
                        <PencilIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onDelete(material.id);
                        }}
                        className="text-red-600 hover:text-red-900 transition-colors"
                        title="삭제"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    )
  );
};

export default MaterialList;