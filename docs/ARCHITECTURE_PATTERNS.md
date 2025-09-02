# Code Architecture & Design Patterns

이 문서는 프로젝트에서 사용되는 아키텍처 패턴과 설계 원칙을 설명합니다.

## Backend (Django) 패턴

### 1. Service Layer Pattern
- **비즈니스 로직을 service.py에서 처리, view는 얇게 유지**
- Controller-Service-Model 3계층 구조
- ViewSet은 HTTP 요청/응답만 담당
- Service는 핵심 비즈니스 로직 담당

### 2. Repository Pattern
- **복잡한 쿼리 로직은 별도 repository 클래스로 분리**
- QueryService로 구현 (예: HaccpQueryService)
- 데이터 접근 계층 캡슐화
- 테스트 시 Mock 객체로 대체 가능

### 3. Serializer 분리 패턴
- **CRUD 별로 다른 serializer 사용**
- CreateSerializer, UpdateSerializer, ListSerializer 분리
- 입력 검증과 출력 형식을 용도별로 최적화
- 보안과 성능 향상

### 4. Custom Manager Pattern
- **자주 사용하는 쿼리는 커스텀 매니저로 캡슐화**
- Model.objects.custom_query() 형태로 제공
- 복잡한 필터링 로직 재사용
- 쿼리 최적화 중앙 관리

### 5. Custom Permission Classes
- **역할별 권한은 커스텀 permission 클래스로 구현**
- IsAdminOrQualityManager, IsOwnerOrAdmin 등
- 세밀한 권한 제어
- 재사용 가능한 권한 로직

## Frontend (React) 패턴

### 1. Custom Hooks Pattern
- **API 호출, 상태 관리 로직을 훅으로 추상화**
- useAuth, useApi, useDashboard 등
- 컴포넌트에서 비즈니스 로직 분리
- 재사용성과 테스트 용이성 향상

### 2. Compound Component Pattern
- **복잡한 UI 컴포넌트는 여러 하위 컴포넌트로 구성**
- Table.Header, Table.Body, Table.Row 형태
- 유연한 조합과 확장성
- 일관된 디자인 시스템

### 3. Container/Presenter Pattern
- **로직과 UI 분리**
- Container: 상태 관리 및 비즈니스 로직
- Presenter: UI 렌더링만 담당
- 테스트와 유지보수 용이성

### 4. Context + Reducer Pattern
- **전역 상태 관리 (Redux 대신)**
- useContext + useReducer 조합
- 가벼운 상태 관리 솔루션
- Props Drilling 방지

### 5. Error Boundary Pattern
- **컴포넌트별 에러 처리**
- React의 Error Boundary 활용
- 부분적 오류가 전체 앱 크래시로 이어지는 것 방지
- 사용자 친화적 에러 메시지

## 폴더 구조 패턴

### Backend 구조
```
backend/core/
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── supplier.py
│   ├── production.py
│   └── haccp.py
├── serializers/
│   ├── __init__.py
│   ├── user_serializers.py
│   └── haccp_serializers.py
├── services/
│   ├── __init__.py
│   ├── haccp_service.py
│   ├── production_service.py
│   └── supplier_service.py
├── views/
│   ├── __init__.py
│   ├── user_views.py
│   ├── production_views.py
│   └── haccp_views.py
├── permissions/
│   ├── __init__.py
│   └── custom_permissions.py
└── repositories/
    ├── __init__.py
    └── query_services.py
```

### Frontend 구조
```
frontend/src/
├── components/
│   ├── common/          # 공통 UI 컴포넌트
│   ├── forms/           # 폼 관련 컴포넌트
│   └── charts/          # 차트/그래프 컴포넌트
├── pages/
│   ├── LoginPage.js
│   ├── DashboardPage.js
│   └── ProductionPage.js
├── hooks/
│   ├── useAuth.js
│   ├── useApi.js
│   └── useDashboard.js
├── services/
│   ├── apiClient.js
│   ├── authService.js
│   └── productionService.js
├── context/
│   ├── AuthContext.js
│   └── AppContext.js
└── utils/
    ├── helpers.js
    ├── constants.js
    └── validators.js
```

## HACCP 특화 패턴

### 1. Immutable Log Pattern
- **CCP 로그는 수정 불가, 새 레코드로만 이력 관리**
- 모든 변경 사항을 새로운 레코드로 저장
- 감사 추적 완벽 보장
- 데이터 무결성 유지

### 2. Audit Trail Pattern
- **모든 중요 데이터 변경 시 자동 감사 로그 생성**
- 누가, 언제, 무엇을, 왜 변경했는지 기록
- 규제 준수 요구사항 충족
- 문제 발생 시 원인 추적 가능

### 3. Chain of Responsibility Pattern
- **HACCP 검증 단계를 체인 패턴으로 구현**
- 여러 검증 단계를 순차적으로 실행
- 각 단계별 독립적 검증 로직
- 유연한 검증 프로세스 구성

### 4. Strategy Pattern (계획)
- **다양한 HACCP 표준에 따른 검증 전략**
- FDA, CODEX, 국내 HACCP 등 표준별 구현
- 런타임에 검증 전략 선택
- 다국가 진출 시 확장성

## 설계 원칙

### 1. SOLID 원칙
- **Single Responsibility**: 각 클래스는 하나의 책임만
- **Open/Closed**: 확장에는 열려있고 수정에는 닫혀있게
- **Liskov Substitution**: 하위 타입은 상위 타입을 대체 가능
- **Interface Segregation**: 클라이언트는 필요한 인터페이스만 의존
- **Dependency Inversion**: 추상화에 의존, 구체화에 의존하지 않음

### 2. DRY (Don't Repeat Yourself)
- **중복 코드 제거**
- 공통 로직은 유틸리티 함수나 베이스 클래스로 추출
- 템플릿 메소드 패턴 활용

### 3. KISS (Keep It Simple, Stupid)
- **단순함 추구**
- 과도한 추상화 지양
- 읽기 쉬운 코드 작성

### 4. YAGNI (You Aren't Gonna Need It)
- **필요할 때만 구현**
- 미래를 위한 과도한 준비 지양
- 현재 요구사항에 집중

## 보안 패턴

### 1. Input Validation
- **모든 입력값 검증**
- Serializer 레벨에서 1차 검증
- Service Layer에서 비즈니스 로직 검증
- SQL Injection, XSS 방지

### 2. Authentication & Authorization
- **JWT 기반 인증**
- 역할 기반 접근 제어 (RBAC)
- 세션 관리 및 토큰 만료 처리

### 3. Data Encryption
- **민감 데이터 암호화**
- 데이터베이스 레벨 암호화
- 전송 구간 HTTPS 적용

## 성능 최적화 패턴

### 1. Query Optimization
- **N+1 Query 문제 해결**
- select_related, prefetch_related 활용
- 인덱스 최적화
- 쿼리 성능 모니터링

### 2. Caching Strategy
- **Redis 기반 캐싱**
- API 응답 캐싱
- 데이터베이스 쿼리 결과 캐싱
- 캐시 무효화 전략

### 3. Lazy Loading
- **필요할 때만 데이터 로드**
- React Suspense 활용
- 무한 스크롤
- 이미지 지연 로딩

이러한 패턴들을 통해 확장 가능하고 유지보수하기 쉬운 코드베이스를 구축하고 있습니다.