import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import ccpService from '../../services/ccpService';

const CCPLogForm = ({ onSubmitSuccess, preselectedCCP = null }) => {
  const [formData, setFormData] = useState({
    ccp: preselectedCCP?.id || '',
    measured_value: '',
    unit: '',
    measured_at: new Date().toISOString().slice(0, 16), // YYYY-MM-DDTHH:MM
    deviation_notes: '',
    measurement_device: '',
    environmental_conditions: ''
  });

  const [ccps, setCcps] = useState([]);
  const [selectedCCP, setSelectedCCP] = useState(preselectedCCP);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // CCP 목록 조회
  useEffect(() => {
    const loadCCPs = async () => {
      try {
        setLoading(true);
        const response = await ccpService.getCCPs({ is_active: true });
        setCcps(response.results || []);
      } catch (error) {
        console.error('CCP 목록 조회 실패:', error);
        toast.error('CCP 목록을 불러오는 중 오류가 발생했습니다.');
      } finally {
        setLoading(false);
      }
    };

    if (!preselectedCCP) {
      loadCCPs();
    }
  }, [preselectedCCP]);

  // CCP 선택 시 단위 자동 설정
  const handleCCPChange = (ccpId) => {
    const selected = ccps.find(ccp => ccp.id === ccpId);
    setSelectedCCP(selected);
    
    if (selected) {
      // CCP 타입에 따른 기본 단위 설정
      const defaultUnits = {
        'temperature': '°C',
        'ph': 'pH',
        'time': '분',
        'pressure': 'bar',
        'weight': 'kg',
        'visual': '판정',
        'metal_detection': '판정'
      };
      
      setFormData(prev => ({
        ...prev,
        ccp: ccpId,
        unit: defaultUnits[selected.ccp_type] || ''
      }));
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.ccp) {
      toast.error('CCP를 선택해주세요.');
      return;
    }

    if (!formData.measured_value) {
      toast.error('측정값을 입력해주세요.');
      return;
    }

    if (!formData.unit) {
      toast.error('단위를 입력해주세요.');
      return;
    }

    try {
      setSubmitting(true);
      
      const submitData = {
        ccp_id: formData.ccp,
        measured_value: parseFloat(formData.measured_value),
        unit: formData.unit.trim(),
        measured_at: new Date(formData.measured_at).toISOString(),
      };

      // 빈 문자열이 아닌 경우에만 추가
      if (formData.deviation_notes.trim()) {
        submitData.deviation_notes = formData.deviation_notes.trim();
      }
      if (formData.measurement_device.trim()) {
        submitData.measurement_device = formData.measurement_device.trim();
      }
      if (formData.environmental_conditions.trim()) {
        submitData.environmental_conditions = formData.environmental_conditions.trim();
      }

      console.log('Submitting CCP Log data:', submitData);
      await ccpService.createCCPLog(submitData);
      
      toast.success('CCP 로그가 성공적으로 저장되었습니다.');
      
      // 폼 초기화
      setFormData({
        ccp: preselectedCCP?.id || '',
        measured_value: '',
        unit: selectedCCP ? formData.unit : '', // 단위는 유지
        measured_at: new Date().toISOString().slice(0, 16),
        deviation_notes: '',
        measurement_device: '',
        environmental_conditions: ''
      });

      if (onSubmitSuccess) {
        onSubmitSuccess();
      }

    } catch (error) {
      console.error('CCP 로그 저장 실패:', error);
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message ||
                          'CCP 로그 저장 중 오류가 발생했습니다.';
      toast.error(errorMessage);
    } finally {
      setSubmitting(false);
    }
  };

  const getCriticalLimitDisplay = () => {
    if (!selectedCCP) return null;
    
    const { critical_limit_min, critical_limit_max } = selectedCCP;
    
    if (critical_limit_min && critical_limit_max) {
      return `${critical_limit_min} ~ ${critical_limit_max} ${formData.unit}`;
    } else if (critical_limit_min) {
      return `최소: ${critical_limit_min} ${formData.unit}`;
    } else if (critical_limit_max) {
      return `최대: ${critical_limit_max} ${formData.unit}`;
    }
    return '설정되지 않음';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-lg font-semibold mb-4">CCP 모니터링 로그 입력</h3>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* CCP 선택 */}
        {!preselectedCCP && (
          <div>
            <label htmlFor="ccp" className="block text-sm font-medium text-gray-700 mb-1">
              CCP 선택 *
            </label>
            <select
              id="ccp"
              name="ccp"
              value={formData.ccp}
              onChange={(e) => handleCCPChange(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">CCP를 선택하세요</option>
              {ccps.map(ccp => (
                <option key={ccp.id} value={ccp.id}>
                  {ccp.name} ({ccp.code}) - {ccp.process_step}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* 선택된 CCP 정보 표시 */}
        {selectedCCP && (
          <div className="bg-gray-50 p-4 rounded-md">
            <h4 className="font-medium text-gray-900">{selectedCCP.name}</h4>
            <p className="text-sm text-gray-600">공정: {selectedCCP.process_step}</p>
            <p className="text-sm text-gray-600">타입: {selectedCCP.ccp_type}</p>
            <p className="text-sm text-gray-600">한계기준: {getCriticalLimitDisplay()}</p>
          </div>
        )}

        {/* 측정값과 단위 */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="measured_value" className="block text-sm font-medium text-gray-700 mb-1">
              측정값 *
            </label>
            <input
              type="number"
              step="0.001"
              id="measured_value"
              name="measured_value"
              value={formData.measured_value}
              onChange={handleInputChange}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          <div>
            <label htmlFor="unit" className="block text-sm font-medium text-gray-700 mb-1">
              단위 *
            </label>
            <input
              type="text"
              id="unit"
              name="unit"
              value={formData.unit}
              onChange={handleInputChange}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
        </div>

        {/* 측정 시간 */}
        <div>
          <label htmlFor="measured_at" className="block text-sm font-medium text-gray-700 mb-1">
            측정 시간 *
          </label>
          <input
            type="datetime-local"
            id="measured_at"
            name="measured_at"
            value={formData.measured_at}
            onChange={handleInputChange}
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        {/* 측정 장비 */}
        <div>
          <label htmlFor="measurement_device" className="block text-sm font-medium text-gray-700 mb-1">
            측정 장비
          </label>
          <input
            type="text"
            id="measurement_device"
            name="measurement_device"
            value={formData.measurement_device}
            onChange={handleInputChange}
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="예: 온도계 TH-101"
          />
        </div>

        {/* 환경 조건 */}
        <div>
          <label htmlFor="environmental_conditions" className="block text-sm font-medium text-gray-700 mb-1">
            환경 조건
          </label>
          <textarea
            id="environmental_conditions"
            name="environmental_conditions"
            value={formData.environmental_conditions}
            onChange={handleInputChange}
            rows={2}
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="예: 실온 25°C, 습도 60%"
          />
        </div>

        {/* 이탈 시 비고사항 */}
        <div>
          <label htmlFor="deviation_notes" className="block text-sm font-medium text-gray-700 mb-1">
            이탈 시 비고사항
          </label>
          <textarea
            id="deviation_notes"
            name="deviation_notes"
            value={formData.deviation_notes}
            onChange={handleInputChange}
            rows={3}
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="기준 이탈 시 상황 설명"
          />
        </div>

        {/* 제출 버튼 */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={submitting}
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? '저장 중...' : 'CCP 로그 저장'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CCPLogForm;