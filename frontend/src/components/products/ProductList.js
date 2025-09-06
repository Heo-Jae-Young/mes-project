import { 
  PencilIcon, 
  TrashIcon, 
  CheckCircleIcon,
  XCircleIcon,
  ClipboardDocumentListIcon
} from '@heroicons/react/24/outline';
import { formatDistanceToNow } from 'date-fns';
import { ko } from 'date-fns/locale';

const ProductList = ({ products, onEdit, onDelete, onManageBOM }) => {
  
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
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                제품 정보
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                버전
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                중량
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                포장형태
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                유통기한
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                보관온도
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                영양정보
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                상태
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                생성일
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                작업
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {products.map((product) => (
              <tr key={product.id} className="hover:bg-gray-50 transition-colors">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      {product.name}
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
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  v{product.version}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatWeight(product.net_weight)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {product.packaging_type}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {product.shelf_life_days}일
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatTemperatureRange(product.storage_temp_min, product.storage_temp_max)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatNutritionSummary(product.nutrition_facts)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <StatusBadge isActive={product.is_active} />
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {formatDistanceToNow(new Date(product.created_at), { 
                    addSuffix: true, 
                    locale: ko 
                  })}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
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
    </div>
  );
};

export default ProductList;