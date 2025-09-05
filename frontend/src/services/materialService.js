import apiClient from './apiClient';

class MaterialService {
  // 원자재 목록 조회
  async getMaterials(params = {}) {
    try {
      const response = await apiClient.get('/raw-materials/', { params });
      return response.data;
    } catch (error) {
      console.error('원자재 목록 조회 실패:', error);
      throw error;
    }
  }

  // 특정 원자재 조회
  async getMaterial(id) {
    try {
      const response = await apiClient.get(`/raw-materials/${id}/`);
      return response.data;
    } catch (error) {
      console.error('원자재 조회 실패:', error);
      throw error;
    }
  }

  // 원자재 생성
  async createMaterial(materialData) {
    try {
      const response = await apiClient.post('/raw-materials/', materialData);
      return response.data;
    } catch (error) {
      console.error('원자재 생성 실패:', error);
      throw error;
    }
  }

  // 원자재 수정
  async updateMaterial(id, materialData) {
    try {
      const response = await apiClient.patch(`/raw-materials/${id}/`, materialData);
      return response.data;
    } catch (error) {
      console.error('원자재 수정 실패:', error);
      throw error;
    }
  }

  // 원자재 삭제
  async deleteMaterial(id) {
    try {
      await apiClient.delete(`/raw-materials/${id}/`);
    } catch (error) {
      console.error('원자재 삭제 실패:', error);
      throw error;
    }
  }

  // 원자재 카테고리 목록
  async getMaterialCategories() {
    try {
      const response = await apiClient.get('/raw-materials/categories/');
      return response.data;
    } catch (error) {
      console.error('카테고리 목록 조회 실패:', error);
      throw error;
    }
  }

  // 특정 원자재의 로트 목록
  async getMaterialLots(materialId, params = {}) {
    try {
      const response = await apiClient.get(`/raw-materials/${materialId}/lots/`, { params });
      return response.data;
    } catch (error) {
      console.error('원자재 로트 목록 조회 실패:', error);
      throw error;
    }
  }

  // 특정 원자재의 재고 현황
  async getMaterialInventory(materialId) {
    try {
      const response = await apiClient.get(`/raw-materials/${materialId}/inventory/`);
      return response.data;
    } catch (error) {
      console.error('원자재 재고 현황 조회 실패:', error);
      throw error;
    }
  }

  // 재고 부족 원자재 목록
  async getLowStockMaterials(threshold = 10) {
    try {
      const response = await apiClient.get('/raw-materials/low_stock/', { 
        params: { threshold } 
      });
      return response.data;
    } catch (error) {
      console.error('재고 부족 원자재 목록 조회 실패:', error);
      throw error;
    }
  }

  // ===== Material Lot 관련 =====
  
  // 전체 로트 목록 조회
  async getAllMaterialLots(params = {}) {
    try {
      const response = await apiClient.get('/material-lots/', { params });
      return response.data;
    } catch (error) {
      console.error('전체 로트 목록 조회 실패:', error);
      throw error;
    }
  }

  // 로트 목록 조회 (별칭)
  async getMaterialLotList(params = {}) {
    return this.getAllMaterialLots(params);
  }

  // 로트 생성 (입고 처리)
  async createMaterialLot(lotData) {
    try {
      const response = await apiClient.post('/material-lots/', lotData);
      return response.data;
    } catch (error) {
      console.error('로트 생성 실패:', error);
      throw error;
    }
  }

  // 로트 소비/사용
  async consumeMaterialLot(lotId, consumeData) {
    try {
      const response = await apiClient.post(`/material-lots/${lotId}/consume/`, consumeData);
      return response.data;
    } catch (error) {
      console.error('로트 소비 처리 실패:', error);
      throw error;
    }
  }

  // 로트 삭제
  async deleteMaterialLot(lotId) {
    try {
      const response = await apiClient.delete(`/material-lots/${lotId}/`);
      return response.data;
    } catch (error) {
      console.error('로트 삭제 실패:', error);
      throw error;
    }
  }

  // 로트 추적성 정보
  async getMaterialLotTraceability(lotId) {
    try {
      const response = await apiClient.get(`/material-lots/${lotId}/traceability/`);
      return response.data;
    } catch (error) {
      console.error('로트 추적성 정보 조회 실패:', error);
      throw error;
    }
  }

  // 유통기한 임박 로트 목록
  async getExpiringSoonLots(days = 7) {
    try {
      const response = await apiClient.get('/material-lots/expiring_soon/', {
        params: { days }
      });
      return response.data;
    } catch (error) {
      console.error('유통기한 임박 로트 조회 실패:', error);
      throw error;
    }
  }

  // 유통기한 임박 로트 목록 (별칭)
  async getExpiringLots(days = 7) {
    return this.getExpiringSoonLots(days);
  }

  // 품질검사 요약
  async getQualitySummary() {
    try {
      const response = await apiClient.get('/material-lots/quality_summary/');
      return response.data;
    } catch (error) {
      console.error('품질검사 요약 조회 실패:', error);
      throw error;
    }
  }
}

// 싱글톤 인스턴스 생성 및 내보내기
const materialService = new MaterialService();
export default materialService;