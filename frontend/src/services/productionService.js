import apiClient from './apiClient';

class ProductionService {
  // 제품 목록 조회 (생산 주문 폼용)
  async getFinishedProducts() {
    try {
      const response = await apiClient.get('/finished-products/');
      return response.data;
    } catch (error) {
      console.error('제품 목록 조회 실패:', error);
      throw error;
    }
  }
  // 생산 주문 목록 조회
  async getProductionOrders(params = {}) {
    try {
      const response = await apiClient.get('/production-orders/', { params });
      return response.data;
    } catch (error) {
      console.error('생산 주문 목록 조회 실패:', error);
      throw error;
    }
  }

  // 특정 생산 주문 조회
  async getProductionOrder(id) {
    try {
      const response = await apiClient.get(`/production-orders/${id}/`);
      return response.data;
    } catch (error) {
      console.error('생산 주문 조회 실패:', error);
      throw error;
    }
  }

  // 생산 주문 생성
  async createProductionOrder(orderData) {
    try {
      const response = await apiClient.post('/production-orders/', orderData);
      return response.data;
    } catch (error) {
      console.error('생산 주문 생성 실패:', error);
      throw error;
    }
  }

  // 생산 주문 수정
  async updateProductionOrder(id, orderData) {
    try {
      const response = await apiClient.patch(`/production-orders/${id}/`, orderData);
      return response.data;
    } catch (error) {
      console.error('생산 주문 수정 실패:', error);
      throw error;
    }
  }

  // 생산 시작
  async startProduction(orderId) {
    try {
      const response = await apiClient.post(`/production-orders/${orderId}/start_production/`);
      return response.data;
    } catch (error) {
      console.error('생산 시작 실패:', error.response?.data);
      throw error;
    }
  }

  // 생산 완료
  async completeProduction(orderId, data) {
    try {
      const response = await apiClient.post(`/production-orders/${orderId}/complete_production/`, data);
      return response.data;
    } catch (error) {
      console.error('생산 완료 실패:', error.response?.data);
      throw error;
    }
  }

  // 생산 일시정지
  async pauseProduction(orderId, reason) {
    try {
      const response = await apiClient.post(`/production-orders/${orderId}/pause_production/`, {
        reason
      });
      return response.data;
    } catch (error) {
      console.error('생산 일시정지 실패:', error);
      throw error;
    }
  }

  // 생산 재개
  async resumeProduction(orderId) {
    try {
      const response = await apiClient.post(`/production-orders/${orderId}/resume_production/`);
      return response.data;
    } catch (error) {
      console.error('생산 재개 실패:', error);
      throw error;
    }
  }

  // 생산 대시보드 데이터
  async getProductionDashboard() {
    try {
      const response = await apiClient.get('/production-orders/dashboard/');
      return response.data;
    } catch (error) {
      console.error('생산 대시보드 데이터 조회 실패:', error);
      throw error;
    }
  }

  // 예정된 생산 주문
  async getUpcomingOrders(days = 7) {
    try {
      const response = await apiClient.get('/production-orders/upcoming/', {
        params: { days }
      });
      return response.data;
    } catch (error) {
      console.error('예정된 생산 주문 조회 실패:', error);
      throw error;
    }
  }

  // 생산 성과 분석
  async getProductionPerformance() {
    try {
      const response = await apiClient.get('/production-orders/performance/');
      return response.data;
    } catch (error) {
      console.error('생산 성과 분석 조회 실패:', error);
      throw error;
    }
  }

  // 생산 주문의 CCP 로그
  async getProductionCCPLogs(orderId) {
    try {
      const response = await apiClient.get(`/production-orders/${orderId}/ccp_logs/`);
      return response.data;
    } catch (error) {
      console.error('생산 주문 CCP 로그 조회 실패:', error);
      throw error;
    }
  }
}

export default new ProductionService();