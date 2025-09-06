import { 
  ExclamationTriangleIcon,
  XMarkIcon,
  ClipboardDocumentListIcon
} from '@heroicons/react/24/outline';

const BOMAlert = ({ products, onManageBOM, onDismiss }) => {
  // BOM이 설정되지 않은 제품들만 필터링
  const productsWithoutBOM = products.filter(product => !product.has_bom && product.is_active);

  // BOM 미설정 제품이 없으면 알림을 표시하지 않음
  if (productsWithoutBOM.length === 0) {
    return null;
  }

  return (
    <div className="bg-orange-50 border-l-4 border-orange-400 p-4 mb-6 rounded-r-lg">
      <div className="flex">
        <div className="flex-shrink-0">
          <ExclamationTriangleIcon className="h-5 w-5 text-orange-400" />
        </div>
        <div className="ml-3 flex-1">
          <h3 className="text-sm font-medium text-orange-800">
            BOM 설정이 필요한 제품이 있습니다
          </h3>
          <div className="mt-2 text-sm text-orange-700">
            <p className="mb-2">
              다음 {productsWithoutBOM.length}개 제품에 BOM(자재명세서)이 설정되지 않았습니다.
              생산 주문 생성을 위해 BOM을 설정해주세요.
            </p>
            <div className="space-y-2">
              {productsWithoutBOM.slice(0, 5).map(product => (
                <div 
                  key={product.id} 
                  className="flex items-center justify-between bg-white bg-opacity-50 rounded px-3 py-2"
                >
                  <div className="flex items-center">
                    <span className="text-sm font-medium text-orange-900">
                      {product.name}
                    </span>
                    <span className="ml-2 text-xs text-orange-600">
                      ({product.code})
                    </span>
                  </div>
                  <button
                    onClick={() => onManageBOM(product)}
                    className="flex items-center text-xs text-orange-800 hover:text-orange-900 font-medium hover:bg-orange-100 px-2 py-1 rounded transition-colors"
                  >
                    <ClipboardDocumentListIcon className="w-4 h-4 mr-1" />
                    BOM 설정
                  </button>
                </div>
              ))}
              
              {productsWithoutBOM.length > 5 && (
                <div className="text-xs text-orange-600 text-center py-1">
                  ... 및 {productsWithoutBOM.length - 5}개 제품 더
                </div>
              )}
            </div>
          </div>
          
          {/* 일괄 처리 버튼들 */}
          <div className="mt-4 flex space-x-2">
            <button
              onClick={() => {
                // 첫 번째 미설정 제품의 BOM 관리로 이동
                if (productsWithoutBOM[0]) {
                  onManageBOM(productsWithoutBOM[0]);
                }
              }}
              className="inline-flex items-center px-3 py-1.5 border border-orange-300 text-xs font-medium rounded-md text-orange-800 bg-white hover:bg-orange-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 transition-colors"
            >
              <ClipboardDocumentListIcon className="w-4 h-4 mr-1" />
              첫 번째 제품부터 설정
            </button>
            
            {onDismiss && (
              <button
                onClick={onDismiss}
                className="inline-flex items-center px-3 py-1.5 text-xs text-orange-600 hover:text-orange-800 transition-colors"
              >
                나중에 설정
              </button>
            )}
          </div>
        </div>
        
        {/* 닫기 버튼 */}
        {onDismiss && (
          <div className="flex-shrink-0 ml-4">
            <button
              onClick={onDismiss}
              className="inline-flex text-orange-400 hover:text-orange-600 transition-colors"
            >
              <span className="sr-only">닫기</span>
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default BOMAlert;