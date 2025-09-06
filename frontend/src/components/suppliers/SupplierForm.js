import React, { useState, useEffect } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';

const SupplierForm = ({ isOpen, onClose, onSubmit, supplier = null }) => {
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    contact_person: '',
    email: '',
    phone: '',
    address: '',
    certification: '',
    status: 'active'
  });
  const [loading, setLoading] = useState(false);

  // 편집 모드인 경우 폼 데이터 초기화
  useEffect(() => {
    if (supplier) {
      setFormData({
        name: supplier.name || '',
        code: supplier.code || '',
        contact_person: supplier.contact_person || '',
        email: supplier.email || '',
        phone: supplier.phone || '',
        address: supplier.address || '',
        certification: supplier.certification || '',
        status: supplier.status || 'active'
      });
    } else {
      setFormData({
        name: '',
        code: '',
        contact_person: '',
        email: '',
        phone: '',
        address: '',
        certification: '',
        status: 'active'
      });
    }
  }, [supplier]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // 기본 유효성 검증
    if (!formData.name.trim()) {
      alert('공급업체명을 입력해주세요.');
      return;
    }
    if (!formData.code.trim()) {
      alert('공급업체 코드를 입력해주세요.');
      return;
    }
    if (!formData.contact_person.trim()) {
      alert('담당자명을 입력해주세요.');
      return;
    }
    if (!formData.email.trim()) {
      alert('이메일을 입력해주세요.');
      return;
    }
    if (!formData.phone.trim()) {
      alert('전화번호를 입력해주세요.');
      return;
    }
    if (!formData.address.trim()) {
      alert('주소를 입력해주세요.');
      return;
    }

    setLoading(true);
    try {
      if (supplier) {
        await onSubmit(supplier.id, formData);
      } else {
        await onSubmit(formData);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-10 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
        {/* 헤더 */}
        <div className="flex items-center justify-between border-b border-gray-200 pb-4 mb-6">
          <h3 className="text-xl font-bold text-gray-900">
            {supplier ? '공급업체 수정' : '공급업체 등록'}
          </h3>
          <button
            onClick={handleClose}
            disabled={loading}
            className="text-gray-400 hover:text-gray-600 transition-colors disabled:opacity-50"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        {/* 폼 */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* 기본 정보 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                공급업체명 <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                disabled={loading}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:opacity-50 disabled:bg-gray-100"
                placeholder="예: 한국식품㈜"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                공급업체 코드 <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="code"
                value={formData.code}
                onChange={handleChange}
                disabled={loading}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:opacity-50 disabled:bg-gray-100"
                placeholder="예: SUP001"
                required
              />
            </div>
          </div>

          {/* 담당자 정보 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                담당자명 <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="contact_person"
                value={formData.contact_person}
                onChange={handleChange}
                disabled={loading}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:opacity-50 disabled:bg-gray-100"
                placeholder="예: 김영업"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                이메일 <span className="text-red-500">*</span>
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                disabled={loading}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:opacity-50 disabled:bg-gray-100"
                placeholder="예: contact@supplier.com"
                required
              />
            </div>
          </div>

          {/* 연락처 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              전화번호 <span className="text-red-500">*</span>
            </label>
            <input
              type="tel"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              disabled={loading}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:opacity-50 disabled:bg-gray-100"
              placeholder="예: 02-1234-5678"
              required
            />
          </div>

          {/* 주소 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              주소 <span className="text-red-500">*</span>
            </label>
            <textarea
              name="address"
              value={formData.address}
              onChange={handleChange}
              disabled={loading}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:opacity-50 disabled:bg-gray-100"
              placeholder="공급업체 주소를 입력하세요"
              required
            />
          </div>

          {/* 인증 정보 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              인증 정보
            </label>
            <textarea
              name="certification"
              value={formData.certification}
              onChange={handleChange}
              disabled={loading}
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:opacity-50 disabled:bg-gray-100"
              placeholder="HACCP, ISO, FSSC 등 인증 정보를 입력하세요"
            />
            <p className="mt-1 text-sm text-gray-500">
              HACCP, ISO 22000, FSSC 22000 등 보유 인증을 기입해주세요
            </p>
          </div>

          {/* 상태 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              상태
            </label>
            <select
              name="status"
              value={formData.status}
              onChange={handleChange}
              disabled={loading}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:opacity-50 disabled:bg-gray-100"
            >
              <option value="active">활성</option>
              <option value="inactive">비활성</option>
              <option value="suspended">정지</option>
            </select>
          </div>

          {/* 버튼 */}
          <div className="flex justify-end space-x-3 pt-6 border-t">
            <button
              type="button"
              onClick={handleClose}
              disabled={loading}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50"
            >
              취소
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {loading && (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              )}
              {loading ? '처리중...' : (supplier ? '수정' : '등록')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SupplierForm;