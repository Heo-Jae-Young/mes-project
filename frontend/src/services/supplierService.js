import apiClient from './apiClient';

class SupplierService {
  // 공급업체 목록 조회
  async getSuppliers(params = {}) {
    try {
      const response = await apiClient.get('/suppliers/', { params });
      return response.data;
    } catch (error) {
      console.error('공급업체 목록 조회 실패:', error);
      throw error;
    }
  }

  // 특정 공급업체 조회
  async getSupplier(id) {
    try {
      const response = await apiClient.get(`/suppliers/${id}/`);
      return response.data;
    } catch (error) {
      console.error('공급업체 조회 실패:', error);
      throw error;
    }
  }

  // 공급업체 생성
  async createSupplier(supplierData) {
    try {
      const response = await apiClient.post('/suppliers/', supplierData);
      return response.data;
    } catch (error) {
      console.error('공급업체 생성 실패:', error);
      throw error;
    }
  }

  // 공급업체 수정
  async updateSupplier(id, supplierData) {
    try {
      const response = await apiClient.patch(`/suppliers/${id}/`, supplierData);
      return response.data;
    } catch (error) {
      console.error('공급업체 수정 실패:', error);
      throw error;
    }
  }

  // 공급업체 삭제
  async deleteSupplier(id) {
    try {
      await apiClient.delete(`/suppliers/${id}/`);
    } catch (error) {
      console.error('공급업체 삭제 실패:', error);
      throw error;
    }
  }
}

const supplierService = new SupplierService();
export default supplierService;