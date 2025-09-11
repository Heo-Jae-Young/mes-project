/**
 * HACCP MES 라이브 데모 자동화 CRUD 테스트
 * 
 * 실행 방법:
 * 1. Playwright 설치: npm install -g playwright
 * 2. 브라우저 설치: playwright install chromium
 * 3. 스크립트 실행: node scripts/test/automated-crud-test.js
 */

const { chromium } = require('playwright');

// 설정
const CONFIG = {
  BASE_URL: 'http://52.78.61.106',
  LOGIN_CREDENTIALS: {
    username: 'admin',
    password: 'admin123'
  },
  HEADLESS: false, // false로 설정하면 브라우저 창이 보임
  TIMEOUT: 5000 // 5초로 단축
};

// 동적 테스트 데이터 생성 함수 (중복 방지)
function generateTestData() {
  const timestamp = Date.now();
  const dateStr = new Date().toISOString().slice(5, 16).replace(/[-:]/g, ''); // MMDDHHMMSS
  
  return {
    supplier: {
      name: `자동테스트회사_${dateStr}`,
      code: `AUTO${timestamp.toString().slice(-6)}`, // 마지막 6자리로 유니크 코드
      contact: '테스트담당자',
      email: `test${timestamp}@autotest.com`,
      phone: '02-1234-5678',
      address: '서울시 강남구 자동테스트로 123',
      certifications: 'HACCP, ISO 22000 (자동테스트용)'
    },
    material: {
      name: `자동테스트원자재_${dateStr}`,
      code: `MAT${timestamp.toString().slice(-6)}`, // 마지막 6자리로 유니크 코드
      unit: 'kg',
      description: '자동 CRUD 테스트용 원자재',
      memo: '테스트 완료 후 자동 삭제됨'
    }
  };
}

async function runCRUDTest() {
  const browser = await chromium.launch({ 
    headless: CONFIG.HEADLESS,
    slowMo: 1000 // 각 액션 사이 1초 대기
  });
  
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 } // 화면 크기 고정
  });
  const page = await context.newPage();
  
  // 동적 테스트 데이터 생성
  const testData = generateTestData();
  console.log('📋 생성된 테스트 데이터:');
  console.log('  - 공급업체:', testData.supplier.name, testData.supplier.code);
  console.log('  - 원자재:', testData.material.name, testData.material.code);
  
  try {
    console.log('🚀 HACCP MES 라이브 데모 CRUD 테스트 시작');
    
    // 데코레이터 패턴으로 각 테스트 단계 래핑 (testData 전달)
    const steps = [
      withStepLogging('로그인 테스트', 1)(login),
      withStepLogging('대시보드 기능 확인', 2)(checkDashboard),  
      withStepLogging('공급업체 CRUD 테스트', 3)((page) => testSupplierCRUD(page, testData)),
      withStepLogging('원자재 CRUD 테스트', 4)((page) => testMaterialCRUD(page, testData)),
      withStepLogging('제품 관리 확인', 5)(checkProductManagement),
      withStepLogging('생산 관리 확인', 6)(checkProductionManagement),
      withStepLogging('CCP 로그 관리 확인', 7)(checkCCPLogs)
    ];
    
    // 각 단계 순차 실행
    for (const step of steps) {
      await step(page);
    }
    
    console.log('🎉 모든 테스트 완료!');
    
  } catch (error) {
    console.error('💥 전체 테스트 실패!');
    console.error('🔍 최종 오류:', error.stack);
  } finally {
    if (!CONFIG.HEADLESS) {
      console.log('⏳ 5초 후 브라우저를 닫습니다...');
      await page.waitForTimeout(5000);
    }
    await browser.close();
  }
}

async function login(page) {
  console.log('📋 1. 로그인 테스트');
  
  await page.goto(CONFIG.BASE_URL);
  await page.waitForSelector('input[type="text"]');
  
  // 로그인 정보 입력
  await page.fill('input[type="text"]', CONFIG.LOGIN_CREDENTIALS.username);
  await page.fill('input[type="password"]', CONFIG.LOGIN_CREDENTIALS.password);
  await page.click('button:has-text("로그인")');
  
  // 대시보드 로드 대기
  await page.waitForURL('**/dashboard');
  await page.waitForSelector('h1:has-text("HACCP MES 대시보드")');
  
  console.log('✅ 로그인 성공');
}

async function checkDashboard(page) {
  console.log('📋 2. 대시보드 기능 확인');
  
  // 대시보드 위젯들 확인
  await page.waitForSelector('text=재고 현황');
  await page.waitForSelector('text=시스템 현황');
  await page.waitForSelector('text=최근 CCP 로그');
  
  console.log('✅ 대시보드 정상 작동');
}

async function testSupplierCRUD(page, testData) {
  let createdSupplierId = null;
  
  // 공급업체 관리 페이지로 이동
  await logAction('공급업체 관리 페이지 이동', async () => {
    await page.getByRole('link', { name: '공급업체 관리' }).click();
    await page.waitForSelector('h1:has-text("공급업체 관리")');
  });
  
  // CREATE: 새 공급업체 등록
  await logAction('공급업체 등록 (Create)', async () => {
    await page.getByRole('button', { name: '공급업체 등록' }).click();
    
    // 동적 테스트 데이터 사용
    await page.fill('input[name="name"]', testData.supplier.name);
    await page.fill('input[name="code"]', testData.supplier.code);
    await page.fill('input[name="contact_person"]', testData.supplier.contact);
    await page.fill('input[name="email"]', testData.supplier.email);
    await page.fill('input[name="phone"]', testData.supplier.phone);
    await page.fill('textarea[name="address"]', testData.supplier.address);
    await page.fill('textarea[name="certification"]', testData.supplier.certifications);
    
    await page.getByRole('button', { name: '등록', exact: true }).click();
    
    // 등록 결과 확인 (헬퍼 함수 사용)
    await waitForResult(page, '공급업체이(가) 등록되었습니다', '공급업체 등록');
  });
  
  // UPDATE: 공급업체 수정 (등록이 성공한 경우에만)
  await logAction('공급업체 수정 (Update)', async () => {
    // 방금 생성한 공급업체 찾기 (테이블에서 이름으로 검색)
    const supplierRow = page.locator('tr', { hasText: testData.supplier.name });
    
    // 해당 행의 첫 번째 버튼(수정 버튼) 클릭
    await supplierRow.getByRole('button').first().click();
    
    // 담당자명 수정
    await page.fill('input[name="contact_person"]', '자동테스트_수정됨');
    
    // 모달 안의 수정 버튼 클릭 (submit 타입)
    await page.locator('button[type="submit"]', { hasText: '수정' }).click();
    await page.waitForSelector('text=공급업체 정보가 수정되었습니다');
  });
  
  // DELETE: 공급업체 삭제 (테스트 데이터 정리)
  await logAction('공급업체 삭제 (Delete)', async () => {
    // 기존 다이얼로그 리스너 제거 후 새로 설정
    page.removeAllListeners('dialog');
    
    // 삭제 확인 다이얼로그 처리 (한 번만)
    page.once('dialog', async dialog => {
      console.log('    📢 삭제 확인:', dialog.message());
      await dialog.accept();
    });
    
    // 방금 수정한 공급업체 찾기 (해당 행의 두 번째 버튼이 삭제 버튼)
    const supplierRow = page.locator('tr', { hasText: testData.supplier.name });
    await supplierRow.getByRole('button').nth(1).click(); // 두 번째 버튼 = 삭제
    await page.waitForSelector('text=공급업체이(가) 삭제되었습니다');
  });
}

async function testMaterialCRUD(page, testData) {
  // 원자재 관리 페이지로 이동
  await logAction('원자재 관리 페이지 이동', async () => {
    await page.getByRole('link', { name: '원자재 관리' }).click();
    await page.waitForSelector('h1:has-text("원자재 관리")');
  });
  
  // CREATE: 새 원자재 등록
  await logAction('원자재 등록 (Create)', async () => {
    await page.getByRole('button', { name: '원자재 등록' }).click();
    
    // 동적 테스트 데이터 사용
    await page.fill('input[name="name"]', testData.material.name);
    await page.fill('input[name="code"]', testData.material.code);
    await page.selectOption('select[name="category"]', 'ingredient');
    
    // 공급업체는 첫 번째 옵션 선택 (기존 공급업체 중 하나)
    const supplierOptions = await page.locator('select[name="supplier_id"] option:not([value=""])').all();
    if (supplierOptions.length > 0) {
      const firstSupplierValue = await supplierOptions[0].getAttribute('value');
      await page.selectOption('select[name="supplier_id"]', firstSupplierValue);
    } else {
      console.log('    ⚠️ 사용 가능한 공급업체가 없습니다.');
    }
    
    await page.fill('input[name="unit"]', testData.material.unit);
    await page.fill('textarea[name="description"]', testData.material.description);
    await page.fill('textarea[name="notes"]', testData.material.memo);
    
    // 페이지 끝까지 스크롤 후 등록 버튼 클릭
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(500);
    
    // submit 타입의 등록 버튼을 직접 선택하여 클릭
    await page.locator('button[type="submit"]').filter({ hasText: '등록' }).click();
    
    // 등록 결과 확인 (헬퍼 함수 사용)
    await waitForResult(page, '원자재이(가) 등록되었습니다', '원자재 등록');
  });
  
  // DELETE: 원자재 삭제 (테스트 데이터 정리)
  await logAction('원자재 삭제 (Delete)', async () => {
    // 기존 다이얼로그 리스너 제거 후 새로 설정
    page.removeAllListeners('dialog');
    
    // 삭제 확인 다이얼로그 처리 (한 번만)
    page.once('dialog', async dialog => {
      console.log('    📢 삭제 확인:', dialog.message());
      await dialog.accept();
    });
    
    // 방금 생성한 원자재 찾기 (해당 행의 두 번째 버튼이 삭제 버튼)
    const materialRow = page.locator('tr', { hasText: testData.material.name });
    await materialRow.getByRole('button').nth(1).click(); // 두 번째 버튼 = 삭제
    await page.waitForSelector('text=원자재이(가) 삭제되었습니다');
  });
}

async function checkProductManagement(page) {
  console.log('📋 5. 제품 관리 확인');
  
  await page.click('a:has-text("제품 관리")');
  await page.waitForSelector('h1:has-text("제품 관리")');
  
  // BOM 설정 알림 닫기
  const bomAlertButton = await page.locator('button:has-text("나중에 설정")');
  if (await bomAlertButton.isVisible()) {
    await bomAlertButton.click();
  }
  
  // 제품 목록 확인
  await page.waitForSelector('text=바닐라 쿠키');
  await page.waitForSelector('text=프리미엄 쌀과자');
  
  console.log('✅ 제품 관리 확인 완료');
}

async function checkProductionManagement(page) {
  console.log('📋 6. 생산 관리 확인');
  
  await page.click('a:has-text("생산 관리")');
  await page.waitForSelector('h1:has-text("생산 관리")');
  
  // 생산 주문 목록 확인
  await page.waitForSelector('text=PO002');
  await page.waitForSelector('text=PO001');
  
  console.log('✅ 생산 관리 확인 완료');
}

async function checkCCPLogs(page) {
  console.log('📋 7. CCP 로그 관리 확인');
  
  await page.click('a:has-text("품질 관리")');
  await page.waitForSelector('h1:has-text("CCP 모니터링 로그")');
  
  // CCP 로그 확인
  await page.waitForSelector('text=가열 온도 관리');
  await page.waitForSelector('text=금속 이물질 검출');
  await page.waitForSelector('text=쿠키 굽기 온도');
  
  console.log('✅ CCP 로그 관리 확인 완료');
}

// 테스트 단계 래퍼 함수 (데코레이터 역할)
function withStepLogging(stepName, stepNumber) {
  return function(testFunction) {
    return async function(page) {
      console.log(`📋 ${stepNumber}. ${stepName}`);
      const startTime = Date.now();
      
      try {
        await testFunction(page);
        const duration = ((Date.now() - startTime) / 1000).toFixed(1);
        console.log(`✅ ${stepName} 완료 (${duration}초)`);
      } catch (error) {
        const duration = ((Date.now() - startTime) / 1000).toFixed(1);
        console.error(`❌ ${stepName} 실패 (${duration}초)`);
        console.error(`   원인: ${error.message}`);
        
        // 실패 시 스크린샷
        try {
          const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
          const filename = `screenshots/failure-${stepName.replace(/\s+/g, '-')}-${timestamp}.png`;
          await page.screenshot({ path: filename, fullPage: true });
          console.log(`   📸 스크린샷: ${filename}`);
        } catch (screenshotError) {
          console.log(`   📸 스크린샷 실패: ${screenshotError.message}`);
        }
        
        throw error; // 에러 다시 던지기
      }
    };
  };
}

// 서브 액션 로깅 함수 (검증 실패 감지 포함)
async function logAction(actionName, actionFunction) {
  console.log(`  🔄 ${actionName}...`);
  const startTime = Date.now();
  
  try {
    await actionFunction();
    const duration = ((Date.now() - startTime) / 1000).toFixed(1);
    console.log(`  ✅ ${actionName} 성공 (${duration}초)`);
  } catch (error) {
    const duration = ((Date.now() - startTime) / 1000).toFixed(1);
    console.error(`  ❌ ${actionName} 실패 (${duration}초): ${error.message}`);
    throw error;
  }
}

// 성공/실패 메시지 대기 헬퍼 함수
async function waitForResult(page, successText, actionName) {
  try {
    await page.waitForSelector(`text=${successText}`, { timeout: 5000 });
    console.log(`    ✅ ${actionName} 성공`);
  } catch (error) {
    // 에러 메시지 확인
    const errorElements = await page.locator('text*=이미 존재, text*=오류, text*=실패').all();
    if (errorElements.length > 0) {
      const errorText = await errorElements[0].textContent();
      console.log(`    ⚠️ ${actionName} 실패 (예상된 오류):`, errorText);
      // 모달 닫기
      await page.keyboard.press('Escape');
      await page.waitForTimeout(1000);
      throw new Error(`${actionName} 실패: ${errorText}`);
    } else {
      throw error;
    }
  }
}

// 스크립트 실행
if (require.main === module) {
  runCRUDTest().catch(console.error);
}

module.exports = { runCRUDTest, CONFIG, generateTestData };