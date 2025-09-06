import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';

/**
 * 엔티티 페이지 공통 로직을 관리하는 Custom Hook
 * 
 * @param {Object} service - API 서비스 객체 또는 서비스 어댑터
 * @param {string} entityName - 엔티티 이름 (에러 메시지에 사용)
 * @param {Object} options - 추가 옵션
 * @param {Object} options.initialFilters - 초기 필터 값
 * @param {Function} options.transformData - 데이터 변환 함수
 * @param {boolean} options.autoFetch - 컴포넌트 마운트 시 자동 fetch 여부 (기본값: true)
 * 
 * @returns {Object} 엔티티 페이지에 필요한 상태와 핸들러들
 */
const useEntityPage = (service, entityName, options = {}) => {
  const {
    initialFilters = {},
    transformData = (data) => data.results || data,
    autoFetch = true
  } = options;

  // 공통 상태 관리
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [filters, setFilters] = useState(initialFilters);

  // 목록 조회
  const fetchItems = async () => {
    try {
      setLoading(true);
      const data = await service.getAll(filters);
      const transformedData = transformData(data);
      setItems(transformedData);
    } catch (error) {
      toast.error(`${entityName} 목록을 불러오는데 실패했습니다`);
      console.error(`${entityName} fetch error:`, error);
    } finally {
      setLoading(false);
    }
  };

  // 아이템 생성
  const handleCreate = async (itemData) => {
    try {
      await service.create(itemData);
      toast.success(`${entityName}이(가) 등록되었습니다.`);
      setShowForm(false);
      fetchItems();
    } catch (error) {
      console.error(`${entityName} 생성 실패:`, error);
      if (error.response?.data) {
        const errorMessages = Object.values(error.response.data).flat();
        toast.error(`등록 실패: ${errorMessages.join(', ')}`);
      } else {
        toast.error(`${entityName} 등록에 실패했습니다.`);
      }
    }
  };

  // 아이템 수정
  const handleUpdate = async (id, itemData) => {
    try {
      await service.update(id, itemData);
      toast.success(`${entityName} 정보가 수정되었습니다.`);
      setEditingItem(null);
      setShowForm(false);
      fetchItems();
    } catch (error) {
      console.error(`${entityName} 수정 실패:`, error);
      if (error.response?.data) {
        const errorMessages = Object.values(error.response.data).flat();
        toast.error(`수정 실패: ${errorMessages.join(', ')}`);
      } else {
        toast.error(`${entityName} 수정에 실패했습니다.`);
      }
    }
  };

  // 아이템 삭제
  const handleDelete = async (id) => {
    if (!window.confirm(`정말로 이 ${entityName}을(를) 삭제하시겠습니까?\n삭제된 데이터는 복구할 수 없습니다.`)) {
      return;
    }

    try {
      await service.delete(id);
      toast.success(`${entityName}이(가) 삭제되었습니다.`);
      fetchItems();
    } catch (error) {
      console.error(`${entityName} 삭제 실패:`, error);
      if (error.response?.status === 400) {
        toast.error(`사용 중인 ${entityName}은(는) 삭제할 수 없습니다.`);
      } else {
        toast.error(`${entityName} 삭제에 실패했습니다.`);
      }
    }
  };

  // 수정 모드 활성화
  const handleEdit = (item) => {
    setEditingItem(item);
    setShowForm(true);
  };

  // 폼 닫기
  const handleFormClose = () => {
    setShowForm(false);
    setEditingItem(null);
  };

  // 필터 변경
  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  // 필터가 변경될 때마다 데이터 재조회
  useEffect(() => {
    if (autoFetch) {
      fetchItems();
    }
  }, [filters]);

  // 컴포넌트 마운트 시 초기 데이터 로드 (필터가 없을 때)
  useEffect(() => {
    if (autoFetch && Object.keys(filters).length === 0) {
      fetchItems();
    }
  }, []);

  return {
    // 상태
    items,
    loading,
    showForm,
    editingItem,
    filters,
    
    // 액션
    fetchItems,
    handleCreate,
    handleUpdate,
    handleDelete,
    handleEdit,
    handleFormClose,
    handleFilterChange,
    
    // 상태 변경 함수 (필요한 경우 직접 접근)
    setItems,
    setLoading,
    setShowForm,
    setEditingItem,
    setFilters
  };
};

/**
 * 서비스 객체를 useEntityPage 훅과 호환되는 형태로 변환하는 어댑터
 */
export const createServiceAdapter = (originalService, methodMap = {}) => {
  const defaultMap = {
    getAll: 'getMaterials',    // 또는 'getProducts', 'getSuppliers' 등
    create: 'createMaterial',   // 또는 'createProduct', 'createSupplier' 등
    update: 'updateMaterial',   // 또는 'updateProduct', 'updateSupplier' 등
    delete: 'deleteMaterial'    // 또는 'deleteProduct', 'deleteSupplier' 등
  };

  const finalMap = { ...defaultMap, ...methodMap };

  const adapter = {
    getAll: (filters) => originalService[finalMap.getAll](filters),
    create: (data) => originalService[finalMap.create](data),
    update: (id, data) => originalService[finalMap.update](id, data)
  };

  // 삭제 기능이 있는 경우에만 추가
  if (finalMap.delete && originalService[finalMap.delete]) {
    adapter.delete = (id) => originalService[finalMap.delete](id);
  }

  return adapter;
};

export default useEntityPage;