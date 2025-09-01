from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from core.views import (
    UserViewSet,
    SupplierViewSet, 
    RawMaterialViewSet,
    MaterialLotViewSet,
    FinishedProductViewSet,
    ProductionOrderViewSet,
    CCPViewSet,
    CCPLogViewSet,
)

# DRF Router로 ViewSet URL 자동 생성
router = DefaultRouter()

# ViewSet 등록
router.register(r'users', UserViewSet, basename='user')
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'raw-materials', RawMaterialViewSet, basename='rawmaterial')
router.register(r'material-lots', MaterialLotViewSet, basename='materiallot')
router.register(r'finished-products', FinishedProductViewSet, basename='finishedproduct')
router.register(r'production-orders', ProductionOrderViewSet, basename='productionorder')
router.register(r'ccps', CCPViewSet, basename='ccp')
router.register(r'ccp-logs', CCPLogViewSet, basename='ccplog')

urlpatterns = [
    # JWT Token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # API endpoints
    path('', include(router.urls)),
]