import React, { useState, useEffect } from 'react';
import { 
  XMarkIcon, 
  ExclamationTriangleIcon,
  InformationCircleIcon,
  CheckCircleIcon,
  CurrencyDollarIcon
} from '@heroicons/react/24/outline';
import productService from '../../services/productService';

const ProductCostDetail = ({ product, onClose }) => {
  const [costDetail, setCostDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCostDetail = async () => {
      if (!product?.id) return;
      
      try {
        setLoading(true);
        const data = await productService.getProductCost(product.id, 1);
        setCostDetail(data);
      } catch (err) {
        setError(err.message || '원가 정보를 가져올 수 없습니다.');
      } finally {
        setLoading(false);
      }
    };

    fetchCostDetail();
  }, [product?.id]);

  const formatCost = (value) => {
    if (!value || value === '0') return '₩0';
    return `₩${parseFloat(value).toLocaleString()}`;
  };

  // 계산 방법별 색상 정보
  const getMethodInfo = (method) => {
    const methodInfo = {
      'current_lot': { 
        label: '현재 재고', 
        color: 'bg-green-50 text-green-600',
        textColor: 'text-green-600',
        icon: CheckCircleIcon
      },
      'recent_average': { 
        label: '최근 평균', 
        color: 'bg-blue-50 text-blue-600',
        textColor: 'text-blue-600',
        icon: InformationCircleIcon
      },
      'historical_average': { 
        label: '전체 평균', 
        color: 'bg-orange-50 text-orange-600',
        textColor: 'text-orange-600',
        icon: InformationCircleIcon
      },
      'no_data': { 
        label: '데이터 없음', 
        color: 'bg-gray-50 text-gray-600',
        textColor: 'text-gray-600',
        icon: ExclamationTriangleIcon
      },
      'estimated': { 
        label: '추정', 
        color: 'bg-orange-50 text-orange-600',
        textColor: 'text-orange-600',
        icon: ExclamationTriangleIcon
      }
    };
    return methodInfo[method] || methodInfo['no_data'];
  };

  const getMethodBadge = (method) => {
    const info = getMethodInfo(method);
    const IconComponent = info.icon;

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${info.color}`}>
        <IconComponent className="w-3 h-3 mr-1" />
        {info.label}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
        <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
        <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
          <div className="flex justify-between items-center pb-3 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">원가 상세 정보</h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>
          
          <div className="mt-4 text-center text-red-600">
            <ExclamationTriangleIcon className="w-16 h-16 mx-auto mb-4" />
            <p>{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-6xl shadow-lg rounded-md bg-white">
        {/* 헤더 */}
        <div className="flex justify-between items-center pb-3 border-b border-gray-200">
          <div className="flex items-center">
            <CurrencyDollarIcon className="h-6 w-6 text-blue-600 mr-2" />
            <div>
              <h3 className="text-lg font-medium text-gray-900">
                제품 원가 상세 정보
              </h3>
              <p className="text-sm text-gray-500">
                {product.name} ({product.code})
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        {costDetail && (
          <div className="mt-6">
            {/* 요약 정보 */}
            <div className="bg-gray-50 rounded-lg p-4 mb-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className={`text-2xl font-bold ${
                    costDetail.calculation_method ? 
                    getMethodInfo(costDetail.calculation_method).textColor : 'text-blue-600'
                  }`}>
                    {formatCost(costDetail.unit_cost)}
                  </div>
                  <div className="text-sm text-gray-600">단위 원가</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold text-gray-900">
                    {costDetail.production_quantity}개
                  </div>
                  <div className="text-sm text-gray-600">생산 수량</div>
                </div>
                <div className="text-center">
                  <div className={`text-lg font-semibold ${
                    costDetail.calculation_method ? 
                    getMethodInfo(costDetail.calculation_method).textColor : 'text-gray-900'
                  }`}>
                    {formatCost(costDetail.total_cost)}
                  </div>
                  <div className="text-sm text-gray-600">총 원가</div>
                </div>
              </div>
              
              {costDetail.calculation_method && (
                <div className="mt-4 flex justify-center">
                  {getMethodBadge(costDetail.calculation_method)}
                </div>
              )}
            </div>

            {/* BOM 누락 경고 */}
            {costDetail.bom_missing && (
              <div className="bg-orange-50 border-l-4 border-orange-400 p-4 mb-6">
                <div className="flex">
                  <ExclamationTriangleIcon className="h-5 w-5 text-orange-400" />
                  <div className="ml-3">
                    <p className="text-sm text-orange-700">
                      이 제품에 BOM(자재명세서)이 설정되지 않아 원가를 계산할 수 없습니다.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* 경고 메시지 */}
            {costDetail.warnings && costDetail.warnings.length > 0 && (
              <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
                <div className="flex">
                  <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" />
                  <div className="ml-3">
                    <h4 className="text-sm font-medium text-yellow-700">주의사항</h4>
                    <ul className="mt-1 text-sm text-yellow-700 list-disc list-inside">
                      {costDetail.warnings.map((warning, index) => (
                        <li key={index}>{warning}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {/* 원자재별 원가 상세 */}
            {costDetail.material_costs && costDetail.material_costs.length > 0 && (
              <div>
                <h4 className="text-lg font-medium text-gray-900 mb-4">
                  원자재별 원가 내역
                </h4>
                
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          원자재
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          필요량
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          단가
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          총 비용
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          가격 산출 방식
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {costDetail.material_costs.map((material, index) => (
                        <tr key={index} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div>
                              <div className="text-sm font-medium text-gray-900">
                                {material.material.name}
                              </div>
                              <div className="text-sm text-gray-500">
                                {material.material.code} | {material.material.category}
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {parseFloat(material.required_quantity).toLocaleString()} {material.material.unit}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatCost(material.unit_price)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {formatCost(material.total_cost)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {getMethodBadge(material.price_method)}
                            {material.lot_info && (
                              <div className="mt-1 text-xs text-gray-500">
                                재고: {material.lot_info.available_lots}개 로트, 
                                {parseFloat(material.lot_info.total_available_quantity).toLocaleString()} {material.material.unit}
                              </div>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* 닫기 버튼 */}
        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className="bg-gray-100 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-200 transition-colors"
          >
            닫기
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductCostDetail;