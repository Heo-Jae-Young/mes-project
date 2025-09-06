import React from 'react';
import { 
  XMarkIcon, 
  QuestionMarkCircleIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  ChartBarIcon,
  ClockIcon,
  CurrencyDollarIcon
} from '@heroicons/react/24/outline';

const CostCalculationGuide = ({ onClose }) => {
  const methodsData = [
    {
      method: 'current_lot',
      title: '현재 재고 기준',
      description: 'FIFO 방식으로 현재 보유 재고의 가중평균 단가',
      icon: CheckCircleIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      accuracy: '매우 높음',
      details: [
        '품질검사를 통과한 현재 재고만 사용',
        '유통기한 순서로 FIFO(선입선출) 방식 적용',
        '실제 생산에 사용될 재고의 정확한 가격',
        '로트별 단가를 수량 가중평균으로 계산'
      ],
      example: {
        scenario: '밀가루 10kg 필요시',
        calculation: [
          '로트A: 5kg × ₩2,000/kg = ₩10,000',
          '로트B: 5kg × ₩2,200/kg = ₩11,000',
          '총 비용: ₩21,000 / 10kg = ₩2,100/kg'
        ]
      }
    },
    {
      method: 'recent_average',
      title: '최근 30일 평균',
      description: '재고 부족 시 최근 30일 입고 평균 단가 사용',
      icon: InformationCircleIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      accuracy: '높음',
      details: [
        '현재 재고가 부족하거나 없을 때 적용',
        '최근 30일간 입고된 로트들의 평균 단가',
        '시장 가격 변동을 어느 정도 반영',
        '추정 원가이므로 실제와 차이 발생 가능'
      ],
      example: {
        scenario: '최근 30일 설탕 입고 이력',
        calculation: [
          '1주차: ₩1,800/kg × 2회 입고',
          '3주차: ₩1,900/kg × 1회 입고',
          '평균: ₩1,833/kg로 계산'
        ]
      }
    },
    {
      method: 'historical_average',
      title: '전체 평균',
      description: '전체 입고 이력의 평균 단가 (최근 입고가 없을 때)',
      icon: ChartBarIcon,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      borderColor: 'border-orange-200',
      accuracy: '보통',
      details: [
        '최근 30일 입고 이력이 없을 때 적용',
        '모든 과거 입고 기록의 전체 평균',
        '오래된 가격이 포함되어 정확도가 낮을 수 있음',
        '참고용으로만 사용 권장'
      ],
      example: {
        scenario: '6개월간 올리브오일 전체 평균',
        calculation: [
          '1-2월: ₩15,000/L (유가 상승기)',
          '3-6월: ₩12,000/L (정상기)',
          '전체 평균: ₩13,500/L'
        ]
      }
    },
    {
      method: 'no_data',
      title: '데이터 없음',
      description: '해당 원자재의 가격 정보를 찾을 수 없음',
      icon: ExclamationTriangleIcon,
      color: 'text-gray-600',
      bgColor: 'bg-gray-50',
      borderColor: 'border-gray-200',
      accuracy: '계산 불가',
      details: [
        '해당 원자재의 입고 이력이 전혀 없음',
        '원가 계산이 불가능한 상태',
        '원자재 입고 후 다시 계산 가능',
        '공급업체에서 단가 정보 확인 필요'
      ],
      example: {
        scenario: '신규 원자재 추가',
        calculation: [
          '새로 추가된 향신료',
          '아직 입고 이력 없음',
          '단가 ₩0으로 표시'
        ]
      }
    }
  ];

  const getMethodIcon = (method) => {
    const methodData = methodsData.find(m => m.method === method);
    if (!methodData) return null;
    
    const IconComponent = methodData.icon;
    return (
      <IconComponent className={`w-5 h-5 ${methodData.color}`} />
    );
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-10 mx-auto p-5 border w-11/12 max-w-6xl shadow-lg rounded-md bg-white">
        {/* 헤더 */}
        <div className="flex justify-between items-center pb-4 border-b border-gray-200">
          <div className="flex items-center">
            <QuestionMarkCircleIcon className="h-6 w-6 text-blue-600 mr-2" />
            <div>
              <h3 className="text-lg font-medium text-gray-900">
                제품 원가 계산 방법 안내
              </h3>
              <p className="text-sm text-gray-500">
                HACCP 추적성을 기반으로 한 정확한 원가 계산 시스템
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        <div className="mt-6">
          {/* 개요 */}
          <div className="bg-blue-50 rounded-lg p-4 mb-6">
            <div className="flex items-center mb-2">
              <CurrencyDollarIcon className="h-5 w-5 text-blue-600 mr-2" />
              <h4 className="text-sm font-medium text-blue-900">계산 원리</h4>
            </div>
            <p className="text-sm text-blue-800 leading-relaxed">
              제품 원가는 <strong>BOM(자재명세서)</strong>에 정의된 원자재별 소요량과 
              각 원자재의 <strong>현재 단가</strong>를 곱하여 계산됩니다. 
              원자재 단가는 재고 상황과 입고 이력에 따라 다음 우선순위로 결정됩니다.
            </p>
          </div>

          {/* 계산 방법별 상세 설명 */}
          <div className="space-y-6">
            {methodsData.map((method, index) => {
              const IconComponent = method.icon;
              return (
                <div key={method.method} className={`border rounded-lg p-6 ${method.borderColor}`}>
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center">
                      <div className={`p-2 rounded-lg ${method.bgColor} mr-3`}>
                        <IconComponent className={`w-6 h-6 ${method.color}`} />
                      </div>
                      <div>
                        <h4 className="text-lg font-medium text-gray-900 flex items-center">
                          {index + 1}. {method.title}
                          <span className={`ml-3 px-2 py-1 text-xs font-medium rounded-full ${method.bgColor} ${method.color}`}>
                            정확도: {method.accuracy}
                          </span>
                        </h4>
                        <p className="text-sm text-gray-600 mt-1">{method.description}</p>
                      </div>
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-6">
                    {/* 상세 설명 */}
                    <div>
                      <h5 className="text-sm font-medium text-gray-900 mb-3">상세 내용</h5>
                      <ul className="space-y-2">
                        {method.details.map((detail, idx) => (
                          <li key={idx} className="flex items-start text-sm text-gray-700">
                            <span className={`w-1.5 h-1.5 rounded-full ${method.color.replace('text-', 'bg-')} mt-2 mr-3 flex-shrink-0`}></span>
                            {detail}
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* 계산 예시 */}
                    <div>
                      <h5 className="text-sm font-medium text-gray-900 mb-3">계산 예시</h5>
                      <div className="bg-gray-50 rounded-md p-3">
                        <p className="text-xs font-medium text-gray-600 mb-2">{method.example.scenario}</p>
                        <div className="space-y-1">
                          {method.example.calculation.map((calc, idx) => (
                            <div key={idx} className="text-xs text-gray-700 font-mono">
                              {calc}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* 추가 정보 */}
          <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-center mb-2">
              <ClockIcon className="h-5 w-5 text-yellow-600 mr-2" />
              <h4 className="text-sm font-medium text-yellow-800">실시간 업데이트</h4>
            </div>
            <p className="text-sm text-yellow-700">
              원자재 입고, 재고 소모, 품질검사 결과에 따라 원가가 실시간으로 업데이트됩니다. 
              더 정확한 원가 계산을 위해 정기적인 재고 관리와 BOM 업데이트를 권장합니다.
            </p>
          </div>
        </div>

        {/* 닫기 버튼 */}
        <div className="mt-6 flex justify-end border-t border-gray-200 pt-4">
          <button
            onClick={onClose}
            className="bg-gray-100 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-200 transition-colors"
          >
            확인
          </button>
        </div>
      </div>
    </div>
  );
};

export default CostCalculationGuide;