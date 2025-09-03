# Development Log

이 문서는 프로젝트의 주요 개발 이정표와 학습 내용을 기록합니다.

## 2025-09-01: Django Backend 초기 설정 완료

- Django 5.2.5 + DRF 프로젝트 생성
- MariaDB Docker 연동 (localhost → 127.0.0.1 소켓 이슈 해결)
- JWT 인증, CORS 설정 완료
- 기본 마이그레이션 성공
- **상태**: PR #1 머지 완료

## 2025-09-01: HACCP 모델 구현 완료

- models/ 패키지 구조로 8개 모델 파일 분리 구현
- User, Supplier, RawMaterial, MaterialLot, FinishedProduct, ProductionOrder, CCP, CCPLog
- Django Admin 인터페이스 완비 (CCPLog는 불변 데이터로 수정/삭제 불가)
- 시드 데이터 management command 구현 (admin 계정 자동 생성 포함)
- **상태**: PR #2 머지 완료

## 2025-09-01: DRF API 구현 완료

- **Serializers 구현**: 8개 모델별 CRUD 분리 구조
- **ViewSets 구현**: REST API 엔드포인트 및 커스텀 액션
  - 역할별 권한 필터링 (admin, quality_manager, operator 등)
  - 통계/대시보드 API (/statistics, /dashboard 등)
  - HACCP 전용 기능 (/compliance-report, /critical-alerts)
- **URL 라우팅**: DRF Router로 자동 URL 생성
- **의존성 추가**: django-filter 패키지 및 설정
- **상태**: PR #3 머지 완료

## 2025-09-01: Service Layer 구현 완료

### 구현된 서비스 클래스

#### HaccpService
- `validate_ccp_log_creation()`: CCP 로그 생성 전 검증
- `calculate_compliance_score()`: HACCP 컴플라이언스 점수 계산
- `get_critical_alerts()`: 중요 알림 목록 조회
- `generate_compliance_report()`: 컴플라이언스 보고서 생성

#### ProductionService
- `validate_production_order_creation()`: 생산 주문 생성 검증
- `start_production()`: 생산 시작 처리 (원자재 할당)
- `complete_production()`: 생산 완료 처리
- `get_production_efficiency()`: 효율성 지표 계산

#### SupplierService
- `validate_supplier_creation()`: 공급업체 등록 검증
- `evaluate_supplier_performance()`: 성과 평가
- `get_supplier_risk_assessment()`: 리스크 평가

### 테스트 현황
- **총 25개 단위 테스트 모두 통과**
- UserService Tests: 8개
- HaccpService Tests: 6개
- ProductionService Tests: 5개
- SupplierService Tests: 6개

**상태**: PR #4 머지 완료

## 2025-09-01: ViewSet-Service Layer 연결 완료

- CCPLogViewSet: `perform_create`, `get_queryset` Service 연결
- ProductionOrderViewSet: `start_production`, `complete_production` Service 연결  
- UserViewSet: 완전한 Service Layer 활용
- SupplierViewSet: Service 클래스 연결
- API 문서화: drf-spectacular 설치 및 Swagger UI 구축
- **상태**: PR #6 머지 완료

## 2025-09-02: 프론트엔드 초기 설정 완료

- **React 프로젝트 생성**: `create-react-app`을 사용하여 기본 구조 설정
- **초기 라이브러리 설치**: `axios`, `react-router-dom`, `tailwindcss`
- **기본 컴포넌트**: LoginPage, DashboardPage 스켈레톤 구현
- **Context API**: 전역 상태 관리 (AuthContext)
- **상태**: PR #7 머지 완료

## 2025-09-02: 대시보드 통계 API 구현 및 문서화 완료

### 백엔드: StatisticsAPIView 구현
- HACCP 준수율 계산 (최근 30일)
- 중요 이탈 건수 조회 (최근 7일)
- 진행중인 생산 오더 수 제공
- `/api/statistics/` 엔드포인트 추가

### 프론트엔드: 동적 데이터 연동
- `DashboardPage.js`에서 3개 API 병렬 호출
- 실제 백엔드 데이터로 대시보드 카드 렌더링
- 최근 CCP 로그 목록 동적 생성
- 로딩 상태 및 에러 처리 구현

### 종합 개발 문서 구축
- 백엔드/프론트엔드 데이터 흐름 다이어그램 (Mermaid)
- 파일별 상세 설명과 기술적 구조 문서화
- Mermaid 다이어그램 작성 가이드

**상태**: PR #8 생성

## Development Insights

### DB 연결 이슈 해결
- Django mysqlclient에서 localhost는 Unix 소켓 시도
- Docker 환경에서는 127.0.0.1 사용 (TCP 포트)
- mysqlclient 컴파일 위해 libmysqlclient-dev 설치 필요

### 테스트 아키텍처 결정
- **최종 선택**: MariaDB 단일 환경 (SQLite vs MariaDB 복잡성 제거)
- **이유**: 실제 운영환경과 동일한 DB 사용이 가장 신뢰성 있음
- **MariaDB 전환으로 발견한 실제 버그**: `employee_id` 필드 길이 제한

### 환경 설정 베스트 프랙티스
- .env.example 템플릿 제공
- SECRET_KEY는 절대 하드코딩 금지

## 2025-09-03: CCP 로그 관리 기능 + 아키텍처 개선 완료

### 🎯 구현 내용
- **프론트엔드 CCP 로그 기능**: CCPLogForm, CCPLogList, CCPLogsPage 완성
- **네비게이션 시스템**: Header 컴포넌트와 라우팅 구조 완비
- **아키텍처 개선**: 레이어별 책임 분리, 중복 코드 제거
- **상수 관리**: constants.py 도입으로 하드코딩 제거

### 🔧 주요 기술적 해결사항
- **API 경로 문제**: .env 파일에서 REACT_APP_API_URL 설정 누락으로 404 에러 → `/api` 접두사 추가로 해결
- **데이터 무결성 오류**: CCPLog 생성 시 is_within_limits 필드 null 에러 → Model의 save() 메서드에서 자동 계산으로 해결
- **중복 로직 제거**: CCP 한계 기준 체크가 Model, Serializer, View에 중복 → Model Layer에만 남기고 나머지 제거

### 📂 생성된 파일들
**Backend:**
- `core/constants.py`: 시스템 상수 정의

**Frontend:**
- `src/components/forms/CCPLogForm.js`: CCP 로그 입력 폼
- `src/components/lists/CCPLogList.js`: CCP 로그 목록 및 필터링
- `src/components/layout/Header.js`: 네비게이션 헤더
- `src/pages/CCPLogsPage.js`: CCP 로그 관리 메인 페이지
- `src/services/ccpService.js`: CCP 관련 API 서비스

### 🎓 학습 내용
- **레이어별 책임 분리**: 각 레이어가 명확한 역할을 가져야 성능과 유지보수성이 향상됨
- **환경 변수 중요성**: API 경로 설정 실수로 전체 기능이 동작하지 않을 수 있음
- **Django Model의 save() 메서드**: 비즈니스 로직을 Model에서 처리하면 데이터 일관성 보장

### ✅ 테스트 결과
- CCP 로그 입력/조회 기능 정상 작동
- 한계 기준 이탈 시 자동 상태 계산 정상
- 대시보드 API 데이터 일관성 확보

**상태**: feature/ccp-log-management 브랜치에서 작업 완료, PR 준비 중
- docker-compose.yml 최신 문법 (version 필드 제거)