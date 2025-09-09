# GitHub Actions 고급 배포 전략 분석

> Examples 워크플로우에서 발견한 고급 전략들을 체계적으로 분석하고 적용 방안을 제시합니다.

## 📋 목차

- [환경 관리 전략](#-환경-관리-전략)
- [빌드 및 테스트 전략](#-빌드-및-테스트-전략)
- [배포 전략](#-배포-전략)
- [리소스 최적화 전략](#-리소스-최적화-전략)
- [모니터링 및 품질 관리](#-모니터링-및-품질-관리)
- [Elixir 특화 전략](#-elixir-특화-전략)
- [MES 프로젝트 적용 가이드](#-mes-프로젝트-적용-가이드)

---

## 🌍 환경 관리 전략

### 1. 다단계 환경 분리

**전략 개요**
```yaml
# 3단계 환경 구성
environments:
  - alpha: 개발 테스트용 (불안정, 자주 리셋)
  - beta: 스테이징 환경 (프로덕션 유사)
  - prod: 프로덕션 환경 (안정성 최우선)
```

**장점:**
- 단계적 검증으로 위험 최소화
- 각 환경별 용도와 정책 명확화
- 롤백 시나리오 체계화

**단점:**
- 인프라 비용 증가 (3배)
- 관리 복잡성 증가
- 환경 간 데이터 동기화 이슈

**적용 예시:**
```yaml
jobs:
  deploy-staging:
    if: github.ref == 'refs/heads/develop'
    environment: staging
    
  deploy-production:
    if: github.ref == 'refs/heads/main'
    environment: production
    needs: [deploy-staging]
```

### 2. 환경별 설정 관리

**전략 개요**
```yaml
env:
  CONFIG: fly/braavos-${{inputs.target}}-${{inputs.app}}.toml
```

**적용 방법:**
- 환경별 설정 파일 분리
- 템플릿 기반 동적 설정 생성
- Secrets 환경별 분리 관리

---

## 🔨 빌드 및 테스트 전략

### 1. Matrix Strategy (병렬 실행)

**전략 개요**
```yaml
strategy:
  fail-fast: false
  matrix:
    mix_env: [dev, test]
    ecto: [noop, ecto.reset, ecto.empty]
    cpu: [2, 4]
    include:
      - mix_env: test
        ecto: ecto.reset
        cpu: 4
```

**장점:**
- 여러 조건 동시 테스트
- 빠른 피드백 루프
- 환경별 최적화 가능

**단점:**
- 복잡한 매트릭스 관리
- 리소스 사용량 증가
- 디버깅 복잡성

**MES 적용 예시:**
```yaml
strategy:
  matrix:
    python-version: [3.11, 3.12]
    node-version: [18, 20, 23]
    database: [mysql, postgresql]
```

### 2. 조건부 스킵 메커니즘

**전략 개요**
```yaml
if: ${{! contains(github.event.head_commit.message, 'skip-check')}}
```

**활용 사례:**
```yaml
# 다양한 스킵 조건들
skip-check: CI 테스트 스킵
skip-build: 빌드 단계 스킵  
skip-deploy: 배포 스킵
docs-only: 문서 변경만 (전체 스킵)
```

**장점:**
- 불필요한 실행 방지
- 개발자 제어 가능
- 리소스 절약

### 3. 멀티 환경 테스트

**Dev 환경 검증:**
```yaml
# 코드 품질 검사
- run: mix format --check-formatted
- run: mix dialyzer  # 정적 분석
- run: mix compile --all-warnings --warnings-as-errors
```

**Test 환경 검증:**
```yaml
# 실제 테스트 실행
- run: mix ecto.reset  # 데이터베이스 리셋
- run: mix test --cover --exclude fragile
```

---

## 🚀 배포 전략

### 1. 조건부 배포 시스템

**Run Number 기반 배포**
```yaml
if: >
  (endsWith(format('{0}', github.run_number), 0) || 
   endsWith(format('{0}', github.run_number), 3) || 
   endsWith(format('{0}', github.run_number), 6))
```

**분석:**
- **목적**: 모든 커밋마다 배포하지 않음
- **패턴**: 10번 중 3번만 배포 (30% 확률)
- **장점**: 환경 안정성, 리소스 절약
- **단점**: 예측 불가능한 배포 타이밍

**커밋 메시지 기반 배포**
```yaml
# 강제 배포 트리거
|| contains(github.event.head_commit.message, 'reset-alpha')
|| contains(github.event.head_commit.message, 'deploy-beta')
```

**MES 적용 제안:**
```yaml
# 커밋 메시지 패턴
deploy: production  # 프로덕션 강제 배포
deploy: staging     # 스테이징 배포
hotfix: critical    # 긴급 패치 배포
skip: deploy        # 배포 스킵
```

### 2. 워크플로우 재사용 시스템

**Reusable Workflow 구조**
```yaml
# _deploy.yml (재사용 가능한 워크플로우)
on:
  workflow_call:
    inputs:
      target: { type: string, required: true }
      drop-db: { type: boolean, required: true }
```

**호출하는 쪽**
```yaml
jobs:
  alpha:
    uses: ./.github/workflows/_deploy.yml
    with:
      target: alpha
      drop-db: true
    secrets: inherit
```

**장점:**
- 코드 중복 제거
- 일관된 배포 프로세스
- 유지보수성 향상

### 3. 마이크로서비스 배포 오케스트레이션

**서비스별 선택적 배포**
```yaml
inputs:
  worker: { type: boolean, default: true }
  auth: { type: boolean, default: true }
  pig: { type: boolean, default: true }
  # ... 각 서비스별 플래그
```

**단계적 배포 프로세스**
```yaml
jobs:
  1. build-worker      # Worker 먼저 빌드
  2. build-web         # 웹 서비스들 병렬 빌드
  3. drop-db           # 필요시 DB 초기화
  4. deploy-worker     # Worker 먼저 배포
  5. deploy-web        # 웹 서비스들 병렬 배포
```

---

## ⚡ 리소스 최적화 전략

### 1. 고성능 러너 활용

**BuildJet 러너 사용**
```yaml
runs-on: buildjet-${{matrix.cpu}}vcpu-ubuntu-2204
timeout-minutes: 30
```

**성능 비교:**
- GitHub 표준: ~6-10분 (일반적인 빌드)
- BuildJet: ~1-2분 (최대 10배 빠름)
- 비용: 약간 증가하지만 시간 단축 효과 큰

### 2. 지능형 캐싱 전략

**날짜 기반 캐싱**
```yaml
- name: Get current date
  id: date
  run: echo "date=$(date +'%Y-%m-%d')" >> $GITHUB_OUTPUT

- name: Cache
  uses: buildjet/cache@v4.0.0
  with:
    key: ${{runner.os}}-${{env.otp}}-${{env.elixir}}-${{hashFiles('**/mix.lock')}}-${{steps.date.outputs.date}}
```

**캐시 전략 분석:**
- **일별 캐시**: 매일 새로운 캐시로 일관성 보장
- **의존성 해시**: mix.lock 변경 시에만 캐시 무효화
- **조건부 캐시**: 재시도 횟수 제한으로 무한루프 방지

**MES 프로젝트 캐시 최적화:**
```yaml
cache_paths:
  backend: 
    - ~/.cache/pip
    - backend/.pytest_cache
  frontend:
    - ~/.npm
    - frontend/node_modules
```

### 3. 조건부 실행으로 리소스 절약

**재시도 제한**
```yaml
if: github.run_attempt < 3  # 3번 이상 재시도 시 캐시 스킵
```

**조건부 서비스 실행**
```yaml
services:
  postgres:
    if: matrix.mix_env == 'test'  # 테스트 환경에서만 DB 실행
```

---

## 📊 모니터링 및 품질 관리

### 1. 코드 커버리지 자동화

**Codecov 연동**
```yaml
- uses: codecov/codecov-action@v3.1.1
  if: matrix.mix_env == 'test'
  with:
    token: ${{secrets.CODECOV_TOKEN}}
```

**MES 프로젝트 적용:**
```yaml
# 백엔드 커버리지
- run: pytest --cov=core --cov-report=xml
- uses: codecov/codecov-action@v4
  with:
    file: coverage.xml
    flags: backend
    
# 프론트엔드 커버리지 (계획)
- run: npm run test:coverage
- uses: codecov/codecov-action@v4
  with:
    file: frontend/coverage/lcov.info
    flags: frontend
```

### 2. 품질 게이트 시스템

**다단계 검증**
```yaml
quality_gates:
  1. 코드 포맷팅: mix format --check-formatted
  2. 컴파일 경고: --warnings-as-errors
  3. 정적 분석: mix dialyzer
  4. 테스트 커버리지: --cover
  5. 보안 스캔: 계획 중
```

---

## ⚗️ Elixir 특화 전략

> **주의**: 이 섹션의 전략들은 Elixir/Phoenix 프레임워크 전용입니다.

### 1. Mix 환경 관리

**Elixir 전용:**
```yaml
env:
  MIX_ENV: ${{matrix.mix_env}}  # dev, test, prod
  
# 환경별 명령어
- run: mix setup                    # dev 환경 설정
- run: mix ecto.reset              # test DB 리셋  
- run: mix compile --warnings-as-errors
```

**타 언어 등가물:**
- **Django**: `DJANGO_SETTINGS_MODULE`
- **Rails**: `RAILS_ENV`
- **Node.js**: `NODE_ENV`

### 2. Dialyzer 정적 분석

**Elixir 전용:**
```yaml
- run: mix dialyzer
```

**특징:**
- Erlang VM의 타입 시스템 활용
- 런타임 에러를 컴파일 타임에 감지
- 초기 설정 복잡하지만 매우 강력

**타 언어 등가물:**
- **Python**: mypy, pylint
- **JavaScript**: ESLint, TypeScript
- **Java**: SpotBugs, PMD

### 3. OTP/Elixir 버전 관리

**Elixir 전용:**
```yaml
- uses: erlef/setup-beam@v1.17.2
  with:
    otp-version: ${{env.otp}}      # Erlang OTP
    elixir-version: ${{env.elixir}} # Elixir
```

**특이점:**
- Erlang OTP와 Elixir 버전 조합 중요
- 호환성 매트릭스 존재

### 4. Phoenix/Ecto 특화 명령어

**Elixir/Phoenix 전용:**
```yaml
- run: mix ecto.reset        # DB 스키마 리셋
- run: mix ecto.empty        # 빈 DB로 테스트
- run: mix test --exclude fragile  # 불안정한 테스트 제외
```

---

## 📅 스케줄링 전략

### 1. 자동화된 야간 배포

**스케줄 설정**
```yaml
on:
  schedule:
    - cron: "0 21 * * *"    # 매일 밤 9시 (KST)
    - cron: "10 15 * * *"   # 매일 자정 10분 (UTC)
```

**야간 배포 장점:**
- 사용자 영향 최소화
- 문제 발생 시 다음날 대응 가능
- 자동화된 최신 코드 반영

**야간 작업 구성:**
```yaml
jobs:
  1. daily-jobs           # 데이터 정리, 백업 등
  2. destroy-builders     # 리소스 정리
  3. deploy-alpha         # 알파 환경 재배포
  4. deploy-beta          # 베타 환경 업데이트
```

### 2. 리소스 정리 자동화

**Build 머신 정리**
```yaml
destroy-builders:
  uses: ./.github/workflows/_fly-destroy-builders.yml
```

**목적:**
- 미사용 빌드 캐시 정리
- 컴퓨팅 리소스 비용 절약
- 다음날 콜드 스타트로 깨끗한 환경

---

## 🎯 MES 프로젝트 적용 가이드

### 단계별 도입 계획

#### Phase 1: 기본 최적화 (현재 → 1주차)
```yaml
✅ 현재 구현됨:
- 기본 CI/CD 파이프라인
- 백엔드 테스트 + 70% 커버리지
- EC2 자동 배포

🔄 개선 예정:
- Node.js 버전 통일 (23.7)
- 프론트엔드/백엔드 병렬 실행
- 고급 캐싱 전략 도입
```

#### Phase 2: 환경 분리 (2주차)
```yaml
📋 구현 계획:
- staging 환경 추가
- 환경별 설정 분리
- 조건부 배포 도입

🎯 목표:
environments:
  - develop → staging (자동)
  - main → production (테스트 통과 후)
```

#### Phase 3: 고급 전략 (3-4주차)  
```yaml
🚀 고급 기능:
- Matrix 전략으로 병렬화
- 커밋 메시지 기반 배포 제어
- 자동화된 야간 배포
- 워크플로우 재사용 시스템
```

### 구체적인 구현 예시

#### MES용 Matrix 전략
```yaml
strategy:
  fail-fast: false
  matrix:
    include:
      - name: "Backend Tests"
        path: "backend"
        command: "pytest --cov=core"
        
      - name: "Frontend Build"  
        path: "frontend"
        command: "npm run build"
        
      - name: "Integration Tests"
        depends: ["Backend Tests", "Frontend Build"]
        command: "pytest backend/tests/integration/"
```

#### 커밋 메시지 제어 시스템
```yaml
# 배포 제어
deploy-rules:
  - "[deploy:prod]" → 프로덕션 강제 배포
  - "[deploy:staging]" → 스테이징 배포
  - "[skip:deploy]" → 배포 건너뛰기
  - "[hotfix]" → 긴급 배포 (모든 검증 스킵)
  
# 테스트 제어  
test-rules:
  - "[skip:tests]" → 테스트 건너뛰기
  - "[skip:frontend]" → 프론트엔드 테스트만 스킵
  - "[skip:backend]" → 백엔드 테스트만 스킵
```

#### 스케줄링 도입
```yaml
# 야간 정기 배포 (주 3회)
schedule:
  - cron: "0 22 * * 1,3,5"  # 월/수/금 밤 10시
    jobs: [deploy-staging]
    
# 주말 전체 시스템 점검  
  - cron: "0 23 * * 0"      # 일요일 밤 11시
    jobs: [full-system-check, deploy-all-environments]
```

### 예상 효과

#### 성능 개선
- **빌드 시간**: 10분 → 5분 (병렬화)
- **배포 안정성**: 90% → 98% (단계적 검증)
- **개발 속도**: 30% 향상 (빠른 피드백)

#### 비용 최적화  
- **GitHub Actions 사용량**: 50% 절약 (조건부 실행)
- **AWS 비용**: staging 환경으로 20% 증가
- **개발자 시간**: 40% 절약 (자동화)

---

## 📚 참고 자료

### 도구별 공식 문서
- [GitHub Actions 매트릭스 전략](https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs)
- [Reusable Workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)  
- [Environment 보호 규칙](https://docs.github.com/en/actions/deployment/targeting-different-environments)

### 성능 도구
- [BuildJet - 고성능 러너](https://buildjet.com/)
- [Codecov - 커버리지 분석](https://codecov.io/)
- [GitHub Actions 사용량 모니터링](https://github.com/settings/billing)

### 모범 사례
- [GitHub Actions 보안](https://docs.github.com/en/actions/security-guides)
- [워크플로우 최적화](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [시크릿 관리](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

---

## 🔄 업데이트 이력

- **2025-01-09**: 초기 문서 작성, Examples 워크플로우 분석 완료
- **계획**: MES 프로젝트 단계별 적용 후 실전 경험 추가 예정

---

> 이 문서는 `.github/workflows/examples/` 의 실제 프로덕션 워크플로우를 분석하여 작성되었습니다.  
> 각 전략의 실제 적용 시에는 프로젝트 특성에 맞게 조정이 필요합니다.