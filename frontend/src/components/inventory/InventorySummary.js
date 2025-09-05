import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  CubeIcon,
  DocumentTextIcon,
  ShieldCheckIcon,
  TruckIcon
} from '@heroicons/react/24/outline';
import materialService from '../../services/materialService';
import { toast } from 'react-hot-toast';

const InventorySummary = () => {
  const [summaryData, setSummaryData] = useState({
    totalMaterials: 0,
    activeLots: 0,
    totalInventoryValue: 0,
    suppliersCount: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadInventorySummary();
  }, []);

  const loadInventorySummary = async () => {
    try {
      setLoading(true);
      
      // 여러 데이터를 병렬로 가져오기
      const [materialsData, lotsData] = await Promise.all([
        materialService.getMaterials({ is_active: true }),
        materialService.getAllMaterialLots() // 모든 로트를 가져와서 프론트엔드에서 필터링
      ]);

      // 고유한 공급업체 수 계산
      const uniqueSuppliers = new Set();
      materialsData.results?.forEach(material => {
        if (material.supplier) {
          if (typeof material.supplier === 'object') {
            uniqueSuppliers.add(material.supplier.id);
          } else {
            uniqueSuppliers.add(material.supplier);
          }
        }
      });

      // 활성 로트만 필터링 (received, in_storage, in_use 상태이고 수량이 있는 것)
      const activeLots = lotsData.results?.filter(lot => 
        ['received', 'in_storage', 'in_use'].includes(lot.status) && lot.quantity_current > 0
      ) || [];

      // 총 재고 가치 계산 (단가가 있는 로트만)
      let totalValue = 0;
      activeLots.forEach(lot => {
        if (lot.unit_price && lot.quantity_current > 0) {
          totalValue += lot.unit_price * lot.quantity_current;
        }
      });

      setSummaryData({
        totalMaterials: materialsData.results?.length || 0,
        activeLots: activeLots.length,
        totalInventoryValue: totalValue,
        suppliersCount: uniqueSuppliers.size
      });

    } catch (error) {
      console.error('재고 요약 데이터 로드 실패:', error);
      toast.error('재고 요약 정보를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW',
      minimumFractionDigits: 0,
    }).format(value);
  };

  const summaryCards = [
    {
      title: '활성 원자재',
      value: loading ? '...' : `${summaryData.totalMaterials} 종`,
      icon: CubeIcon,
      color: 'bg-blue-500',
      link: '/materials'
    },
    {
      title: '보유 로트',
      value: loading ? '...' : `${summaryData.activeLots} 건`,
      icon: DocumentTextIcon,
      color: 'bg-green-500',
      link: '/materials'
    },
    {
      title: '총 재고 가치',
      value: loading ? '...' : formatCurrency(summaryData.totalInventoryValue),
      icon: ShieldCheckIcon,
      color: 'bg-purple-500',
      link: '/materials'
    },
    {
      title: '등록 공급업체',
      value: loading ? '...' : `${summaryData.suppliersCount} 곳`,
      icon: TruckIcon,
      color: 'bg-indigo-500',
      link: '/materials'
    }
  ];

  return (
    <div className="mb-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-gray-900">재고 현황</h2>
        <Link 
          to="/materials" 
          className="text-sm text-blue-600 hover:text-blue-500 font-medium"
        >
          전체 보기 →
        </Link>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {summaryCards.map((card, index) => {
          const IconComponent = card.icon;
          
          return (
            <div key={index} className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className={`w-8 h-8 ${card.color} rounded-full flex items-center justify-center`}>
                      <IconComponent className="w-5 h-5 text-white" />
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        {card.title}
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {card.value}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
              {card.link && (
                <div className="bg-gray-50 px-5 py-3">
                  <div className="text-sm">
                    <Link 
                      to={card.link}
                      className="font-medium text-gray-600 hover:text-gray-500"
                    >
                      상세 보기
                    </Link>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default InventorySummary;