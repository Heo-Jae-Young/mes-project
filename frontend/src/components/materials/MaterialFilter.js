import React, { useState, useEffect, useRef } from 'react';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';

const MaterialFilter = ({ 
  suppliers = [],
  categories = [],
  filters = {},
  onFilterChange,
  onRefresh
}) => {
  const searchInputRef = useRef(null);
  const [localSearchTerm, setLocalSearchTerm] = useState(filters.search || '');

  // 검색어 디바운싱 - 부모에게만 전달
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      onFilterChange({ search: localSearchTerm });
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [localSearchTerm]);

  // 외부에서 filters.search가 변경되면 로컬 상태도 동기화 (초기화 시에만)
  useEffect(() => {
    // 외부에서 강제로 변경된 경우에만 동기화 (예: 필터 리셋)
    if (filters.search !== localSearchTerm && filters.search === '') {
      setLocalSearchTerm('');
    }
  }, [filters.search]);

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm border">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* 검색 */}
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            ref={searchInputRef}
            type="text"
            placeholder="원자재명, 코드로 검색"
            value={localSearchTerm}
            onChange={(e) => setLocalSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* 카테고리 필터 */}
        <select
          value={filters.category || ''}
          onChange={(e) => onFilterChange({ category: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">모든 카테고리</option>
          {categories.map((category) => (
            <option key={category.key} value={category.key}>
              {category.value}
            </option>
          ))}
        </select>

        {/* 공급업체 필터 */}
        <select
          value={filters.supplier || ''}
          onChange={(e) => onFilterChange({ supplier: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">모든 공급업체</option>
          {suppliers.map((supplier) => (
            <option key={supplier.id} value={supplier.id}>
              {supplier.name}
            </option>
          ))}
        </select>

        {/* 활성 상태 필터 */}
        <select
          value={filters.is_active || ''}
          onChange={(e) => onFilterChange({ is_active: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">모든 상태</option>
          <option value="true">활성</option>
          <option value="false">비활성</option>
        </select>
      </div>

      {/* 새로고침 버튼 */}
      <div className="mt-4 flex justify-end">
        <button
          onClick={onRefresh}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
        >
          새로고침
        </button>
      </div>
    </div>
  );
};

export default MaterialFilter;