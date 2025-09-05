import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import Modal from '../common/Modal';

const MaterialLotForm = ({ 
  isOpen,
  onClose, 
  onSubmit, 
  material,
  suppliers = []
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setValue,
    reset,
    watch
  } = useForm({
    defaultValues: {
      lot_number: '',
      raw_material_id: material?.id || '',
      supplier_id: material?.supplier?.id || material?.supplier || '',
      received_date: new Date().toISOString().split('T')[0], // 오늘 날짜
      expiry_date: '',
      quantity_received: '',
      unit_price: '',
      status: 'received',
      quality_test_passed: null,
      quality_test_date: '',
      quality_test_notes: '',
      storage_location: '',
      temperature_at_receipt: ''
    }
  });

  // 기본값 설정
  useEffect(() => {
    if (material && isOpen) {
      setValue('raw_material_id', material.id);
      setValue('supplier_id', material.supplier?.id || material.supplier || '');
      
      // 유통기한 자동 계산 (shelf_life_days가 있는 경우)
      if (material.shelf_life_days) {
        const today = new Date();
        const expiryDate = new Date(today);
        expiryDate.setDate(today.getDate() + material.shelf_life_days);
        setValue('expiry_date', expiryDate.toISOString().split('T')[0]);
      }
    }
  }, [material, isOpen, setValue]);

  const onSubmitForm = async (data) => {
    // 날짜 형식 처리
    const formatDateTimeForAPI = (datetimeLocal) => {
      if (!datetimeLocal) return null;
      // datetime-local 값을 ISO format으로 변환
      const date = new Date(datetimeLocal);
      return date.toISOString();
    };

    const submitData = {
      lot_number: data.lot_number,
      raw_material_id: material.id,
      supplier_id: data.supplier_id,
      received_date: data.received_date, // YYYY-MM-DD 형식 그대로
      expiry_date: data.expiry_date || null,
      quantity_received: parseFloat(data.quantity_received),
      unit_price: parseFloat(data.unit_price),
      status: data.status || 'received',
      quality_test_passed: data.quality_test_passed === 'true' ? true : 
                          data.quality_test_passed === 'false' ? false : null,
      quality_test_date: formatDateTimeForAPI(data.quality_test_date),
      quality_test_notes: data.quality_test_notes || '',
      storage_location: data.storage_location || '',
      temperature_at_receipt: data.temperature_at_receipt ? parseFloat(data.temperature_at_receipt) : null
    };

    console.log('입고 처리 데이터:', submitData);
    await onSubmit(submitData);
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  // 품질검사 상태에 따른 품질검사 날짜 필수 여부
  const qualityTestPassed = watch('quality_test_passed');

  return (
    <Modal 
      isOpen={isOpen}
      onClose={handleClose}
      title={`${material?.name} - 입고 처리`}
      size="large"
    >
      <form onSubmit={handleSubmit(onSubmitForm)} className="space-y-6">
        {/* 원자재 정보 표시 */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-900 mb-2">원자재 정보</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">원자재명:</span>
              <span className="ml-2 font-medium">{material?.name}</span>
            </div>
            <div>
              <span className="text-gray-500">코드:</span>
              <span className="ml-2 font-medium">{material?.code}</span>
            </div>
            <div>
              <span className="text-gray-500">단위:</span>
              <span className="ml-2 font-medium">{material?.unit}</span>
            </div>
            <div>
              <span className="text-gray-500">유통기한:</span>
              <span className="ml-2 font-medium">
                {material?.shelf_life_days ? `${material.shelf_life_days}일` : '무제한'}
              </span>
            </div>
          </div>
        </div>

        {/* 기본 입고 정보 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              로트 번호 *
            </label>
            <input
              type="text"
              {...register('lot_number', { 
                required: '로트 번호는 필수입니다',
                minLength: {
                  value: 3,
                  message: '로트 번호는 최소 3자 이상이어야 합니다'
                }
              })}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                errors.lot_number ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="예: LOT-2024-001"
            />
            {errors.lot_number && (
              <p className="mt-1 text-sm text-red-600">{errors.lot_number.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              공급업체 *
            </label>
            <select
              {...register('supplier_id', { 
                required: '공급업체를 선택해주세요'
              })}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                errors.supplier_id ? 'border-red-500' : 'border-gray-300'
              }`}
            >
              <option value="">공급업체 선택</option>
              {suppliers.map((supplier) => (
                <option key={supplier.id} value={supplier.id}>
                  {supplier.name}
                </option>
              ))}
            </select>
            {errors.supplier_id && (
              <p className="mt-1 text-sm text-red-600">{errors.supplier_id.message}</p>
            )}
          </div>
        </div>

        {/* 날짜 정보 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              입고일 *
            </label>
            <input
              type="date"
              {...register('received_date', { 
                required: '입고일은 필수입니다'
              })}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                errors.received_date ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.received_date && (
              <p className="mt-1 text-sm text-red-600">{errors.received_date.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              유통기한
            </label>
            <input
              type="date"
              {...register('expiry_date')}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <p className="mt-1 text-xs text-gray-500">
              자동 계산된 날짜를 수정할 수 있습니다
            </p>
          </div>
        </div>

        {/* 수량 및 가격 정보 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              입고 수량 * ({material?.unit})
            </label>
            <input
              type="number"
              step="0.001"
              min="0.001"
              {...register('quantity_received', { 
                required: '입고 수량은 필수입니다',
                min: {
                  value: 0.001,
                  message: '수량은 0보다 커야 합니다'
                }
              })}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                errors.quantity_received ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="0.0"
            />
            {errors.quantity_received && (
              <p className="mt-1 text-sm text-red-600">{errors.quantity_received.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              단가 (원/{material?.unit}) *
            </label>
            <input
              type="number"
              step="0.01"
              min="0.01"
              {...register('unit_price', { 
                required: '단가는 필수입니다',
                min: {
                  value: 0.01,
                  message: '단가는 0보다 커야 합니다'
                }
              })}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                errors.unit_price ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="예: 1500.00"
            />
            {errors.unit_price && (
              <p className="mt-1 text-sm text-red-600">{errors.unit_price.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              입고 시 온도 (°C)
            </label>
            <input
              type="number"
              step="0.1"
              {...register('temperature_at_receipt')}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="예: -18.0"
            />
          </div>
        </div>

        {/* 품질검사 정보 */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">품질검사</h3>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              품질검사 결과
            </label>
            <select
              {...register('quality_test_passed')}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">미검사</option>
              <option value="true">합격</option>
              <option value="false">불합격</option>
            </select>
          </div>

          {qualityTestPassed && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                품질검사 일시 *
              </label>
              <input
                type="datetime-local"
                {...register('quality_test_date', {
                  required: qualityTestPassed ? '품질검사 결과가 있는 경우 검사 일시는 필수입니다' : false
                })}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.quality_test_date ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.quality_test_date && (
                <p className="mt-1 text-sm text-red-600">{errors.quality_test_date.message}</p>
              )}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              품질검사 메모
            </label>
            <textarea
              {...register('quality_test_notes')}
              rows="3"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="품질검사 관련 메모사항"
            />
          </div>
        </div>

        {/* 보관 위치 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            보관 위치
          </label>
          <input
            type="text"
            {...register('storage_location')}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="예: 냉동창고 A-1"
          />
        </div>

        {/* 버튼 */}
        <div className="flex justify-end space-x-3 pt-4 border-t">
          <button
            type="button"
            onClick={handleClose}
            disabled={isSubmitting}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50"
          >
            취소
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {isSubmitting ? '처리 중...' : '입고 처리'}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default MaterialLotForm;