import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { XMarkIcon, PlusIcon, TrashIcon } from '@heroicons/react/24/outline';
import bomService from '../../services/bomService';
import materialService from '../../services/materialService';
import LoadingSpinner from '../common/LoadingSpinner';

const ProductBOMManager = ({ product, onClose }) => {
  const [bomItems, setBomItems] = useState([]);
  const [availableMaterials, setAvailableMaterials] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [newItem, setNewItem] = useState({
    raw_material: '',
    quantity_per_unit: '',
    unit: '',
    notes: ''
  });

  // BOM 데이터 로드
  const fetchBOMData = async () => {
    try {
      setLoading(true);
      
      // 병렬로 BOM 목록과 원자재 목록 조회
      const [bomData, materialsData] = await Promise.all([
        bomService.getBOMByProduct(product.id),
        materialService.getMaterials({ is_active: true })
      ]);
      
      setBomItems(bomData.bom_items || []);
      setAvailableMaterials(materialsData.results || materialsData || []);
    } catch (error) {
      toast.error('BOM 데이터를 불러오는데 실패했습니다');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (product?.id) {
      fetchBOMData();
    }
  }, [product]);

  // 새 BOM 아이템 추가
  const handleAddItem = async () => {
    if (!newItem.raw_material || !newItem.quantity_per_unit) {
      toast.error('원자재와 소요량을 입력해주세요');
      return;
    }

    try {
      setSaving(true);
      
      await bomService.createBOM({
        finished_product: product.id,
        raw_material: newItem.raw_material,
        quantity_per_unit: parseFloat(newItem.quantity_per_unit),
        unit: newItem.unit || 'kg',
        notes: newItem.notes,
        is_active: true
      });

      toast.success('BOM 아이템이 추가되었습니다');
      setNewItem({
        raw_material: '',
        quantity_per_unit: '',
        unit: '',
        notes: ''
      });
      fetchBOMData();
    } catch (error) {
      const errorMessage = error.response?.data?.raw_material?.[0] || 
                          error.response?.data?.non_field_errors?.[0] || 
                          'BOM 아이템 추가에 실패했습니다';
      toast.error(errorMessage);
    } finally {
      setSaving(false);
    }
  };

  // BOM 아이템 수정
  const handleUpdateItem = async (itemId, updatedData) => {
    try {
      setSaving(true);
      
      await bomService.updateBOM(itemId, {
        quantity_per_unit: parseFloat(updatedData.quantity_per_unit),
        unit: updatedData.unit,
        notes: updatedData.notes,
        is_active: updatedData.is_active
      });

      toast.success('BOM 아이템이 수정되었습니다');
      setEditingItem(null);
      fetchBOMData();
    } catch (error) {
      toast.error('BOM 아이템 수정에 실패했습니다');
    } finally {
      setSaving(false);
    }
  };

  // BOM 아이템 삭제
  const handleDeleteItem = async (itemId) => {
    if (!window.confirm('이 BOM 아이템을 삭제하시겠습니까?')) {
      return;
    }

    try {
      setSaving(true);
      await bomService.deleteBOM(itemId);
      toast.success('BOM 아이템이 삭제되었습니다');
      fetchBOMData();
    } catch (error) {
      console.error('BOM 삭제 에러:', error.response?.data);
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.non_field_errors?.[0] ||
                          error.response?.data?.message ||
                          'BOM 아이템 삭제에 실패했습니다';
      toast.error(errorMessage);
    } finally {
      setSaving(false);
    }
  };


  if (loading) {
    return (
      <div className="fixed inset-0 z-50 overflow-y-auto">
        <div className="flex items-center justify-center min-h-screen px-4">
          <div className="fixed inset-0 bg-black opacity-50"></div>
          <div className="relative bg-white rounded-lg max-w-4xl w-full p-8">
            <LoadingSpinner />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="fixed inset-0 bg-black opacity-50"></div>
        
        <div className="relative bg-white rounded-lg max-w-6xl w-full max-h-screen overflow-y-auto">
          {/* 모달 헤더 */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                BOM 관리: {product.name}
              </h2>
              <p className="text-sm text-gray-500">
                제품코드: {product.code} | 버전: v{product.version}
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          <div className="p-6">
            {/* 새 BOM 아이템 추가 폼 */}
            <div className="bg-gray-50 rounded-lg p-4 mb-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">새 원자재 추가</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    원자재 *
                  </label>
                  <select
                    value={newItem.raw_material}
                    onChange={(e) => setNewItem(prev => ({ ...prev, raw_material: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">원자재 선택</option>
                    {availableMaterials
                      .filter(material => !bomItems.some(bom => bom.raw_material_name === material.name))
                      .map(material => (
                        <option key={material.id} value={material.id}>
                          {material.name} ({material.code})
                        </option>
                      ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    단위당 소요량 *
                  </label>
                  <input
                    type="number"
                    step="0.001"
                    value={newItem.quantity_per_unit}
                    onChange={(e) => setNewItem(prev => ({ ...prev, quantity_per_unit: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="0.000"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    단위
                  </label>
                  <input
                    type="text"
                    value={newItem.unit}
                    onChange={(e) => setNewItem(prev => ({ ...prev, unit: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="kg, L, 개 등"
                  />
                </div>

                <div className="flex items-end">
                  <button
                    onClick={handleAddItem}
                    disabled={saving || !newItem.raw_material || !newItem.quantity_per_unit}
                    className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
                  >
                    <PlusIcon className="h-4 w-4 mr-1" />
                    추가
                  </button>
                </div>
              </div>

              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  비고
                </label>
                <input
                  type="text"
                  value={newItem.notes}
                  onChange={(e) => setNewItem(prev => ({ ...prev, notes: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="추가 정보나 주의사항"
                />
              </div>
            </div>

            {/* BOM 목록 */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                현재 BOM ({bomItems.length}개)
              </h3>
              
              {bomItems.length === 0 ? (
                <div className="bg-white border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                  <div className="text-gray-500">등록된 BOM이 없습니다</div>
                  <div className="text-gray-400 text-sm mt-1">위의 폼을 사용해 원자재를 추가해보세요</div>
                </div>
              ) : (
                <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          원자재
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          단위당 소요량
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          단위
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          비고
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          상태
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          작업
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {bomItems.map((item) => (
                        <tr key={item.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div>
                              <div className="text-sm font-medium text-gray-900">
                                {item.raw_material_name}
                              </div>
                              <div className="text-sm text-gray-500">
                                {item.raw_material_code} | {item.raw_material_category}
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {parseFloat(item.quantity_per_unit).toLocaleString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {item.unit}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {item.notes || '-'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              item.is_active 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {item.is_active ? '활성' : '비활성'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <button
                              onClick={() => handleDeleteItem(item.id)}
                              disabled={saving}
                              className="text-red-600 hover:text-red-900 p-1 rounded-full hover:bg-red-50 transition-colors disabled:opacity-50"
                              title="삭제"
                            >
                              <TrashIcon className="h-4 w-4" />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>

          {/* 모달 푸터 */}
          <div className="border-t border-gray-200 px-6 py-4 bg-gray-50">
            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-600">
                총 {bomItems.length}개의 원자재가 등록되어 있습니다
              </div>
              <button
                onClick={onClose}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                닫기
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductBOMManager;