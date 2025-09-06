import apiClient from './apiClient';

class BOMService {
  // BOM 목록 조회
  async getBOMs(params = {}) {
    try {
      const response = await apiClient.get('/bom/', { params });
      return response.data;
    } catch (error) {
      console.error('BOM 목록 조회 실패:', error);
      throw error;
    }
  }

  // 특정 BOM 조회
  async getBOM(id) {
    try {
      const response = await apiClient.get(`/bom/${id}/`);
      return response.data;
    } catch (error) {
      console.error('BOM 조회 실패:', error);
      throw error;
    }
  }

  // BOM 생성
  async createBOM(bomData) {
    try {
      const response = await apiClient.post('/bom/', bomData);
      return response.data;
    } catch (error) {
      console.error('BOM 생성 실패:', error);
      throw error;
    }
  }

  // BOM 수정
  async updateBOM(id, bomData) {
    try {
      const response = await apiClient.patch(`/bom/${id}/`, bomData);
      return response.data;
    } catch (error) {
      console.error('BOM 수정 실패:', error);
      throw error;
    }
  }

  // BOM 삭제
  async deleteBOM(id) {
    try {
      const response = await apiClient.delete(`/bom/${id}/`);
      return response.data;
    } catch (error) {
      console.error('BOM 삭제 실패:', error);
      throw error;
    }
  }

  // 제품별 BOM 목록 조회
  async getBOMByProduct(productId, productionQuantity = 1) {
    try {
      const response = await apiClient.get(`/bom/by_product/`, {
        params: { 
          product_id: productId,
          production_quantity: productionQuantity
        }
      });
      return response.data;
    } catch (error) {
      console.error('제품별 BOM 목록 조회 실패:', error);
      throw error;
    }
  }

  // 원자재 소요량 계산
  async calculateRequirements(productId, productionQuantity) {
    try {
      const response = await apiClient.get(`/bom/calculate_requirements/`, {
        params: { 
          product_id: productId,
          production_quantity: productionQuantity
        }
      });
      return response.data;
    } catch (error) {
      console.error('원자재 소요량 계산 실패:', error);
      throw error;
    }
  }

  // BOM 일괄 등록
  async bulkCreateBOM(productId, bomItems) {
    try {
      const response = await apiClient.post(`/bom/bulk_create/`, {
        product_id: productId,
        bom_items: bomItems
      });
      return response.data;
    } catch (error) {
      console.error('BOM 일괄 등록 실패:', error);
      throw error;
    }
  }
}

const bomService = new BOMService();
export default bomService;