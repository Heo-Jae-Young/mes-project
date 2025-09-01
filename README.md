# 식품 MES SaaS 프로젝트

HACCP 기반 식품 안전 규정 준수를 위한 제조 실행 시스템(MES) SaaS 플랫폼

## 🎯 프로젝트 개요

식품 제조업체를 위한 디지털 HACCP 관리 시스템으로, 7가지 HACCP 원칙을 중심으로 구축된 제조 실행 관리 플랫폼입니다.

### 핵심 기능
- 🔍 **HACCP 중요관리점(CCP) 모니터링**
- 📊 **실시간 생산 관리 및 추적**
- 🏭 **원자재부터 완제품까지 전체 추적성**
- 👥 **역할 기반 사용자 관리**
- 📋 **규정 준수 보고서 생성**

## 🛠 기술 스택

**Backend:**
- Django 5.2.5 + Django REST Framework
- JWT Authentication
- MariaDB
- Python 3.12.7

**Frontend (예정):**
- React 18+
- Axios

**Infrastructure:**
- Docker Compose
- Nginx (배포용)

## 🚀 빠른 시작

### 사전 요구사항
- Docker & Docker Compose
- Python 3.12.7

### 설치 및 실행

```bash
# 1. 레포지토리 클론
git clone [repository-url]
cd mes-project

# 2. 환경 변수 설정
cp backend/.env.example backend/.env
# .env 파일의 SECRET_KEY를 실제 값으로 수정

# 3. MariaDB 시작
docker-compose up -d db

# 4. 백엔드 설정
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 5. 데이터베이스 마이그레이션
python manage.py migrate

# 6. 개발 서버 실행
python manage.py runserver
```

서버가 실행되면 http://127.0.0.1:8000 에서 확인 가능합니다.

## 📖 문서

- [CLAUDE.md](./CLAUDE.md) - 개발 가이드 및 아키텍처 문서
- [식품 MES SaaS 프로젝트 기획 및 개발.txt](./식품%20MES%20SaaS%20프로젝트%20기획%20및%20개발.txt) - 상세 기획서

## 🗂 프로젝트 구조

```
mes-project/
├── backend/                 # Django 백엔드
│   ├── mes_backend/         # Django 프로젝트 설정
│   ├── core/                # 핵심 앱 (모델, API)
│   ├── requirements.txt     # Python 의존성
│   └── .env.example        # 환경변수 템플릿
├── frontend/               # React 프론트엔드 (예정)
├── docker-compose.yml      # 개발환경 설정
└── docs/                  # 프로젝트 문서
```

## 🏗 개발 상태

- [x] Django 백엔드 초기 설정
- [x] MariaDB Docker 환경 구성
- [x] 기본 인증 시스템 설정
- [ ] HACCP 데이터 모델 구현
- [ ] REST API 개발
- [ ] React 프론트엔드 구현
- [ ] Docker 컨테이너화 완료

## 📋 주요 명령어

```bash
# 데이터베이스 관련
python manage.py makemigrations  # 마이그레이션 파일 생성
python manage.py migrate         # 마이그레이션 적용
python manage.py createsuperuser # 관리자 계정 생성

# 개발 서버
python manage.py runserver       # 개발 서버 실행
python manage.py check          # 설정 검증

# Docker
docker-compose up -d db         # MariaDB만 실행
docker-compose ps              # 컨테이너 상태 확인
docker-compose logs db         # MariaDB 로그 확인
```

## 🤝 기여 방법

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 문의

프로젝트 관련 문의사항이 있으시면 Issue를 생성해 주세요.