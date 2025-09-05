import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  ExclamationTriangleIcon, 
  ClockIcon, 
  ChartBarIcon 
} from '@heroicons/react/24/outline';
import materialService from '../../services/materialService';
import { toast } from 'react-hot-toast';

const InventoryAlerts = () => {
  const [lowStockMaterials, setLowStockMaterials] = useState([]);
  const [expiringLots, setExpiringLots] = useState([]);
  const [qualitySummary, setQualitySummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadInventoryAlerts();
  }, []);

  const loadInventoryAlerts = async () => {
    try {
      setLoading(true);
      const [lowStockData, expiringData, qualityData] = await Promise.all([
        materialService.getLowStockMaterials(10), // 10개 이하
        materialService.getExpiringLots(7), // 7일 이내
        materialService.getQualitySummary()
      ]);

      setLowStockMaterials(lowStockData);
      setExpiringLots(expiringData.expiring_lots || []);
      setQualitySummary(qualityData);
    } catch (error) {
      console.error('재고 알림 데이터 로드 실패:', error);
      toast.error('재고 알림 정보를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const getStockLevelColor = (currentStock) => {
    if (currentStock <= 0) return 'text-red-600 bg-red-100';
    if (currentStock <= 5) return 'text-orange-600 bg-orange-100';
    return 'text-yellow-600 bg-yellow-100';
  };

  const getDaysUntilExpiry = (expiryDate) => {
    const today = new Date();
    const expiry = new Date(expiryDate);
    const diffTime = expiry - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const getExpiryColor = (expiryDate) => {
    const days = getDaysUntilExpiry(expiryDate);
    if (days <= 1) return 'text-red-600 bg-red-100';
    if (days <= 3) return 'text-orange-600 bg-orange-100';
    return 'text-yellow-600 bg-yellow-100';
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-white rounded-lg shadow p-6">
            <div className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
              <div className="h-8 bg-gray-200 rounded w-1/4"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* 재고 부족 알림 */}
      <div className="bg-white overflow-hidden shadow rounded-lg">
        <div className="p-5">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ExclamationTriangleIcon className="h-8 w-8 text-red-500" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  재고 부족 원자재
                </dt>
                <dd className="text-lg font-medium text-gray-900">
                  {lowStockMaterials.length} 종
                </dd>
              </dl>
            </div>
          </div>
          {lowStockMaterials.length > 0 && (
            <div className="mt-4">
              <div className="max-h-32 overflow-y-auto">
                {lowStockMaterials.slice(0, 3).map((material) => (
                  <div key={material.id} className="flex justify-between items-center py-1 text-sm">
                    <Link 
                      to={`/materials/${material.id}`}
                      className="text-blue-600 hover:text-blue-800 truncate"
                    >
                      {material.name}
                    </Link>
                    <span className={`px-2 py-1 text-xs rounded-full ${getStockLevelColor(material.current_stock)}`}>
                      {material.current_stock} {material.unit}
                    </span>
                  </div>
                ))}
              </div>
              {lowStockMaterials.length > 3 && (
                <p className="text-xs text-gray-500 mt-2">
                  외 {lowStockMaterials.length - 3}건 더
                </p>
              )}
            </div>
          )}
        </div>
        <div className="bg-gray-50 px-5 py-3">
          <div className="text-sm">
            <Link to="/materials" className="font-medium text-red-600 hover:text-red-500">
              재고 관리 →
            </Link>
          </div>
        </div>
      </div>

      {/* 유통기한 임박 알림 */}
      <div className="bg-white overflow-hidden shadow rounded-lg">
        <div className="p-5">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ClockIcon className="h-8 w-8 text-orange-500" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  유통기한 임박 로트
                </dt>
                <dd className="text-lg font-medium text-gray-900">
                  {expiringLots.length} 건
                </dd>
              </dl>
            </div>
          </div>
          {expiringLots.length > 0 && (
            <div className="mt-4">
              <div className="max-h-32 overflow-y-auto">
                {expiringLots.slice(0, 3).map((lot) => (
                  <div key={lot.id} className="flex justify-between items-center py-1 text-sm">
                    <Link 
                      to={`/materials/${lot.raw_material.id}`}
                      className="text-blue-600 hover:text-blue-800 truncate"
                    >
                      {lot.raw_material.name} ({lot.lot_number})
                    </Link>
                    <span className={`px-2 py-1 text-xs rounded-full ${getExpiryColor(lot.expiry_date)}`}>
                      {getDaysUntilExpiry(lot.expiry_date)}일
                    </span>
                  </div>
                ))}
              </div>
              {expiringLots.length > 3 && (
                <p className="text-xs text-gray-500 mt-2">
                  외 {expiringLots.length - 3}건 더
                </p>
              )}
            </div>
          )}
        </div>
        <div className="bg-gray-50 px-5 py-3">
          <div className="text-sm">
            <Link to="/materials" className="font-medium text-orange-600 hover:text-orange-500">
              유통기한 관리 →
            </Link>
          </div>
        </div>
      </div>

      {/* 품질관리 요약 */}
      <div className="bg-white overflow-hidden shadow rounded-lg">
        <div className="p-5">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ChartBarIcon className="h-8 w-8 text-blue-500" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  품질 합격률 (30일)
                </dt>
                <dd className="text-lg font-medium text-gray-900">
                  {qualitySummary ? `${qualitySummary.quality_results.pass_rate}%` : '-'}
                </dd>
              </dl>
            </div>
          </div>
          {qualitySummary && (
            <div className="mt-4">
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div className="text-center">
                  <div className="text-green-600 font-medium">
                    {qualitySummary.quality_results.passed}
                  </div>
                  <div className="text-gray-500">합격</div>
                </div>
                <div className="text-center">
                  <div className="text-red-600 font-medium">
                    {qualitySummary.quality_results.failed}
                  </div>
                  <div className="text-gray-500">불합격</div>
                </div>
                <div className="text-center">
                  <div className="text-gray-600 font-medium">
                    {qualitySummary.quality_results.pending}
                  </div>
                  <div className="text-gray-500">미검사</div>
                </div>
              </div>
            </div>
          )}
        </div>
        <div className="bg-gray-50 px-5 py-3">
          <div className="text-sm">
            <Link to="/materials" className="font-medium text-blue-600 hover:text-blue-500">
              품질관리 →
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InventoryAlerts;