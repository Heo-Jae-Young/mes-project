# HACCP MES E2E 테스트

End-to-End 테스트로 실제 브라우저에서 전체 사용자 시나리오를 자동으로 검증합니다.

## 🚀 빠른 시작

### 1. 의존성 설치
```bash
# 프로젝트 루트에서 실행
cd e2e_tests
npm run install-playwright
```

### 2. 테스트 실행
```bash
# e2e_tests 디렉토리에서 실행
cd e2e_tests

# 브라우저 창을 보면서 실행 (권장)
npm run test:crud

# 백그라운드에서 실행 (빠름)  
npm run test:crud-headless
```

## 📋 테스트 내용

자동화 스크립트가 다음 작업들을 순서대로 실행합니다:

### 1. ✅ 로그인 테스트
- `admin/admin123` 계정으로 자동 로그인
- 대시보드 접근 확인

### 2. ✅ 대시보드 확인
- 재고 현황 위젯 로드 확인
- 시스템 현황 확인
- 최근 CCP 로그 표시 확인

### 3. ✅ 공급업체 CRUD 테스트
- **Create**: 테스트 공급업체 자동 등록
- **Read**: 공급업체 목록 조회
- **Update**: 담당자명 수정
- **Delete**: 테스트 공급업체 삭제

### 4. ✅ 원자재 CRUD 테스트
- **Create**: 테스트 원자재 자동 등록
- **Read**: 원자재 목록 조회
- **Delete**: 테스트 원자재 삭제

### 5. ✅ 제품 관리 확인
- 제품 목록 조회
- BOM 설정 알림 처리

### 6. ✅ 생산 관리 확인
- 생산 주문 목록 조회
- 생산 상태 확인

### 7. ✅ CCP 로그 관리 확인
- HACCP 모니터링 로그 조회
- 3개 CCP 항목 확인

## ⚙️ 설정 옵션

### 기본 설정 (`scripts/test/automated-crud-test.js`)

```javascript
const CONFIG = {
  BASE_URL: 'http://52.78.61.106',  // 라이브 데모 URL
  LOGIN_CREDENTIALS: {
    username: 'admin',
    password: 'admin123'
  },
  HEADLESS: false,  // false = 브라우저 창 보임, true = 백그라운드
  TIMEOUT: 30000    // 30초 타임아웃
};
```

### 테스트 데이터 커스터마이징

```javascript
const TEST_DATA = {
  supplier: {
    name: '테스트제품주식회사',
    code: 'SUP999',
    contact: '홍길동',
    // ... 기타 설정
  },
  material: {
    name: '테스트 원자재',
    code: 'TST001',
    // ... 기타 설정
  }
};
```

## 🎬 실행 예시

```bash
$ cd e2e_tests  
$ npm run test:crud

🚀 HACCP MES 라이브 데모 CRUD 테스트 시작
📋 1. 로그인 테스트
✅ 로그인 성공
📋 2. 대시보드 기능 확인
✅ 대시보드 정상 작동
📋 3. 공급업체 CRUD 테스트
  📝 공급업체 등록 (Create)
  ✏️ 공급업체 수정 (Update)
  🗑️ 공급업체 삭제 (Delete)
✅ 공급업체 CRUD 테스트 완료
📋 4. 원자재 CRUD 테스트
  📝 원자재 등록 (Create)
  🗑️ 원자재 삭제 (Delete)
✅ 원자재 CRUD 테스트 완료
📋 5. 제품 관리 확인
✅ 제품 관리 확인 완료
📋 6. 생산 관리 확인
✅ 생산 관리 확인 완료
📋 7. CCP 로그 관리 확인
✅ CCP 로그 관리 확인 완료
✅ 모든 테스트 완료!
```

## 🔧 고급 사용법

### 다른 환경에서 테스트
```javascript
// 로컬 개발 서버 테스트
const CONFIG = {
  BASE_URL: 'http://localhost:3000',
  // ...
};
```

### 테스트 실행 속도 조정
```javascript
const browser = await chromium.launch({ 
  headless: false,
  slowMo: 2000  // 2초씩 대기 (더 느리게)
});
```

### 스크린샷 자동 저장
```javascript
await page.screenshot({ 
  path: `screenshots/test-${Date.now()}.png`,
  fullPage: true 
});
```

## 📝 주의사항

1. **라이브 서버 의존성**: 라이브 데모 서버(`http://52.78.61.106`)가 실행 중이어야 합니다.

2. **데이터 정리**: 테스트 후 생성된 데이터는 자동으로 삭제됩니다.

3. **에러 처리**: 네트워크 오류나 서버 응답 지연 시 자동으로 재시도합니다.

4. **브라우저 호환성**: Chromium 기반으로 작동하며, 다른 브라우저도 지원 가능합니다.

## 🎯 활용 방안

- **CI/CD 파이프라인**: GitHub Actions에서 자동 실행
- **정기 테스트**: cron job으로 주기적 실행
- **데모 준비**: 프레젠테이션 전 시스템 상태 확인
- **회귀 테스트**: 새 기능 배포 후 기존 기능 확인