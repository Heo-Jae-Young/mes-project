from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.utils import timezone

@api_view(['GET'])
@permission_classes([AllowAny])  # 인증 없이 접근 가능
def health_check(request):
    """
    헬스체크 엔드포인트
    - 서버 상태 확인
    - 데이터베이스 연결 확인
    - 인증 없이 접근 가능 (CI/CD용)
    """
    try:
        # 데이터베이스 연결 테스트
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        
        return Response({
            'status': 'healthy',
            'timestamp': timezone.now(),
            'database': 'connected',
            'version': '1.0.0'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'unhealthy',
            'timestamp': timezone.now(),
            'database': 'error',
            'error': str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)