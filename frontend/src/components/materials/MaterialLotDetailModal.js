import React, { useState } from 'react';
import { XMarkIcon, ExclamationTriangleIcon, CheckIcon, XCircleIcon, TrashIcon, NoSymbolIcon } from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';
import materialService from '../../services/materialService';

const MaterialLotDetailModal = ({ isOpen, onClose, lot, material, onLotUpdated }) => {
  const [updating, setUpdating] = useState(false);
  
  if (!isOpen || !lot) return null;

  // 유통기한까지 남은 일수 계산
  const getDaysUntilExpiry = (expiryDate) => {
    if (!expiryDate) return null;
    const today = new Date();
    const expiry = new Date(expiryDate);
    const diffTime = expiry - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  // 로트 상태 배지
  const getLotStatusBadge = (status) => {
    const statusColors = {
      'received': 'bg-blue-100 text-blue-800',
      'in_storage': 'bg-green-100 text-green-800',
      'in_use': 'bg-yellow-100 text-yellow-800',
      'used': 'bg-gray-100 text-gray-800',
      'expired': 'bg-red-100 text-red-800',
      'rejected': 'bg-red-100 text-red-800'
    };
    
    const statusLabels = {
      'received': '입고됨',
      'in_storage': '보관중',
      'in_use': '사용중',
      'used': '사용완료',
      'expired': '유통기한만료',
      'rejected': '반품'
    };

    return (
      <span className={`px-3 py-1 text-sm font-medium rounded-full ${statusColors[status] || 'bg-gray-100 text-gray-800'}`}>
        {statusLabels[status] || status}
      </span>
    );
  };

  // 품질검사 상태 배지
  const getQualityTestBadge = (passed) => {
    if (passed === true) {
      return (
        <span className="px-3 py-1 text-sm font-medium rounded-full bg-green-100 text-green-800">
          합격
        </span>
      );
    } else if (passed === false) {
      return (
        <span className="px-3 py-1 text-sm font-medium rounded-full bg-red-100 text-red-800">
          불합격
        </span>
      );
    } else {
      return (
        <span className="px-3 py-1 text-sm font-medium rounded-full bg-gray-100 text-gray-800">
          미검사
        </span>
      );
    }
  };

  // 통화 포맷
  const formatCurrency = (value) => {
    if (!value || value === 0) return '-';
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW',
      minimumFractionDigits: 0,
    }).format(value);
  };

  // 온도 표시
  const formatTemperature = (temp) => {
    return temp !== null && temp !== undefined ? `${temp}°C` : '-';
  };

  // 품질검사 상태 업데이트
  const handleQualityTestUpdate = async (testResult, notes = '') => {
    if (updating) return;
    
    const confirmMessage = testResult === true 
      ? '이 로트를 품질검사 합격으로 처리하시겠습니까?'
      : '이 로트를 품질검사 불합격으로 처리하시겠습니까?';
    
    if (!window.confirm(confirmMessage)) {
      return;
    }

    setUpdating(true);
    try {
      const updateData = {
        quality_test_passed: testResult,
        quality_test_date: new Date().toISOString(),
        quality_test_notes: notes || (testResult === true ? '검사 통과' : '검사 불합격')
      };
      
      await materialService.updateMaterialLot(lot.id, updateData);
      
      toast.success(`품질검사가 ${testResult ? '합격' : '불합격'}으로 처리되었습니다.`);
      
      // 부모 컴포넌트에 업데이트 알림
      if (onLotUpdated) {
        onLotUpdated();
      }
      
      onClose();
    } catch (error) {
      console.error('품질검사 상태 업데이트 실패:', error);
      if (error.response?.data?.detail) {
        toast.error(error.response.data.detail);
      } else {
        toast.error('품질검사 상태 업데이트에 실패했습니다.');
      }
    } finally {
      setUpdating(false);
    }
  };

  // 로트 상태 변경 (만료/폐기)
  const handleLotStatusUpdate = async (newStatus, reason = '') => {
    if (updating) return;
    
    const statusMessages = {
      'expired': '이 로트를 유통기한 만료로 처리하시겠습니까?',
      'rejected': '이 로트를 반품/폐기로 처리하시겠습니까?'
    };
    
    const statusLabels = {
      'expired': '유통기한 만료',
      'rejected': '반품/폐기'
    };
    
    if (!window.confirm(statusMessages[newStatus] + '\n\n⚠️ 이 작업은 되돌릴 수 없으며, 해당 로트는 더 이상 사용할 수 없게 됩니다.')) {
      return;
    }

    setUpdating(true);
    try {
      const updateData = {
        status: newStatus,
        quality_test_notes: reason || `${statusLabels[newStatus]} 처리됨 - ${new Date().toLocaleString('ko-KR')}`
      };
      
      await materialService.updateMaterialLot(lot.id, updateData);
      
      toast.success(`로트가 ${statusLabels[newStatus]}로 처리되었습니다.`);
      
      // 부모 컴포넌트에 업데이트 알림
      if (onLotUpdated) {
        onLotUpdated();
      }
      
      onClose();
    } catch (error) {
      console.error('로트 상태 업데이트 실패:', error);
      if (error.response?.data?.detail) {
        toast.error(error.response.data.detail);
      } else {
        toast.error('로트 상태 업데이트에 실패했습니다.');
      }
    } finally {
      setUpdating(false);
    }
  };

  const daysUntilExpiry = lot.expiry_date ? getDaysUntilExpiry(lot.expiry_date) : null;
  const isNearExpiry = daysUntilExpiry !== null && daysUntilExpiry <= 30;
  const isExpired = daysUntilExpiry !== null && daysUntilExpiry < 0;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-10 mx-auto p-5 border w-full max-w-4xl shadow-lg rounded-md bg-white">
        {/* 헤더 */}
        <div className="flex items-center justify-between border-b border-gray-200 pb-4">
          <div>
            <h3 className="text-xl font-bold text-gray-900">로트 상세 정보</h3>
            <p className="text-sm text-gray-500 mt-1">{material?.name} - {lot.lot_number}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        <div className="mt-6">
          {/* 기본 정보 섹션 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            {/* 로트 식별 정보 */}
            <div className="bg-gray-50 p-6 rounded-lg">
              <h4 className="text-lg font-semibold text-gray-900 mb-4">로트 식별 정보</h4>
              <dl className="grid grid-cols-1 gap-3">
                <div>
                  <dt className="text-sm font-medium text-gray-500">로트 번호</dt>
                  <dd className="text-lg font-semibold text-gray-900">{lot.lot_number}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">로트 ID</dt>
                  <dd className="text-sm text-gray-600 font-mono">#{lot.id}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">상태</dt>
                  <dd className="mt-1">{getLotStatusBadge(lot.status)}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">공급업체</dt>
                  <dd className="text-sm text-gray-900">
                    {typeof lot.supplier === 'object' ? lot.supplier.name : '정보 없음'}
                  </dd>
                </div>
              </dl>
            </div>

            {/* 수량 및 가격 정보 */}
            <div className="bg-blue-50 p-6 rounded-lg">
              <h4 className="text-lg font-semibold text-gray-900 mb-4">수량 및 가격 정보</h4>
              <dl className="grid grid-cols-1 gap-3">
                <div>
                  <dt className="text-sm font-medium text-gray-500">입고 수량</dt>
                  <dd className="text-lg font-semibold text-gray-900">
                    {lot.quantity_received} {material?.unit || ''}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">현재 수량</dt>
                  <dd className="text-lg font-semibold text-blue-900">
                    {lot.quantity_current} {material?.unit || ''}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">사용률</dt>
                  <dd className="text-sm text-gray-900">
                    {((lot.quantity_received - lot.quantity_current) / lot.quantity_received * 100).toFixed(1)}%
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">단가</dt>
                  <dd className="text-sm text-gray-900">{formatCurrency(lot.unit_price)}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">총 가치</dt>
                  <dd className="text-lg font-semibold text-blue-900">
                    {formatCurrency(lot.quantity_current * lot.unit_price)}
                  </dd>
                </div>
              </dl>
            </div>
          </div>

          {/* 날짜 및 유통기한 정보 */}
          <div className="bg-white border border-gray-200 p-6 rounded-lg mb-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">날짜 정보</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <dt className="text-sm font-medium text-gray-500">입고일</dt>
                <dd className="text-sm text-gray-900">
                  {new Date(lot.received_date).toLocaleString('ko-KR')}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">유통기한</dt>
                <dd className="text-sm text-gray-900 flex items-center">
                  {lot.expiry_date ? new Date(lot.expiry_date).toLocaleDateString('ko-KR') : '무제한'}
                  {isNearExpiry && !isExpired && (
                    <ExclamationTriangleIcon className="h-4 w-4 text-yellow-500 ml-2" title="유통기한 임박" />
                  )}
                  {isExpired && (
                    <ExclamationTriangleIcon className="h-4 w-4 text-red-500 ml-2" title="유통기한 만료" />
                  )}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">남은 일수</dt>
                <dd className={`text-sm font-medium ${
                  isExpired ? 'text-red-600' : 
                  isNearExpiry ? 'text-yellow-600' : 'text-green-600'
                }`}>
                  {daysUntilExpiry !== null ? `${daysUntilExpiry}일` : '-'}
                </dd>
              </div>
            </div>
          </div>

          {/* 품질검사 정보 */}
          <div className="bg-white border border-gray-200 p-6 rounded-lg mb-6">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-lg font-semibold text-gray-900">품질검사 정보</h4>
              {lot.quality_test_passed === null && (
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleQualityTestUpdate(true)}
                    disabled={updating}
                    className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <CheckIcon className="h-4 w-4 mr-1" />
                    합격 처리
                  </button>
                  <button
                    onClick={() => handleQualityTestUpdate(false)}
                    disabled={updating}
                    className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <XCircleIcon className="h-4 w-4 mr-1" />
                    불합격 처리
                  </button>
                </div>
              )}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <dt className="text-sm font-medium text-gray-500">검사 결과</dt>
                <dd className="mt-1 flex items-center">
                  {getQualityTestBadge(lot.quality_test_passed)}
                  {updating && (
                    <div className="ml-2 animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                  )}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">검사일</dt>
                <dd className="text-sm text-gray-900">
                  {lot.quality_test_date ? 
                    new Date(lot.quality_test_date).toLocaleString('ko-KR') : 
                    '미검사'}
                </dd>
              </div>
            </div>
            {lot.quality_test_notes && (
              <div className="mt-4">
                <dt className="text-sm font-medium text-gray-500">검사 메모</dt>
                <dd className="mt-1 text-sm text-gray-900 bg-gray-50 p-3 rounded-lg">
                  {lot.quality_test_notes}
                </dd>
              </div>
            )}
            {lot.quality_test_passed === null && (
              <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-sm text-yellow-800">
                  <ExclamationTriangleIcon className="h-4 w-4 inline mr-1" />
                  이 로트는 아직 품질검사가 완료되지 않았습니다. 위의 버튼을 사용하여 검사 결과를 입력하세요.
                </p>
              </div>
            )}
          </div>

          {/* 보관 정보 */}
          <div className="bg-white border border-gray-200 p-6 rounded-lg mb-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">보관 정보</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <dt className="text-sm font-medium text-gray-500">보관 위치</dt>
                <dd className="text-sm text-gray-900">{lot.storage_location || '미지정'}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">입고시 온도</dt>
                <dd className="text-sm text-gray-900">
                  {formatTemperature(lot.temperature_at_receipt)}
                </dd>
              </div>
            </div>
          </div>

          {/* 사용 이력 및 추적성 */}
          <div className="bg-white border border-gray-200 p-6 rounded-lg mb-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">사용 이력 및 추적성</h4>
            
            {/* 수량 변화 요약 */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-blue-50 p-4 rounded-lg">
                <dt className="text-sm font-medium text-blue-600">입고 수량</dt>
                <dd className="text-xl font-bold text-blue-900">
                  {lot.quantity_received} {material?.unit}
                </dd>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <dt className="text-sm font-medium text-green-600">현재 수량</dt>
                <dd className="text-xl font-bold text-green-900">
                  {lot.quantity_current} {material?.unit}
                </dd>
              </div>
              <div className="bg-orange-50 p-4 rounded-lg">
                <dt className="text-sm font-medium text-orange-600">소비 수량</dt>
                <dd className="text-xl font-bold text-orange-900">
                  {(lot.quantity_received - lot.quantity_current).toFixed(3)} {material?.unit}
                </dd>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <dt className="text-sm font-medium text-purple-600">소비율</dt>
                <dd className="text-xl font-bold text-purple-900">
                  {((lot.quantity_received - lot.quantity_current) / lot.quantity_received * 100).toFixed(1)}%
                </dd>
              </div>
            </div>

            {/* 사용 상태 타임라인 */}
            <div className="space-y-4">
              <h5 className="text-md font-semibold text-gray-800">로트 상태 이력</h5>
              <div className="space-y-3">
                {/* 입고 기록 */}
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <div className="w-3 h-3 bg-blue-600 rounded-full"></div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-gray-900">입고 처리</span>
                      <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                        {lot.quantity_received} {material?.unit}
                      </span>
                    </div>
                    <div className="text-sm text-gray-500">
                      {new Date(lot.received_date).toLocaleString('ko-KR')}
                    </div>
                  </div>
                </div>

                {/* 품질검사 기록 */}
                {lot.quality_test_date && (
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                      <div className="w-3 h-3 bg-green-600 rounded-full"></div>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-gray-900">품질검사</span>
                        {getQualityTestBadge(lot.quality_test_passed)}
                      </div>
                      <div className="text-sm text-gray-500">
                        {new Date(lot.quality_test_date).toLocaleString('ko-KR')}
                      </div>
                      {lot.quality_test_notes && (
                        <div className="text-sm text-gray-600 mt-1">
                          {lot.quality_test_notes}
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* 사용 기록 (소비된 경우) */}
                {lot.quantity_received > lot.quantity_current && (
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center">
                      <div className="w-3 h-3 bg-orange-600 rounded-full"></div>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-gray-900">부분 소비됨</span>
                        <span className="px-2 py-1 text-xs bg-orange-100 text-orange-800 rounded-full">
                          -{(lot.quantity_received - lot.quantity_current).toFixed(3)} {material?.unit}
                        </span>
                      </div>
                      <div className="text-sm text-gray-500">
                        최종 업데이트: {new Date(lot.updated_at).toLocaleString('ko-KR')}
                      </div>
                      <div className="text-sm text-gray-600 mt-1">
                        현재 상태: {getLotStatusBadge(lot.status).props.children}
                      </div>
                    </div>
                  </div>
                )}

                {/* 완전 소비 기록 */}
                {lot.quantity_current === 0 && (
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                      <div className="w-3 h-3 bg-gray-600 rounded-full"></div>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-gray-900">완전 소진됨</span>
                        <span className="px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded-full">
                          전량 사용 완료
                        </span>
                      </div>
                      <div className="text-sm text-gray-500">
                        {new Date(lot.updated_at).toLocaleString('ko-KR')}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* HACCP 추적성 알림 */}
            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h6 className="text-sm font-semibold text-blue-800 mb-2">HACCP 추적성 정보</h6>
              <div className="text-sm text-blue-700 space-y-1">
                <div>• 로트 ID: <code className="bg-blue-100 px-1 rounded text-xs">{lot.id}</code></div>
                <div>• 공급업체: {typeof lot.supplier === 'object' ? lot.supplier.name : '정보 없음'}</div>
                <div>• 입고자: {typeof lot.created_by === 'object' ? (lot.created_by?.username || lot.created_by?.first_name || '시스템') : (lot.created_by || '시스템')}</div>
                <div>• 완전한 순방향/역방향 추적이 가능합니다.</div>
              </div>
            </div>
          </div>

          {/* 메타데이터 */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="text-sm font-semibold text-gray-700 mb-2">시스템 정보</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-gray-600">
              <div>
                <span className="font-medium">생성일:</span> {new Date(lot.created_at).toLocaleString('ko-KR')}
              </div>
              <div>
                <span className="font-medium">수정일:</span> {new Date(lot.updated_at).toLocaleString('ko-KR')}
              </div>
            </div>
          </div>
        </div>

        {/* 푸터 */}
        <div className="mt-8 flex justify-between">
          {/* 위험한 작업 버튼들 (왼쪽) */}
          <div className="flex space-x-2">
            {/* 로트가 활성 상태이고 만료되지 않은 경우에만 표시 */}
            {lot.status !== 'expired' && lot.status !== 'rejected' && lot.status !== 'used' && (
              <>
                {/* 유통기한 만료 처리 */}
                {(isExpired || isNearExpiry) && (
                  <button
                    onClick={() => handleLotStatusUpdate('expired', `유통기한 만료 처리 (${daysUntilExpiry}일 ${daysUntilExpiry > 0 ? '남음' : '초과'})`)}
                    disabled={updating}
                    className="inline-flex items-center px-3 py-2 text-sm font-medium text-white bg-orange-600 rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    title="유통기한 만료로 처리"
                  >
                    <ExclamationTriangleIcon className="h-4 w-4 mr-1" />
                    만료 처리
                  </button>
                )}
                
                {/* 폐기/반품 처리 */}
                <button
                  onClick={() => handleLotStatusUpdate('rejected', '관리자에 의한 반품/폐기 처리')}
                  disabled={updating}
                  className="inline-flex items-center px-3 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  title="반품/폐기로 처리"
                >
                  <NoSymbolIcon className="h-4 w-4 mr-1" />
                  폐기 처리
                </button>
              </>
            )}
            
            {/* 로트가 비활성 상태인 경우 상태 표시 */}
            {(lot.status === 'expired' || lot.status === 'rejected') && (
              <div className="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-500 bg-gray-100 rounded-lg">
                <NoSymbolIcon className="h-4 w-4 mr-1" />
                {lot.status === 'expired' ? '만료된 로트' : '폐기된 로트'}
              </div>
            )}
          </div>

          {/* 일반 버튼들 (오른쪽) */}
          <div className="flex space-x-2">
            {updating && (
              <div className="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-600">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                처리중...
              </div>
            )}
            <button
              onClick={onClose}
              disabled={updating}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              닫기
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MaterialLotDetailModal;