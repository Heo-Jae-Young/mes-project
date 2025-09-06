import apiClient from './apiClient';

class ProductService {
  // 제품 목록 조회
  async getProducts(params = {}) {
    try {
      const response = await apiClient.get('/finished-products/', { params });
      return response.data;
    } catch (error) {
      console.error('제품 목록 조회 실패:', error);
      throw error;
    }
  }

  // 특정 제품 조회
  async getProduct(id) {
    try {
      const response = await apiClient.get(`/finished-products/${id}/`);
      return response.data;
    } catch (error) {
      console.error('제품 조회 실패:', error);
      throw error;
    }
  }

  // 제품 생성
  async createProduct(productData) {
    try {
      const response = await apiClient.post('/finished-products/', productData);
      return response.data;
    } catch (error) {
      console.error('제품 생성 실패:', error);
      throw error;
    }
  }

  // 제품 수정
  async updateProduct(id, productData) {
    try {
      const response = await apiClient.patch(`/finished-products/${id}/`, productData);
      return response.data;
    } catch (error) {
      console.error('제품 수정 실패:', error);
      throw error;
    }
  }

  // 제품 삭제
  async deleteProduct(id) {
    try {
      const response = await apiClient.delete(`/finished-products/${id}/`);
      return response.data;
    } catch (error) {
      console.error('제품 삭제 실패:', error);
      throw error;
    }
  }

  // 활성 제품 목록 (간단 버전)
  async getActiveProducts() {
    try {
      const response = await apiClient.get('/finished-products/active_products/');
      return response.data;
    } catch (error) {
      console.error('활성 제품 목록 조회 실패:', error);
      throw error;
    }
  }

  // 제품 카탈로그 (상세 정보 포함)
  async getProductCatalog() {
    try {
      const response = await apiClient.get('/finished-products/product_catalog/');
      return response.data;
    } catch (error) {
      console.error('제품 카탈로그 조회 실패:', error);
      throw error;
    }
  }

  // 제품별 생산 이력
  async getProductionHistory(productId, limit = 20) {
    try {
      const response = await apiClient.get(`/finished-products/${productId}/production_history/`, { 
        params: { limit } 
      });
      return response.data;
    } catch (error) {
      console.error('제품 생산 이력 조회 실패:', error);
      throw error;
    }
  }

  // 제품별 생산 통계
  async getProductionStatistics(productId) {
    try {
      const response = await apiClient.get(`/finished-products/${productId}/production_statistics/`);
      return response.data;
    } catch (error) {
      console.error('제품 생산 통계 조회 실패:', error);
      throw error;
    }
  }

  // 제품별 CCP 목록
  async getProductCCPs(productId) {
    try {
      const response = await apiClient.get(`/finished-products/${productId}/ccps/`);
      return response.data;
    } catch (error) {
      console.error('제품 CCP 목록 조회 실패:', error);
      throw error;
    }
  }

  // 제품 원가 계산
  async getProductCost(productId, quantity = 1) {
    try {
      const response = await apiClient.get(`/products/${productId}/cost/`, {
        params: { quantity }
      });
      return response.data;
    } catch (error) {
      console.error('제품 원가 조회 실패:', error);
      throw error;
    }
  }

  // 전체 제품 원가 요약
  async getProductsCostSummary() {
    try {
      const response = await apiClient.get('/products/cost-summary/');
      return response.data;
    } catch (error) {
      console.error('제품 원가 요약 조회 실패:', error);
      throw error;
    }
  }
}

const productService = new ProductService();
export default productService;