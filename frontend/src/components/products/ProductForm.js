import React, { useState, useEffect } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';

const ProductForm = ({ product, onSubmit, onCancel, isEditing }) => {
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    description: '',
    version: '1.0',
    shelf_life_days: '',
    storage_temp_min: '',
    storage_temp_max: '',
    net_weight: '',
    packaging_type: '',
    allergen_info: '',
    nutrition_facts: '',
    is_active: true
  });

  const [nutritionFactsJson, setNutritionFactsJson] = useState({
    calories: '',
    protein: '',
    fat: '',
    carbohydrates: '',
    sodium: ''
  });

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  // 수정 모드일 때 기존 데이터 로드
  useEffect(() => {
    if (isEditing && product) {
      setFormData({
        name: product.name || '',
        code: product.code || '',
        description: product.description || '',
        version: product.version || '1.0',
        shelf_life_days: product.shelf_life_days?.toString() || '',
        storage_temp_min: product.storage_temp_min?.toString() || '',
        storage_temp_max: product.storage_temp_max?.toString() || '',
        net_weight: product.net_weight?.toString() || '',
        packaging_type: product.packaging_type || '',
        allergen_info: product.allergen_info || '',
        nutrition_facts: product.nutrition_facts || '',
        is_active: product.is_active !== undefined ? product.is_active : true
      });

      // 영양성분 정보 파싱
      if (product.nutrition_facts) {
        const facts = typeof product.nutrition_facts === 'string' 
          ? JSON.parse(product.nutrition_facts) 
          : product.nutrition_facts;
        
        setNutritionFactsJson({
          calories: facts.calories?.toString() || '',
          protein: facts.protein?.toString() || '',
          fat: facts.fat?.toString() || '',
          carbohydrates: facts.carbohydrates?.toString() || '',
          sodium: facts.sodium?.toString() || ''
        });
      }
    }
  }, [isEditing, product]);

  // 입력값 변경 처리
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));

    // 에러 메시지 클리어
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  // 영양성분 변경 처리
  const handleNutritionChange = (e) => {
    const { name, value } = e.target;
    setNutritionFactsJson(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // 폼 유효성 검사
  const validateForm = () => {
    const newErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = '제품명을 입력해주세요';
    }

    if (!formData.code.trim()) {
      newErrors.code = '제품 코드를 입력해주세요';
    }

    if (!formData.shelf_life_days) {
      newErrors.shelf_life_days = '유통기한을 입력해주세요';
    } else if (parseInt(formData.shelf_life_days) <= 0) {
      newErrors.shelf_life_days = '유통기한은 1일 이상이어야 합니다';
    }

    if (!formData.net_weight) {
      newErrors.net_weight = '중량을 입력해주세요';
    } else if (parseFloat(formData.net_weight) <= 0) {
      newErrors.net_weight = '중량은 0보다 커야 합니다';
    }

    if (!formData.packaging_type.trim()) {
      newErrors.packaging_type = '포장형태를 입력해주세요';
    }

    // 온도 범위 검증
    if (formData.storage_temp_min && formData.storage_temp_max) {
      const minTemp = parseFloat(formData.storage_temp_min);
      const maxTemp = parseFloat(formData.storage_temp_max);
      
      if (minTemp >= maxTemp) {
        newErrors.storage_temp_max = '최고온도는 최저온도보다 높아야 합니다';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // 폼 제출 처리
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      // 영양성분 JSON 생성
      const nutritionFacts = {};
      Object.entries(nutritionFactsJson).forEach(([key, value]) => {
        if (value && value.trim()) {
          nutritionFacts[key] = parseFloat(value) || value;
        }
      });

      const submitData = {
        ...formData,
        shelf_life_days: parseInt(formData.shelf_life_days),
        storage_temp_min: formData.storage_temp_min ? parseFloat(formData.storage_temp_min) : null,
        storage_temp_max: formData.storage_temp_max ? parseFloat(formData.storage_temp_max) : null,
        net_weight: parseFloat(formData.net_weight),
        nutrition_facts: Object.keys(nutritionFacts).length > 0 ? nutritionFacts : null
      };

      await onSubmit(submitData);
    } catch (error) {
      console.error('Form submission error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="fixed inset-0 bg-black opacity-50"></div>
        
        <div className="relative bg-white rounded-lg max-w-4xl w-full max-h-screen overflow-y-auto">
          {/* 모달 헤더 */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">
              {isEditing ? '제품 수정' : '새 제품 등록'}
            </h2>
            <button
              onClick={onCancel}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          {/* 모달 본문 */}
          <form onSubmit={handleSubmit} className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* 기본 정보 섹션 */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-gray-900 border-b border-gray-200 pb-2">
                  기본 정보
                </h3>

                {/* 제품명 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    제품명 *
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      errors.name ? 'border-red-300' : 'border-gray-300'
                    }`}
                    placeholder="예: 프리미엄 치킨버거"
                  />
                  {errors.name && <p className="text-red-500 text-xs mt-1">{errors.name}</p>}
                </div>

                {/* 제품 코드 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    제품 코드 *
                  </label>
                  <input
                    type="text"
                    name="code"
                    value={formData.code}
                    onChange={handleInputChange}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      errors.code ? 'border-red-300' : 'border-gray-300'
                    }`}
                    placeholder="예: CHK-001"
                  />
                  {errors.code && <p className="text-red-500 text-xs mt-1">{errors.code}</p>}
                </div>

                {/* 버전 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    버전
                  </label>
                  <input
                    type="text"
                    name="version"
                    value={formData.version}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="예: 1.0"
                  />
                </div>

                {/* 제품 설명 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    제품 설명
                  </label>
                  <textarea
                    name="description"
                    value={formData.description}
                    onChange={handleInputChange}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="제품에 대한 상세 설명을 입력하세요"
                  />
                </div>
              </div>

              {/* 제품 사양 섹션 */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-gray-900 border-b border-gray-200 pb-2">
                  제품 사양
                </h3>

                {/* 중량 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    중량 (g) *
                  </label>
                  <input
                    type="number"
                    step="0.001"
                    name="net_weight"
                    value={formData.net_weight}
                    onChange={handleInputChange}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      errors.net_weight ? 'border-red-300' : 'border-gray-300'
                    }`}
                    placeholder="예: 250.5"
                  />
                  {errors.net_weight && <p className="text-red-500 text-xs mt-1">{errors.net_weight}</p>}
                </div>

                {/* 포장형태 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    포장형태 *
                  </label>
                  <input
                    type="text"
                    name="packaging_type"
                    value={formData.packaging_type}
                    onChange={handleInputChange}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      errors.packaging_type ? 'border-red-300' : 'border-gray-300'
                    }`}
                    placeholder="예: 개별포장, 박스포장"
                  />
                  {errors.packaging_type && <p className="text-red-500 text-xs mt-1">{errors.packaging_type}</p>}
                </div>

                {/* 유통기한 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    유통기한 (일) *
                  </label>
                  <input
                    type="number"
                    name="shelf_life_days"
                    value={formData.shelf_life_days}
                    onChange={handleInputChange}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      errors.shelf_life_days ? 'border-red-300' : 'border-gray-300'
                    }`}
                    placeholder="예: 30"
                  />
                  {errors.shelf_life_days && <p className="text-red-500 text-xs mt-1">{errors.shelf_life_days}</p>}
                </div>

                {/* 보관온도 */}
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      최저온도 (°C)
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      name="storage_temp_min"
                      value={formData.storage_temp_min}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="-18"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      최고온도 (°C)
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      name="storage_temp_max"
                      value={formData.storage_temp_max}
                      onChange={handleInputChange}
                      className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                        errors.storage_temp_max ? 'border-red-300' : 'border-gray-300'
                      }`}
                      placeholder="-10"
                    />
                    {errors.storage_temp_max && <p className="text-red-500 text-xs mt-1">{errors.storage_temp_max}</p>}
                  </div>
                </div>
              </div>
            </div>

            {/* 영양성분 및 알러지 정보 섹션 */}
            <div className="mt-6 space-y-4">
              <h3 className="text-lg font-medium text-gray-900 border-b border-gray-200 pb-2">
                영양성분 및 알러지 정보
              </h3>

              {/* 영양성분 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  영양성분 (100g 당)
                </label>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
                  <input
                    type="number"
                    step="0.1"
                    name="calories"
                    value={nutritionFactsJson.calories}
                    onChange={handleNutritionChange}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="칼로리(kcal)"
                  />
                  <input
                    type="number"
                    step="0.1"
                    name="protein"
                    value={nutritionFactsJson.protein}
                    onChange={handleNutritionChange}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="단백질(g)"
                  />
                  <input
                    type="number"
                    step="0.1"
                    name="fat"
                    value={nutritionFactsJson.fat}
                    onChange={handleNutritionChange}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="지방(g)"
                  />
                  <input
                    type="number"
                    step="0.1"
                    name="carbohydrates"
                    value={nutritionFactsJson.carbohydrates}
                    onChange={handleNutritionChange}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="탄수화물(g)"
                  />
                  <input
                    type="number"
                    step="0.1"
                    name="sodium"
                    value={nutritionFactsJson.sodium}
                    onChange={handleNutritionChange}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="나트륨(mg)"
                  />
                </div>
              </div>

              {/* 알러지 정보 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  알러지 정보
                </label>
                <textarea
                  name="allergen_info"
                  value={formData.allergen_info}
                  onChange={handleInputChange}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="예: 밀, 대두, 계란 함유. 견과류를 사용한 제품과 같은 시설에서 제조"
                />
              </div>

              {/* 활성 상태 */}
              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="is_active"
                  checked={formData.is_active}
                  onChange={handleInputChange}
                  className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
                <label className="ml-2 text-sm text-gray-700">
                  활성 제품 (체크 해제 시 비활성화)
                </label>
              </div>
            </div>

            {/* 버튼 그룹 */}
            <div className="mt-8 flex items-center justify-end space-x-3 pt-6 border-t border-gray-200">
              <button
                type="button"
                onClick={onCancel}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                disabled={loading}
              >
                취소
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? '처리 중...' : (isEditing ? '수정' : '등록')}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ProductForm;