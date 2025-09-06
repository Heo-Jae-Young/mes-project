import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { ArrowLeftIcon, PencilIcon, BuildingOfficeIcon } from '@heroicons/react/24/outline';
import Header from '../components/layout/Header';
import LoadingSpinner from '../components/common/LoadingSpinner';
import SupplierForm from '../components/suppliers/SupplierForm';
import supplierService from '../services/supplierService';

const SupplierDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [supplier, setSupplier] = useState(null);
  const [materials, setMaterials] = useState([]);
  const [performance, setPerformance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showEditModal, setShowEditModal] = useState(false);

  useEffect(() => {
    loadSupplierDetail();
  }, [id]);

  const loadSupplierDetail = async () => {
    try {
      setLoading(true);
      const [supplierData, materialsData, performanceData] = await Promise.all([
        supplierService.getSupplier(id),
        supplierService.getSupplierMaterials(id),
        supplierService.getSupplierPerformance(id)
      ]);

      setSupplier(supplierData);
      setMaterials(materialsData);
      setPerformance(performanceData);
    } catch (error) {
      console.error('공급업체 상세 정보 로드 실패:', error);
      toast.error('공급업체 정보를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 상태 배지
  const getStatusBadge = (status) => {
    const statusConfig = {
      'active': 'bg-green-100 text-green-800',
      'inactive': 'bg-gray-100 text-gray-800',
      'suspended': 'bg-red-100 text-red-800'
    };

    const statusLabels = {
      'active': '활성',
      'inactive': '비활성',
      'suspended': '정지'
    };

    return (
      <span className={`px-3 py-1 text-sm font-medium rounded-full ${
        statusConfig[status] || 'bg-gray-100 text-gray-800'
      }`}>
        {statusLabels[status] || status}
      </span>
    );
  };

  // 공급업체 수정 처리
  const handleEditSupplier = async (supplierId, supplierData) => {
    try {
      await supplierService.updateSupplier(supplierId, supplierData);
      toast.success('공급업체가 성공적으로 수정되었습니다.');
      setShowEditModal(false);
      loadSupplierDetail(); // 데이터 새로고침
    } catch (error) {
      console.error('공급업체 수정 실패:', error);
      toast.error('공급업체 수정에 실패했습니다.');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="p-8 text-center">
            <LoadingSpinner size="large" />
            <p className="mt-2 text-gray-500">로딩중...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!supplier) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <BuildingOfficeIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">공급업체를 찾을 수 없습니다.</p>
            <button
              onClick={() => navigate('/suppliers')}
              className="mt-4 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
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
            onClick={() => navigate('/suppliers')}
            className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
          >
            <ArrowLeftIcon className="h-4 w-4 mr-1" />
            공급업체 목록으로 돌아가기
          </button>
        </div>

        {/* 페이지 헤더 */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{supplier.name}</h1>
              <p className="mt-1 text-sm text-gray-500">
                {supplier.code} • {supplier.contact_person}
              </p>
              {supplier.certification && (
                <p className="mt-2 text-gray-600">{supplier.certification}</p>
              )}
            </div>
            <div className="flex items-center space-x-3">
              {getStatusBadge(supplier.status)}
              <button 
                onClick={() => setShowEditModal(true)}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                <PencilIcon className="h-4 w-4 mr-2" />
                편집
              </button>
            </div>
          </div>

          {/* 기본 정보 카드들 */}
          <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <dt className="text-sm font-medium text-gray-500">연락처</dt>
              <dd className="mt-1 text-sm text-gray-900">{supplier.phone}</dd>
              <dd className="text-sm text-gray-600">{supplier.email}</dd>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <dt className="text-sm font-medium text-gray-500">주소</dt>
              <dd className="mt-1 text-sm text-gray-900">{supplier.address}</dd>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <dt className="text-sm font-medium text-gray-500">등록일</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {new Date(supplier.created_at).toLocaleDateString('ko-KR')}
              </dd>
            </div>
          </div>
        </div>

        {/* 성과 요약 */}
        {performance && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">성과 요약 ({performance.analysis_period})</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <dt className="text-sm font-medium text-blue-600">총 로트 수</dt>
                <dd className="mt-1 text-2xl font-bold text-blue-900">{performance.total_lots}</dd>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <dt className="text-sm font-medium text-green-600">품질 합격률</dt>
                <dd className="mt-1 text-2xl font-bold text-green-900">{performance.quality_summary.pass_rate}%</dd>
              </div>
              <div className="bg-yellow-50 p-4 rounded-lg">
                <dt className="text-sm font-medium text-yellow-600">납기 준수율</dt>
                <dd className="mt-1 text-2xl font-bold text-yellow-900">{performance.delivery_performance.delivery_rate}%</dd>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <dt className="text-sm font-medium text-purple-600">공급 원자재</dt>
                <dd className="mt-1 text-2xl font-bold text-purple-900">{materials.length}개</dd>
              </div>
            </div>
          </div>
        )}

        {/* 공급 원자재 목록 */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-900">공급 원자재 목록</h2>
          </div>
          {materials.length === 0 ? (
            <div className="p-8 text-center">
              <p className="text-gray-500">등록된 원자재가 없습니다.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      원자재명
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      코드
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      카테고리
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      단위
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      상태
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {materials.map((material) => (
                    <tr key={material.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium text-gray-900">{material.name}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-500">{material.code}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">{material.category}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">{material.unit}</div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          material.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {material.is_active ? '활성' : '비활성'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* 공급업체 수정 모달 */}
      <SupplierForm
        isOpen={showEditModal}
        onClose={() => setShowEditModal(false)}
        onSubmit={handleEditSupplier}
        supplier={supplier}
      />
    </div>
  );
};

export default SupplierDetailPage;