import React, { useState } from 'react';
import { 
  PencilIcon, 
  TrashIcon, 
  CheckCircleIcon,
  XCircleIcon,
  ClipboardDocumentListIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
  CurrencyDollarIcon,
  QuestionMarkCircleIcon
} from '@heroicons/react/24/outline';
import { formatDistanceToNow } from 'date-fns';
import { ko } from 'date-fns/locale';
import ProductCostDetail from './ProductCostDetail';
import CostCalculationGuide from './CostCalculationGuide';

const ProductList = ({ products, onEdit, onDelete, onManageBOM }) => {
  const [selectedProductForCost, setSelectedProductForCost] = useState(null);
  const [showCostDetail, setShowCostDetail] = useState(false);
  const [showCostGuide, setShowCostGuide] = useState(false);
  
  // 상태 배지 컴포넌트
  const StatusBadge = ({ isActive }) => {
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
        isActive 
          ? 'bg-green-100 text-green-800' 
          : 'bg-red-100 text-red-800'
      }`}>
        {isActive ? (
          <>
            <CheckCircleIcon className="w-4 h-4 mr-1" />
            활성
          </>
        ) : (
          <>
            <XCircleIcon className="w-4 h-4 mr-1" />
            비활성
          </>
        )}
      </span>
    );
  };

  // BOM 상태 인디케이터 컴포넌트 (작은 아이콘)
  const BOMStatusIndicator = ({ hasBOM }) => {
    return (
      <span 
        className={`inline-flex items-center justify-center w-5 h-5 rounded-full ml-2 ${
          hasBOM 
            ? 'bg-blue-100 text-blue-600' 
            : 'bg-orange-100 text-orange-600'
        }`}
        title={hasBOM ? 'BOM 설정됨' : 'BOM 미설정'}
      >
        {hasBOM ? (
          <DocumentTextIcon className="w-3 h-3" />
        ) : (
          <ExclamationTriangleIcon className="w-3 h-3" />
        )}
      </span>
    );
  };

  // 온도 범위 포맷팅
  const formatTemperatureRange = (min, max) => {
    if (!min && !max) return '-';
    if (min && max) return `${min}°C ~ ${max}°C`;
    if (min) return `${min}°C 이상`;
    if (max) return `${max}°C 이하`;
  };

  // 무게 포맷팅
  const formatWeight = (weight) => {
    if (!weight) return '-';
    return `${parseFloat(weight).toLocaleString()}g`;
  };

  // 영양성분 요약
  const formatNutritionSummary = (nutritionFacts) => {
    if (!nutritionFacts) return '-';
    
    const facts = typeof nutritionFacts === 'string' 
      ? JSON.parse(nutritionFacts) 
      : nutritionFacts;
    
    const calories = facts.calories || facts['칼로리'];
    return calories ? `${calories}kcal` : '정보 있음';
  };

  // 원가 포맷팅 및 클릭 핸들러
  const formatCost = (cost, status, product) => {
    if (!cost || cost === '0' || cost === 0) {
      return <span className="text-gray-400">-</span>;
    }
    
    const costValue = parseFloat(cost);
    const formattedCost = `₩${costValue.toLocaleString()}`;
    
    // 계산 방법에 따른 스타일링 (CostCalculationGuide와 일치)
    let textColor = 'text-gray-900';
    let bgColor = '';
    
    if (status?.bom_missing) {
      textColor = 'text-gray-400';
      bgColor = 'bg-gray-50';
    } else if (status?.calculation_method === 'current_lot') {
      textColor = 'text-green-600';
      bgColor = 'bg-green-50';
    } else if (status?.calculation_method === 'recent_average') {
      textColor = 'text-blue-600';
      bgColor = 'bg-blue-50';
    } else if (status?.calculation_method === 'historical_average') {
      textColor = 'text-orange-600';
      bgColor = 'bg-orange-50';
    } else if (status?.calculation_method === 'no_data') {
      textColor = 'text-gray-600';
      bgColor = 'bg-gray-50';
    } else if (status?.calculation_method === 'estimated' || status?.has_warnings) {
      textColor = 'text-orange-600';
      bgColor = 'bg-orange-50';
    }
    
    return (
      <button
        onClick={() => {
          setSelectedProductForCost(product);
          setShowCostDetail(true);
        }}
        className={`${textColor} ${bgColor} px-2 py-1 rounded text-sm hover:opacity-80 transition-opacity flex items-center`}
        title="원가 상세 정보 보기"
      >
        <CurrencyDollarIcon className="w-3 h-3 mr-1" />
        {formattedCost}
      </button>
    );
  };

  // 원가 상세 모달 닫기
  const handleCostDetailClose = () => {
    setShowCostDetail(false);
    setSelectedProductForCost(null);
  };

  if (!products || products.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-8 text-center">
        <div className="text-gray-500 text-lg mb-2">등록된 제품이 없습니다</div>
        <div className="text-gray-400">새 제품을 등록해보세요.</div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="sticky left-0 z-10 bg-gray-50 px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-r border-gray-200">
                제품 정보
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap min-w-20">
                상태
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap min-w-32">
                <div className="flex items-center">
                  예상원가
                  <button
                    onClick={() => setShowCostGuide(true)}
                    className="ml-2 text-gray-400 hover:text-gray-600 transition-colors"
                    title="원가 계산 방법 보기"
                  >
                    <QuestionMarkCircleIcon className="h-4 w-4" />
                  </button>
                </div>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap min-w-20">
                중량
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap min-w-24">
                유통기한
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap min-w-16">
                버전
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap min-w-24">
                포장형태
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap min-w-24">
                보관온도
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap min-w-20">
                영양정보
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap min-w-20">
                생성일
              </th>
              <th className="sticky right-0 z-10 bg-gray-50 px-8 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider border-l border-gray-200 min-w-40">
                작업
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {products.map((product) => (
              <tr key={product.id} className="hover:bg-gray-50 transition-colors">
                <td className="sticky left-0 z-10 bg-white px-6 py-4 whitespace-nowrap border-r border-gray-200">
                  <div>
                    <div className="flex items-center">
                      <span className="text-sm font-medium text-gray-900">
                        {product.name}
                      </span>
                      <BOMStatusIndicator hasBOM={product.has_bom} />
                    </div>
                    <div className="text-sm text-gray-500">
                      {product.code}
                    </div>
                    {product.description && (
                      <div className="text-xs text-gray-400 mt-1 max-w-xs truncate">
                        {product.description}
                      </div>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <StatusBadge isActive={product.is_active} />
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  {formatCost(product.estimated_unit_cost, product.cost_calculation_status, product)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatWeight(product.net_weight)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {product.shelf_life_days}일
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  v{product.version}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {product.packaging_type}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatTemperatureRange(product.storage_temp_min, product.storage_temp_max)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatNutritionSummary(product.nutrition_facts)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {formatDistanceToNow(new Date(product.created_at), { 
                    addSuffix: true, 
                    locale: ko 
                  })}
                </td>
                <td className="sticky right-0 z-10 bg-white px-8 py-4 whitespace-nowrap text-right text-sm font-medium border-l border-gray-200 min-w-40">
                  <div className="flex items-center justify-end space-x-2">
                    <button
                      onClick={() => onManageBOM(product)}
                      className="text-green-600 hover:text-green-900 p-1 rounded-full hover:bg-green-50 transition-colors"
                      title="BOM 관리"
                    >
                      <ClipboardDocumentListIcon className="h-4 w-4" />
                    </button>
                    
                    <button
                      onClick={() => onEdit(product)}
                      className="text-blue-600 hover:text-blue-900 p-1 rounded-full hover:bg-blue-50 transition-colors"
                      title="수정"
                    >
                      <PencilIcon className="h-4 w-4" />
                    </button>
                    
                    <button
                      onClick={() => onDelete(product.id)}
                      className="text-red-600 hover:text-red-900 p-1 rounded-full hover:bg-red-50 transition-colors"
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

      {/* 제품별 알러지 정보가 있는 경우 하단에 표시 */}
      {products.some(product => product.allergen_info) && (
        <div className="bg-yellow-50 border-t border-yellow-200 px-6 py-3">
          <div className="text-xs text-yellow-800">
            <strong>알러지 정보:</strong> 일부 제품에 알러지 유발 성분이 포함되어 있습니다. 
            자세한 내용은 각 제품의 상세 정보를 확인해주세요.
          </div>
        </div>
      )}

      {/* 원가 상세 모달 */}
      {showCostDetail && selectedProductForCost && (
        <ProductCostDetail
          product={selectedProductForCost}
          onClose={handleCostDetailClose}
        />
      )}

      {/* 원가 계산 방법 안내 모달 */}
      {showCostGuide && (
        <CostCalculationGuide
          onClose={() => setShowCostGuide(false)}
        />
      )}
    </div>
  );
};

export default ProductList;