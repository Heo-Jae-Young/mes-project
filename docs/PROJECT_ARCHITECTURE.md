# 프로젝트 아키텍처 및 개발 가이드

이 문서는 MES 프로젝트의 백엔드(Django)와 프론트엔드(React) 아키텍처를 설명하고, 새로운 기능을 추가하거나 기존 코드를 수정할 때 참고할 수 있는 가이드를 제공합니다.

## 1. 전체 구조

이 프로젝트는 하나의 저장소에서 백엔드와 프론트엔드를 함께 관리하는 **모노레포(Monorepo)** 구조를 가집니다.

- `backend/`: Django REST Framework 기반의 API 서버
- `frontend/`: React 기반의 웹 애플리케이션
- `docs/`: 프로젝트 관련 문서

---

## 2. 백엔드 (Django)

백엔드는 **서비스 레이어(Service Layer)** 패턴을 도입하여 비즈니스 로직을 명확하게 분리한 구조를 사용합니다.

### 2.1. 아키텍처 개요

API 요청이 들어왔을 때의 일반적인 처리 흐름은 다음과 같습니다.

**Request → `urls.py` → `views.py` → `services.py` → `models.py` / `serializers.py` → Response**

1.  **`urls.py` (URL 라우팅)**: 요청 URL을 분석하여 어떤 `View`가 처리할지 결정합니다.
2.  **`views.py` (View/Controller)**: HTTP 요청을 직접 받습니다. 데이터 유효성 검증(Serializer)과 핵심 비즈니스 로직은 `Service`에 위임하고, 최종 HTTP 응답(성공/실패)을 반환하는 역할만 담당합니다. **(코드를 얇게 유지)**
3.  **`services.py` (Service Layer)**: 실제 비즈니스 로직을 처리합니다. 여러 모델을 조합하거나, 복잡한 계산, 외부 API 호출 등 핵심적인 역할을 수행합니다.
4.  **`models.py` (Model)**: 데이터베이스 테이블의 구조를 정의합니다. Django ORM을 통해 데이터베이스와 상호작용합니다.
5.  **`serializers.py` (Serializer)**: `Model` 객체를 JSON 형태로 변환하거나, 요청으로 들어온 JSON을 `Model` 객체로 변환하는 역할을 합니다. 데이터의 유효성 검증(validation)도 담당합니다.

### 2.2. 핵심 디렉토리 구조 (`backend/core/`)

```
core/
├── models/         # 데이터베이스 모델 정의
├── serializers/    # JSON 직렬화 및 유효성 검증
├── services/       # 핵심 비즈니스 로직
├── views/          # API 엔드포인트 (HTTP 요청/응답 처리)
├── urls.py         # URL과 View 매핑
└── tests/          # 단위/통합 테스트
```

### 2.3. 개발 가이드: "어디를 수정해야 할까?"

#### 🔹 **새로운 API 엔드포인트를 추가하고 싶을 때**

1.  **`models/`**: API가 다룰 새로운 데이터가 필요하다면 모델을 정의하거나 수정합니다.
2.  **`serializers/`**: 모델에 대한 Serializer를 생성합니다. (데이터 표현 방식 정의)
3.  **`views/`**: 새로운 `ViewSet` 또는 `APIView`를 생성합니다.
4.  **`urls.py`**: URL 경로와 방금 만든 View를 연결합니다.
5.  **`services/` (선택 사항)**: View에 들어갈 비즈니스 로직이 복잡하다면 Service 클래스를 만들어 로직을 분리합니다.

#### 🔹 **기존 API의 비즈니스 로직을 수정하고 싶을 때**

- **`services/` 디렉토리**를 가장 먼저 확인하세요.
- 예를 들어, '생산 완료' 시의 로직을 바꾸고 싶다면 `services/production_service.py`의 `complete_production` 메소드를 수정하면 됩니다.

#### 🔹 **데이터베이스 테이블 구조를 변경하고 싶을 때**

1.  **`models/`**에서 원하는 모델 파일을 수정합니다.
2.  `backend` 디렉토리에서 `python manage.py makemigrations` 명령어로 마이그레이션 파일을 생성합니다.
3.  `python manage.py migrate` 명령어로 데이터베이스에 변경 사항을 적용합니다.

---

## 3. 프론트엔드 (React)

프론트엔드는 `create-react-app`으로 생성된 표준적인 React 프로젝트 구조를 따르며, **컴포넌트 기반 아키텍처**를 사용합니다.

### 3.1. 아키텍처 개요

- **UI**: 재사용 가능한 `Component` 단위로 UI를 구성합니다.
- **Routing**: `react-router-dom`을 사용하여 페이지 간 이동을 처리합니다.
- **State Management**:
  - **로컬 상태**: `useState`, `useReducer`를 사용하여 컴포넌트 내부의 상태를 관리합니다.
  - **전역 상태**: `useContext`를 사용하여 로그인 정보(인증 토큰, 사용자 정보) 등 여러 컴포넌트가 공유해야 하는 상태를 관리합니다. (`context/AuthContext.js`)
- **API Communication**: `axios`를 사용하여 백엔드 API와 통신합니다. `services/` 디렉토리에서 API 호출 함수를 중앙 관리합니다.

### 3.2. 핵심 디렉토리 구조 (`frontend/src/`)

```
src/
├── components/     # 재사용 가능한 공통 컴포넌트 (버튼, 헤더, 레이아웃 등)
├── pages/          # 개별 페이지를 구성하는 메인 컴포넌트 (로그인 페이지, 대시보드 페이지 등)
├── services/       # 백엔드 API 호출 함수들을 모아둔 곳
├── context/        # 전역 상태 관리를 위한 Context API
├── hooks/          # 여러 컴포넌트에서 재사용될 로직을 담은 커스텀 훅
├── utils/          # 기타 유틸리티 함수
├── App.js          # 애플리케이션의 메인 컴포넌트, 라우팅 설정
└── index.js        # 애플리케이션의 진입점
```

### 3.3. 개발 가이드: "어디를 수정해야 할까?"

#### 🔹 **새로운 페이지를 추가하고 싶을 때**

1.  **`pages/`**: `MyNewPage.js`와 같이 새로운 페이지 컴포넌트 파일을 생성합니다.
2.  **`App.js`**: `<Routes>` 내부에 `<Route path="/my-new-page" element={<MyNewPage />} />` 와 같이 새로운 경로를 추가하여 페이지와 URL을 연결합니다.

#### 🔹 **여러 페이지에서 사용될 공통 UI(버튼, 팝업 등)를 만들 때**

- **`components/common/`** 디렉토리에 새로운 컴포넌트 파일을 생성하고, 필요한 곳에서 `import`하여 사용합니다.

#### 🔹 **새로운 API를 호출해야 할 때**

1.  **`services/`**: 기능에 맞는 서비스 파일(예: `haccpService.js`)을 찾거나 생성합니다.
2.  `axios`를 사용하여 API를 호출하는 비동기 함수를 작성합니다.
   ```javascript
   // services/haccpService.js
   import apiClient from './apiClient';

   export const getHaccpLogs = () => {
     return apiClient.get('/api/haccp-logs/');
   };
   ```
3.  사용하려는 페이지나 컴포넌트에서 해당 서비스 함수를 `import`하여 호출합니다.

#### 🔹 **로그인 상태나 사용자 정보를 사용하고 싶을 때**

- **`context/AuthContext.js`**가 사용자 정보, 로그인/로그아웃 함수를 제공합니다.
- `useContext(AuthContext)` 훅을 사용하여 필요한 값이나 함수를 가져올 수 있습니다.
  ```javascript
  import { useContext } from 'react';
  import { AuthContext } from '../context/AuthContext';

  const MyComponent = () => {
    const { user, logout } = useContext(AuthContext);
    // 이제 user 객체와 logout 함수를 사용할 수 있습니다.
  };
  ```
