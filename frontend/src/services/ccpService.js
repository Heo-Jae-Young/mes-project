import apiClient from './apiClient';

const ccpService = {
  // CCP 목록 조회
  getCCPs: async (params = {}) => {
    const response = await apiClient.get('/ccps/', { params });
    return response.data;
  },

  // 특정 CCP 상세 조회
  getCCP: async (id) => {
    const response = await apiClient.get(`/ccps/${id}/`);
    return response.data;
  },

  // CCP 로그 생성
  createCCPLog: async (logData) => {
    const response = await apiClient.post('/ccp-logs/', logData);
    return response.data;
  },

  // CCP 로그 목록 조회
  getCCPLogs: async (params = {}) => {
    const response = await apiClient.get('/ccp-logs/', { params });
    return response.data;
  },

  // 특정 CCP의 모니터링 로그 조회
  getCCPMonitoringLogs: async (ccpId, params = {}) => {
    const response = await apiClient.get(`/ccps/${ccpId}/monitoring_logs/`, { params });
    return response.data;
  },

  // 최근 위반 로그 조회
  getRecentViolations: async (hours = 24) => {
    const response = await apiClient.get('/ccp-logs/recent_violations/', { 
      params: { hours } 
    });
    return response.data;
  },

  // 개선조치 필요 로그 조회
  getPendingActions: async () => {
    const response = await apiClient.get('/ccp-logs/pending_actions/');
    return response.data;
  },

  // CCP 로그 수정 (개선조치 정보만 수정 가능)
  updateCCPLog: async (id, updateData) => {
    const response = await apiClient.patch(`/ccp-logs/${id}/`, updateData);
    return response.data;
  },

  // CCP 타입 목록 조회
  getCCPTypes: async () => {
    const response = await apiClient.get('/ccps/types/');
    return response.data;
  },

  // 중요 알림 조회
  getCriticalAlerts: async (hours = 24) => {
    const response = await apiClient.get('/ccps/critical_alerts/', { 
      params: { hours } 
    });
    return response.data;
  }
};

export default ccpService;