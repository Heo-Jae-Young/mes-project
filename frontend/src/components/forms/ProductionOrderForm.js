import React, { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { getCurrentDateTimeLocal, toISOString } from '../../utils/dateFormatter';
import productionService from '../../services/productionService';

const ProductionOrderForm = ({ onClose, onSubmit, initialData = null }) => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setValue,
    watch
  } = useForm({
    defaultValues: {
      order_number: '',
      finished_product_id: '',
      planned_quantity: '',
      planned_start_date: getCurrentDateTimeLocal(),
      planned_end_date: (() => {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        return tomorrow.toISOString().slice(0, 16);
      })(),
      priority: 'normal',
      notes: ''
    }
  });

  const watchStartDate = watch('planned_start_date');
  const [products, setProducts] = useState([]);
  const [loadingProducts, setLoadingProducts] = useState(true);

  // 제품 목록 로드
  useEffect(() => {
    const loadProducts = async () => {
      try {
        const productsData = await productionService.getFinishedProducts();
        setProducts(productsData.results || productsData);
      } catch (error) {
        console.error('제품 목록 로드 실패:', error);
      } finally {
        setLoadingProducts(false);
      }
    };
    
    loadProducts();
  }, []);

  useEffect(() => {
    if (initialData) {
      Object.keys(initialData).forEach((key) => {
        if (key === 'planned_start_date' || key === 'planned_end_date') {
          setValue(key, new Date(initialData[key]).toISOString().slice(0, 16));
        } else {
          setValue(key, initialData[key]);
        }
      });
    }
  }, [initialData, setValue]);

  const onSubmitForm = async (data) => {
    const submitData = {
      ...data,
      planned_quantity: parseInt(data.planned_quantity),
      planned_start_date: toISOString(data.planned_start_date),
      planned_end_date: toISOString(data.planned_end_date)
    };

    await onSubmit(submitData);
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-2xl shadow-lg rounded-md bg-white">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">
            {initialData ? '생산 주문 수정' : '새 생산 주문'}
          </h3>
          <button
            onClick={onClose}
            type="button"
            className="text-gray-400 hover:text-gray-600"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmitForm)} className="space-y-4">
          {/* 주문번호 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              주문번호 *
            </label>
            <input
              type="text"
              {...register('order_number', { 
                required: '주문번호는 필수입니다',
                minLength: {
                  value: 3,
                  message: '주문번호는 최소 3자 이상이어야 합니다'
                }
              })}
              placeholder="예: PO-2024-001"
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                errors.order_number ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.order_number && (
              <p className="mt-1 text-sm text-red-600">{errors.order_number.message}</p>
            )}
          </div>

          {/* 제품 선택 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              제품 *
            </label>
            {loadingProducts ? (
              <div className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50">
                제품 목록 로딩 중...
              </div>
            ) : (
              <select
                {...register('finished_product_id', { 
                  required: '제품을 선택해주세요'
                })}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.finished_product_id ? 'border-red-500' : 'border-gray-300'
                }`}
              >
                <option value="">제품을 선택하세요</option>
                {products.map((product) => (
                  <option key={product.id} value={product.id}>
                    {product.code} - {product.name}
                  </option>
                ))}
              </select>
            )}
            {errors.finished_product_id && (
              <p className="mt-1 text-sm text-red-600">{errors.finished_product_id.message}</p>
            )}
          </div>

          {/* 계획 수량 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              계획 수량 *
            </label>
            <input
              type="number"
              {...register('planned_quantity', { 
                required: '계획 수량은 필수입니다',
                min: {
                  value: 1,
                  message: '계획 수량은 1 이상이어야 합니다'
                },
                max: {
                  value: 1000000,
                  message: '계획 수량은 1,000,000 이하여야 합니다'
                }
              })}
              min="1"
              placeholder="생산할 수량"
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                errors.planned_quantity ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.planned_quantity && (
              <p className="mt-1 text-sm text-red-600">{errors.planned_quantity.message}</p>
            )}
          </div>

          {/* 날짜 입력 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                계획 시작일 *
              </label>
              <input
                type="datetime-local"
                {...register('planned_start_date', { 
                  required: '계획 시작일은 필수입니다',
                  validate: (value) => {
                    const selectedDate = new Date(value);
                    const now = new Date();
                    if (selectedDate < now) {
                      return '시작일은 현재 시간 이후여야 합니다';
                    }
                    return true;
                  }
                })}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.planned_start_date ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.planned_start_date && (
                <p className="mt-1 text-sm text-red-600">{errors.planned_start_date.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                계획 종료일 *
              </label>
              <input
                type="datetime-local"
                {...register('planned_end_date', { 
                  required: '계획 종료일은 필수입니다',
                  validate: (value) => {
                    if (!watchStartDate) return true;
                    const startDate = new Date(watchStartDate);
                    const endDate = new Date(value);
                    if (endDate <= startDate) {
                      return '종료일은 시작일보다 늦어야 합니다';
                    }
                    return true;
                  }
                })}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.planned_end_date ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.planned_end_date && (
                <p className="mt-1 text-sm text-red-600">{errors.planned_end_date.message}</p>
              )}
            </div>
          </div>

          {/* 우선순위 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              우선순위
            </label>
            <select
              {...register('priority')}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="low">낮음</option>
              <option value="normal">보통</option>
              <option value="high">높음</option>
              <option value="urgent">긴급</option>
            </select>
          </div>

          {/* 메모 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              메모
            </label>
            <textarea
              {...register('notes')}
              rows="3"
              placeholder="추가 메모 사항"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* 버튼 */}
          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
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
              {isSubmitting ? '저장 중...' : (initialData ? '수정' : '생성')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProductionOrderForm;