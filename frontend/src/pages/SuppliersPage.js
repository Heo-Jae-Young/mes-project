import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import Header from '../components/layout/Header';
import SupplierForm from '../components/suppliers/SupplierForm';
import SupplierList from '../components/suppliers/SupplierList';
import LoadingCard from '../components/common/LoadingCard';
import supplierService from '../services/supplierService';

const SuppliersPage = () => {
  const navigate = useNavigate();
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingSupplier, setEditingSupplier] = useState(null);
  const [filters, setFilters] = useState({
    search: '',
    status: ''
  });

  // 공급업체 목록 조회
  const fetchSuppliers = async () => {
    try {
      setLoading(true);
      const data = await supplierService.getSuppliers(filters);
      const suppliersList = data.results || data;
      setSuppliers(suppliersList);
    } catch (error) {
      toast.error('공급업체 목록을 불러오는데 실패했습니다');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSuppliers();
  }, [filters]);

  const handleCreateSupplier = async (supplierData) => {
    try {
      await supplierService.createSupplier(supplierData);
      toast.success('공급업체가 등록되었습니다.');
      setShowForm(false);
      fetchSuppliers();
    } catch (error) {
      console.error('공급업체 생성 실패:', error);
      if (error.response?.data) {
        const errorMessages = Object.values(error.response.data).flat();
        toast.error(`등록 실패: ${errorMessages.join(', ')}`);
      } else {
        toast.error('공급업체 등록에 실패했습니다.');
      }
    }
  };

  const handleUpdateSupplier = async (id, supplierData) => {
    try {
      await supplierService.updateSupplier(id, supplierData);
      toast.success('공급업체 정보가 수정되었습니다.');
      setEditingSupplier(null);
      setShowForm(false);
      fetchSuppliers();
    } catch (error) {
      console.error('공급업체 수정 실패:', error);
      if (error.response?.data) {
        const errorMessages = Object.values(error.response.data).flat();
        toast.error(`수정 실패: ${errorMessages.join(', ')}`);
      } else {
        toast.error('공급업체 수정에 실패했습니다.');
      }
    }
  };

  const handleDeleteSupplier = async (id) => {
    if (!window.confirm('정말로 이 공급업체를 삭제하시겠습니까?\n관련된 원자재 로트가 있는 경우 삭제할 수 없습니다.')) {
      return;
    }

    try {
      await supplierService.deleteSupplier(id);
      toast.success('공급업체가 삭제되었습니다.');
      fetchSuppliers();
    } catch (error) {
      console.error('공급업체 삭제 실패:', error);
      if (error.response?.data?.detail) {
        toast.error(error.response.data.detail);
      } else if (error.response?.status === 400) {
        toast.error('원자재 로트가 존재하는 공급업체는 삭제할 수 없습니다.');
      } else {
        toast.error('공급업체 삭제에 실패했습니다.');
      }
    }
  };

  const handleEdit = (supplier) => {
    setEditingSupplier(supplier);
    setShowForm(true);
  };

  const handleFormClose = () => {
    setShowForm(false);
    setEditingSupplier(null);
  };

  // 필터 변경 처리
  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  // 공급업체 클릭 핸들러
  const handleSupplierClick = (supplier) => {
    navigate(`/suppliers/${supplier.id}`);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 페이지 헤더 */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">공급업체 관리</h1>
              <p className="mt-1 text-sm text-gray-500">
                공급업체 등록, 수정, 조회 및 성과 관리
              </p>
            </div>
            <button
              onClick={() => setShowForm(true)}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
            >
              공급업체 등록
            </button>
          </div>
        </div>

        {/* 필터 영역 */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                상태
              </label>
              <select
                value={filters.status}
                onChange={(e) => handleFilterChange('status', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
              >
                <option value="">전체</option>
                <option value="active">활성</option>
                <option value="inactive">비활성</option>
                <option value="suspended">정지</option>
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
                placeholder="공급업체명, 코드, 담당자로 검색"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
              />
            </div>

            <div className="flex items-end">
              <button
                onClick={fetchSuppliers}
                disabled={loading}
                className="w-full bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors disabled:opacity-50"
              >
                {loading ? '로딩중...' : '새로고침'}
              </button>
            </div>
          </div>
        </div>

        {/* 공급업체 목록 */}
        <div className="bg-white rounded-lg shadow">
          <LoadingCard loading={loading} className="p-8 text-center">
            <SupplierList
              suppliers={suppliers}
              loading={loading}
              onEdit={handleEdit}
              onDelete={handleDeleteSupplier}
              onSupplierClick={handleSupplierClick}
            />
          </LoadingCard>
        </div>

        {/* 공급업체 폼 모달 */}
        {showForm && (
          <SupplierForm
            isOpen={showForm}
            onClose={handleFormClose}
            onSubmit={editingSupplier ? handleUpdateSupplier : handleCreateSupplier}
            supplier={editingSupplier}
          />
        )}
      </div>
    </div>
  );
};

export default SuppliersPage;