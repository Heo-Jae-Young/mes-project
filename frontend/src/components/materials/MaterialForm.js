import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import Modal from '../common/Modal';

const MaterialForm = ({ 
  isOpen,
  onClose, 
  onSubmit, 
  material = null,
  suppliers = [],
  categories = []
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setValue,
    reset
  } = useForm({
    defaultValues: {
      name: '',
      code: '',
      description: '',
      category: '',
      supplier_id: '',
      unit: '',
      storage_temp_min: '',
      storage_temp_max: '',
      shelf_life_days: '',
      is_active: true,
      notes: ''
    }
  });

  // 수정 모드일 때 폼 데이터 설정
  useEffect(() => {
    if (material) {
      Object.keys(material).forEach((key) => {
        if (key === 'supplier') {
          // supplier 객체에서 id 추출하여 supplier_id로 설정
          setValue('supplier_id', material[key]?.id || material[key]);
        } else {
          setValue(key, material[key]);
        }
      });
    } else {
      reset();
    }
  }, [material, setValue, reset]);

  const onSubmitForm = async (data) => {
    const submitData = {
      ...data,
      supplier_id: data.supplier_id, // 백엔드는 supplier_id 필드를 사용
      storage_temp_min: data.storage_temp_min ? parseFloat(data.storage_temp_min) : null,
      storage_temp_max: data.storage_temp_max ? parseFloat(data.storage_temp_max) : null,
      shelf_life_days: data.shelf_life_days ? parseInt(data.shelf_life_days) : null,
    };
    
    console.log('전송할 데이터:', submitData); // 디버깅용
    console.log('수정 모드:', !!material); // 디버깅용
    console.log('원자재 ID:', material?.id); // 디버깅용

    if (material) {
      await onSubmit(material.id, submitData);
    } else {
      await onSubmit(submitData);
    }
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  return (
    <Modal 
      isOpen={isOpen}
      onClose={handleClose}
      title={material ? '원자재 수정' : '원자재 등록'}
      size="large"
    >
      <form onSubmit={handleSubmit(onSubmitForm)} className="space-y-6">
        {/* 기본 정보 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              원자재명 *
            </label>
            <input
              type="text"
              {...register('name', { 
                required: '원자재명은 필수입니다',
                minLength: {
                  value: 2,
                  message: '원자재명은 최소 2자 이상이어야 합니다'
                }
              })}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                errors.name ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="예: 밀가루, 설탕"
            />
            {errors.name && (
              <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              원자재 코드 *
            </label>
            <input
              type="text"
              {...register('code', { 
                required: '원자재 코드는 필수입니다',
                pattern: {
                  value: /^[A-Z0-9-]+$/,
                  message: '코드는 대문자, 숫자, 하이픈만 사용 가능합니다'
                }
              })}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                errors.code ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="예: FLOUR-001, SUGAR-001"
            />
            {errors.code && (
              <p className="mt-1 text-sm text-red-600">{errors.code.message}</p>
            )}
          </div>
        </div>

        {/* 카테고리 및 공급업체 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              카테고리 *
            </label>
            <select
              {...register('category', { 
                required: '카테고리를 선택해주세요'
              })}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                errors.category ? 'border-red-500' : 'border-gray-300'
              }`}
            >
              <option value="">카테고리 선택</option>
              {categories.map((category) => (
                <option key={category.key} value={category.key}>
                  {category.value}
                </option>
              ))}
            </select>
            {errors.category && (
              <p className="mt-1 text-sm text-red-600">{errors.category.message}</p>
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

        {/* 단위 및 보관 조건 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              단위 *
            </label>
            <input
              type="text"
              {...register('unit', { 
                required: '단위는 필수입니다'
              })}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                errors.unit ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="예: kg, L, 개"
            />
            {errors.unit && (
              <p className="mt-1 text-sm text-red-600">{errors.unit.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              최소 보관온도 (°C)
            </label>
            <input
              type="number"
              step="0.1"
              {...register('storage_temp_min')}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="예: -18"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              최대 보관온도 (°C)
            </label>
            <input
              type="number"
              step="0.1"
              {...register('storage_temp_max')}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="예: 4"
            />
          </div>
        </div>

        {/* 유통기한 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            유통기한 (일)
          </label>
          <input
            type="number"
            min="1"
            {...register('shelf_life_days')}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="예: 30 (30일)"
          />
        </div>

        {/* 설명 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            설명
          </label>
          <textarea
            {...register('description')}
            rows="3"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="원자재에 대한 상세 설명"
          />
        </div>

        {/* 메모 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            메모
          </label>
          <textarea
            {...register('notes')}
            rows="2"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="추가 메모사항"
          />
        </div>

        {/* 활성화 상태 */}
        <div className="flex items-center">
          <input
            type="checkbox"
            id="is_active"
            {...register('is_active')}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
            활성화 상태
          </label>
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
            {isSubmitting ? '저장 중...' : (material ? '수정' : '등록')}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default MaterialForm;