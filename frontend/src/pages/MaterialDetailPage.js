import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { 
  ArrowLeftIcon, 
  PencilIcon, 
  PlusIcon,
  TrashIcon,
  ExclamationTriangleIcon 
} from '@heroicons/react/24/outline';
import Header from '../components/layout/Header';
import LoadingSpinner from '../components/common/LoadingSpinner';
import MaterialLotForm from '../components/materials/MaterialLotForm';
import MaterialForm from '../components/materials/MaterialForm';
import materialService from '../services/materialService';
import supplierService from '../services/supplierService';

const MaterialDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [material, setMaterial] = useState(null);
  const [inventory, setInventory] = useState(null);
  const [lots, setLots] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showLotForm, setShowLotForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [consumingLot, setConsumingLot] = useState(null);
  const [consumeQuantity, setConsumeQuantity] = useState('');

  useEffect(() => {
    loadMaterialDetail();
  }, [id]);

  const loadMaterialDetail = async () => {
    try {
      setLoading(true);
      const [materialData, inventoryData, lotsData, suppliersData, categoriesData] = await Promise.all([
        materialService.getMaterial(id),
        materialService.getMaterialInventory(id),
        materialService.getMaterialLots(id),
        supplierService.getSuppliers(),
        materialService.getMaterialCategories()
      ]);

      setMaterial(materialData);
      setInventory(inventoryData);
      setLots(lotsData);
      setSuppliers(suppliersData.results || suppliersData);
      setCategories(categoriesData);
    } catch (error) {
      console.error('원자재 상세 정보 로드 실패:', error);
      toast.error('원자재 정보를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 카테고리 표시명 가져오기
  const getCategoryDisplayName = (categoryKey) => {
    const category = categories.find(cat => cat.key === categoryKey);
    return category ? category.value : categoryKey;
  };

  // 공급업체명 가져오기
  const getSupplierName = (material) => {
    if (material.supplier && typeof material.supplier === 'object') {
      return material.supplier.name;
    }
    const supplier = suppliers.find(sup => sup.id === material.supplier);
    return supplier ? supplier.name : '알 수 없음';
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

  // 로트 상태 배지
  const getLotStatusBadge = (status) => {
    const statusColors = {
      'received': 'bg-blue-100 text-blue-800',
      'in_storage': 'bg-green-100 text-green-800',
      'in_use': 'bg-yellow-100 text-yellow-800',
      'used': 'bg-gray-100 text-gray-800',
      'expired': 'bg-red-100 text-red-800'
    };
    
    const statusLabels = {
      'received': '입고됨',
      'in_storage': '보관중',
      'in_use': '사용중',
      'used': '소진됨',
      'expired': '만료됨'
    };

    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusColors[status] || 'bg-gray-100 text-gray-800'}`}>
        {statusLabels[status] || status}
      </span>
    );
  };

  // 유통기한 체크
  const getDaysUntilExpiry = (expiryDate) => {
    if (!expiryDate) return null;
    const today = new Date();
    const expiry = new Date(expiryDate);
    const diffTime = expiry - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  // 입고 처리 핸들러
  const handleCreateLot = async (lotData) => {
    try {
      await materialService.createMaterialLot(lotData);
      toast.success('입고 처리가 완료되었습니다.');
      setShowLotForm(false);
      // 데이터 새로고침
      loadMaterialDetail();
    } catch (error) {
      console.error('입고 처리 실패:', error);
      if (error.response?.data) {
        const errorMessages = Object.values(error.response.data).flat();
        toast.error(`입고 처리 실패: ${errorMessages.join(', ')}`);
      } else {
        toast.error('입고 처리에 실패했습니다.');
      }
    }
  };

  // 로트 소비 처리 핸들러
  const handleConsumeLot = async () => {
    if (!consumingLot || !consumeQuantity) return;

    const quantity = parseFloat(consumeQuantity);
    if (quantity <= 0) {
      toast.error('소비 수량은 0보다 커야 합니다.');
      return;
    }

    if (quantity > consumingLot.quantity_current) {
      toast.error('소비 수량이 현재 수량을 초과합니다.');
      return;
    }

    try {
      await materialService.consumeMaterialLot(consumingLot.id, { quantity });
      toast.success(`${quantity} ${material.unit} 소비 처리되었습니다.`);
      setConsumingLot(null);
      setConsumeQuantity('');
      // 데이터 새로고침
      loadMaterialDetail();
    } catch (error) {
      console.error('로트 소비 실패:', error);
      if (error.response?.data?.detail) {
        toast.error(error.response.data.detail);
      } else {
        toast.error('로트 소비 처리에 실패했습니다.');
      }
    }
  };

  // 원자재 수정 핸들러
  const handleUpdateMaterial = async (materialId, materialData) => {
    try {
      await materialService.updateMaterial(materialId, materialData);
      toast.success('원자재 정보가 수정되었습니다.');
      setShowEditForm(false);
      // 데이터 새로고침
      loadMaterialDetail();
    } catch (error) {
      console.error('원자재 수정 실패:', error);
      console.error('에러 응답:', error.response?.data);
      console.error('에러 상태:', error.response?.status);
      
      if (error.response?.data) {
        const errorMessages = Object.values(error.response.data).flat();
        toast.error(`수정 실패: ${errorMessages.join(', ')}`);
      } else {
        toast.error('원자재 수정에 실패했습니다.');
      }
    }
  };

  // 로트 삭제 핸들러
  const handleDeleteLot = async (lot) => {
    if (!window.confirm(`정말로 로트 ${lot.lot_number}를 삭제하시겠습니까?\n삭제된 데이터는 복구할 수 없습니다.`)) {
      return;
    }

    try {
      await materialService.deleteMaterialLot(lot.id);
      toast.success('로트가 삭제되었습니다.');
      // 데이터 새로고침
      loadMaterialDetail();
    } catch (error) {
      console.error('로트 삭제 실패:', error);
      if (error.response?.data?.detail) {
        toast.error(error.response.data.detail);
      } else {
        toast.error('로트 삭제에 실패했습니다.');
      }
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-gray-500">로딩중...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!material) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <p className="text-gray-500">원자재를 찾을 수 없습니다.</p>
            <button
              onClick={() => navigate('/materials')}
              className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              목록으로 돌아가기
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 상단 네비게이션 */}
        <div className="mb-6">
          <button
            onClick={() => navigate('/materials')}
            className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
          >
            <ArrowLeftIcon className="h-4 w-4 mr-1" />
            원자재 목록으로 돌아가기
          </button>
        </div>

        {/* 페이지 헤더 */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{material.name}</h1>
              <p className="mt-1 text-sm text-gray-500">
                {material.code} • {getCategoryDisplayName(material.category)} • {getSupplierName(material)}
              </p>
              {material.description && (
                <p className="mt-2 text-gray-600">{material.description}</p>
              )}
            </div>
            <div className="flex space-x-3">
              <button 
                onClick={() => setShowEditForm(true)}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                <PencilIcon className="h-4 w-4 mr-2" />
                편집
              </button>
              <button 
                onClick={() => setShowLotForm(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                입고 처리
              </button>
            </div>
          </div>

          {/* 기본 정보 카드들 */}
          <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <dt className="text-sm font-medium text-gray-500">단위</dt>
              <dd className="mt-1 text-lg font-semibold text-gray-900">{material.unit}</dd>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <dt className="text-sm font-medium text-gray-500">보관 온도</dt>
              <dd className="mt-1 text-lg font-semibold text-gray-900">{getStorageTemp(material)}</dd>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <dt className="text-sm font-medium text-gray-500">유통기한</dt>
              <dd className="mt-1 text-lg font-semibold text-gray-900">
                {material.shelf_life_days ? `${material.shelf_life_days}일` : '무제한'}
              </dd>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <dt className="text-sm font-medium text-gray-500">상태</dt>
              <dd className="mt-1">
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  material.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {material.is_active ? '활성' : '비활성'}
                </span>
              </dd>
            </div>
          </div>
        </div>

        {/* 재고 요약 */}
        {inventory && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">재고 현황</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <dt className="text-sm font-medium text-blue-600">총 재고</dt>
                <dd className="mt-1 text-2xl font-bold text-blue-900">
                  {inventory.total_quantity} {inventory.unit}
                </dd>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <dt className="text-sm font-medium text-green-600">활성 로트</dt>
                <dd className="mt-1 text-2xl font-bold text-green-900">{inventory.active_lots}</dd>
              </div>
              <div className="bg-yellow-50 p-4 rounded-lg">
                <dt className="text-sm font-medium text-yellow-600">유통기한 임박</dt>
                <dd className="mt-1 text-2xl font-bold text-yellow-900">{inventory.near_expiry_lots}</dd>
              </div>
              <div className="bg-red-50 p-4 rounded-lg">
                <dt className="text-sm font-medium text-red-600">만료</dt>
                <dd className="mt-1 text-2xl font-bold text-red-900">{inventory.expired_lots}</dd>
              </div>
            </div>
          </div>
        )}

        {/* 로트 목록 */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-900">로트 목록</h2>
          </div>
          {lots.length === 0 ? (
            <div className="p-8 text-center">
              <p className="text-gray-500">등록된 로트가 없습니다.</p>
              <button 
                onClick={() => setShowLotForm(true)}
                className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
              >
                첫 번째 입고 처리하기
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      로트 번호
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      입고일/유통기한
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      수량
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      상태
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      품질검사
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      작업
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {lots.map((lot) => (
                    <tr key={lot.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium text-gray-900">{lot.lot_number}</div>
                        <div className="text-sm text-gray-500">#{lot.id.slice(0, 8)}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">
                          입고: {new Date(lot.received_date).toLocaleDateString()}
                        </div>
                        {lot.expiry_date && (
                          <div className="text-sm text-gray-500 flex items-center">
                            유통: {new Date(lot.expiry_date).toLocaleDateString()}
                            {getDaysUntilExpiry(lot.expiry_date) <= 30 && (
                              <ExclamationTriangleIcon className="h-4 w-4 text-yellow-500 ml-1" />
                            )}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">
                          {lot.quantity_current} / {lot.quantity_received} {material.unit}
                        </div>
                        <div className="text-sm text-gray-500">
                          사용률: {((lot.quantity_received - lot.quantity_current) / lot.quantity_received * 100).toFixed(1)}%
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        {getLotStatusBadge(lot.status)}
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          lot.quality_test_passed === true ? 'bg-green-100 text-green-800' :
                          lot.quality_test_passed === false ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {lot.quality_test_passed === true ? '합격' :
                           lot.quality_test_passed === false ? '불합격' : '미검사'}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex space-x-2">
                          {lot.quantity_current > 0 && lot.status !== 'used' && (
                            <button 
                              onClick={(e) => {
                                e.stopPropagation();
                                setConsumingLot(lot);
                                setConsumeQuantity('');
                              }}
                              className="text-blue-600 hover:text-blue-900 text-sm font-medium"
                            >
                              소비
                            </button>
                          )}
                          {(lot.status === 'received' || lot.status === 'in_storage') && lot.quantity_current === lot.quantity_received && (
                            <button 
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDeleteLot(lot);
                              }}
                              className="text-red-600 hover:text-red-900 text-sm font-medium"
                              title="로트 삭제"
                            >
                              <TrashIcon className="h-4 w-4" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* 입고 처리 모달 */}
        <MaterialLotForm
          isOpen={showLotForm}
          onClose={() => setShowLotForm(false)}
          onSubmit={handleCreateLot}
          material={material}
          suppliers={suppliers}
        />

        {/* 원자재 편집 모달 */}
        <MaterialForm
          isOpen={showEditForm}
          onClose={() => setShowEditForm(false)}
          onSubmit={handleUpdateMaterial}
          material={material}
          suppliers={suppliers}
          categories={categories}
        />

        {/* 로트 소비 모달 */}
        {consumingLot && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
              <div className="mt-3">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  로트 소비 처리
                </h3>
                
                <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-600">
                    <div><span className="font-medium">로트:</span> {consumingLot.lot_number}</div>
                    <div><span className="font-medium">현재 수량:</span> {consumingLot.quantity_current} {material.unit}</div>
                  </div>
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    소비 수량 ({material.unit})
                  </label>
                  <input
                    type="number"
                    step="0.001"
                    min="0.001"
                    max={consumingLot.quantity_current}
                    value={consumeQuantity}
                    onChange={(e) => setConsumeQuantity(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="소비할 수량을 입력하세요"
                    autoFocus
                  />
                </div>

                <div className="flex justify-end space-x-3">
                  <button
                    onClick={() => {
                      setConsumingLot(null);
                      setConsumeQuantity('');
                    }}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                  >
                    취소
                  </button>
                  <button
                    onClick={handleConsumeLot}
                    disabled={!consumeQuantity || parseFloat(consumeQuantity) <= 0}
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    소비 처리
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MaterialDetailPage;