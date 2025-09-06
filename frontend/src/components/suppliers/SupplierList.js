import React from 'react';
import { PencilIcon, TrashIcon, BuildingOfficeIcon, PhoneIcon, EnvelopeIcon } from '@heroicons/react/24/outline';
import LoadingSpinner from '../common/LoadingSpinner';

const SupplierList = ({ 
  suppliers = [],
  loading = false,
  onEdit,
  onDelete,
  onSupplierClick
}) => {

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
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
        statusConfig[status] || 'bg-gray-100 text-gray-800'
      }`}>
        {statusLabels[status] || status}
      </span>
    );
  };

  if (loading && suppliers.length === 0) {
    return <LoadingSpinner size="large" />;
  }

  return (
    suppliers.length === 0 && !loading ? (
      <div className="text-center py-12 bg-white rounded-lg border">
        <BuildingOfficeIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-500">등록된 공급업체가 없습니다.</p>
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
                  연락처
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  주소
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  인증 정보
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
              {suppliers.map((supplier) => (
                <tr 
                  key={supplier.id} 
                  className="hover:bg-gray-50 cursor-pointer"
                  onClick={() => onSupplierClick && onSupplierClick(supplier)}
                >
                  <td className="px-6 py-4">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {supplier.name}
                      </div>
                      <div className="text-sm text-gray-500">
                        {supplier.code}
                      </div>
                      <div className="text-xs text-gray-400 mt-1 flex items-center">
                        <BuildingOfficeIcon className="h-3 w-3 mr-1" />
                        {supplier.contact_person}
                      </div>
                    </div>
                  </td>
                  
                  <td className="px-6 py-4">
                    <div className="space-y-1">
                      <div className="text-sm text-gray-900 flex items-center">
                        <PhoneIcon className="h-4 w-4 mr-2 text-gray-400" />
                        {supplier.phone}
                      </div>
                      <div className="text-sm text-gray-500 flex items-center">
                        <EnvelopeIcon className="h-4 w-4 mr-2 text-gray-400" />
                        {supplier.email}
                      </div>
                    </div>
                  </td>
                  
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900 max-w-xs">
                      {supplier.address.length > 50 
                        ? `${supplier.address.substring(0, 50)}...` 
                        : supplier.address}
                    </div>
                  </td>
                  
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">
                      {supplier.certification ? (
                        supplier.certification.length > 30 
                          ? `${supplier.certification.substring(0, 30)}...`
                          : supplier.certification
                      ) : (
                        <span className="text-gray-400">인증 정보 없음</span>
                      )}
                    </div>
                  </td>
                  
                  <td className="px-6 py-4">
                    {getStatusBadge(supplier.status)}
                  </td>
                  
                  <td className="px-6 py-4">
                    <div className="flex space-x-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onEdit(supplier);
                        }}
                        className="text-green-600 hover:text-green-900 transition-colors"
                        title="수정"
                      >
                        <PencilIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onDelete(supplier.id);
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

export default SupplierList;