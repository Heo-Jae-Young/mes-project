# Database Setup Guide

이 문서는 HACCP MES 프로젝트의 데이터베이스 초기 설정부터 운영까지의 전체 과정을 설명합니다.

## 📋 Database Architecture

### Technology Stack
- **Database**: MariaDB 10.6 (MySQL 호환)
- **Container**: Docker Compose
- **ORM**: Django ORM
- **Migration**: Django Migration System

### Database Schema Overview
```
mes_db (Database)
├── auth_* (Django 기본 테이블들)
├── core_user (사용자 관리)
├── core_supplier (공급업체)
├── core_rawmaterial (원자재)
├── core_materiallot (원자재 LOT)
├── core_finishedproduct (완성품)
├── core_productionorder (생산 주문)
├── core_ccp (중요관리점)
└── core_ccplog (HACCP 로그 - 불변)
```

## 🚀 Initial Database Setup

### 1. Docker 환경 준비
```bash
# Docker 및 Docker Compose 설치 확인
docker --version
docker-compose --version

# MariaDB 컨테이너 시작
docker-compose up -d db
```

**docker-compose.yml 구성:**
```yaml
services:
  db:
    image: mariadb:10.6
    container_name: mes-mariadb
    environment:
      MYSQL_ROOT_PASSWORD: root123
      MYSQL_DATABASE: mes_db
      MYSQL_USER: mes_user
      MYSQL_PASSWORD: mes_password
    ports:
      - "3306:3306"
    volumes:
      - mariadb_data:/var/lib/mysql
    restart: unless-stopped

volumes:
  mariadb_data:
```

### 2. Django Backend 설정
```bash
# 백엔드 디렉토리로 이동
cd backend

# 가상환경 활성화
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 3. Environment Variables 설정
```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 내용 확인/수정
cat .env
```

**필수 환경변수:**
```bash
SECRET_KEY="your-secret-key-here"
DEBUG=True
DATABASE_NAME=mes_db
DATABASE_USER=mes_user
DATABASE_PASSWORD=mes_password
DATABASE_HOST=127.0.0.1  # 중요: localhost가 아닌 127.0.0.1 사용
DATABASE_PORT=3306
```

### 4. Database Connection 테스트
```bash
# Django 설정 검증
python manage.py check

# 데이터베이스 연결 테스트
python manage.py dbshell
# MariaDB 프롬프트가 나타나면 성공
# 종료: \q
```

### 5. Initial Migration
```bash
# Django 기본 마이그레이션 실행
python manage.py migrate

# 커스텀 모델 마이그레이션
python manage.py makemigrations core
python manage.py migrate core
```

**마이그레이션 성공 확인:**
```bash
# 마이그레이션 상태 확인
python manage.py showmigrations

# 예상 출력:
# admin
#  [X] 0001_initial
#  [X] 0002_logentry_remove_auto_add
# auth  
#  [X] 0001_initial
#  ...
# core
#  [X] 0001_initial
```

### 6. Test 권한 설정 (테스트용)
```bash
# MariaDB 컨테이너 접속
docker exec -it mes-mariadb mysql -u root -proot123

# 테스트 DB 생성 권한 부여
GRANT ALL PRIVILEGES ON *.* TO 'mes_user'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EXIT;
```

### 7. Sample Data 로드
```bash
# 관리자 계정 및 샘플 데이터 생성
python manage.py seed_data --clear

# 성공 메시지 확인:
# ✅ 관리자 계정 생성: admin/admin123
# ✅ 사용자 6개 생성
# ✅ 공급업체 3개 생성
# ...
```

## 🔄 Database Management Commands

### Daily Operations
```bash
# 개발 서버 시작
python manage.py runserver

# 새로운 마이그레이션 생성
python manage.py makemigrations

# 마이그레이션 실행
python manage.py migrate

# 관리자 계정 생성 (추가)
python manage.py createsuperuser
```

### Data Management
```bash
# 시드 데이터 재로드 (기존 데이터 유지)
python manage.py seed_data

# 시드 데이터 완전 재생성 (기존 데이터 삭제)
python manage.py seed_data --clear

# 모든 데이터 삭제 (스키마 유지)
python manage.py flush

# 특정 앱 데이터만 삭제
python manage.py flush --exclude=auth
```

### Database Inspection
```bash
# 데이터베이스 직접 접속
docker exec -it mes-mariadb mysql -u mes_user -p

# SQL 쿼리 실행
python manage.py dbshell

# 모델 구조 확인
python manage.py inspectdb > db_structure.py
```

## 🆘 Complete Database Reset

### 전체 데이터베이스 초기화 (주의!)
```bash
# 1. 모든 서버 중지
./stop_servers.sh

# 2. Docker 볼륨 포함 완전 삭제
docker-compose down -v
docker volume prune -f

# 3. 데이터베이스 재시작
docker-compose up -d db

# 4. 마이그레이션 재실행
cd backend
source venv/bin/activate
python manage.py migrate

# 5. 시드 데이터 로드
python manage.py seed_data --clear

# 6. 서버 재시작
./restart_servers.sh
```

## 🐛 Common Issues & Solutions

### 1. Database Connection Issues

**문제:** `django.db.utils.OperationalError: (2003, "Can't connect to MySQL server")`

**해결방법:**
```bash
# Docker 컨테이너 상태 확인
docker ps | grep mariadb

# 컨테이너 로그 확인
docker logs mes-mariadb

# 네트워크 연결 테스트
telnet localhost 3306

# 환경변수 확인
echo $DATABASE_HOST  # 반드시 127.0.0.1이어야 함
```

### 2. Migration Conflicts

**문제:** `django.db.migrations.exceptions.InconsistentMigrationHistory`

**해결방법:**
```bash
# 1. 마이그레이션 히스토리 확인
python manage.py showmigrations

# 2. 충돌하는 마이그레이션 롤백
python manage.py migrate core 0001

# 3. 문제 마이그레이션 파일 삭제 후 재생성
rm core/migrations/0002_*.py
python manage.py makemigrations core
python manage.py migrate
```

### 3. Permission Denied for Tests

**문제:** `Access denied for user 'mes_user'@'%' to database 'test_mes_db'`

**해결방법:**
```bash
# MariaDB 루트로 접속하여 권한 부여
docker exec -it mes-mariadb mysql -u root -proot123
GRANT ALL PRIVILEGES ON *.* TO 'mes_user'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
```

### 4. Docker Volume Issues

**문제:** 데이터베이스 데이터가 사라짐

**해결방법:**
```bash
# 볼륨 상태 확인
docker volume ls | grep mes

# 볼륨 상세 정보
docker volume inspect mes-project_mariadb_data

# 백업 (데이터 손실 방지)
docker exec mes-mariadb mysqldump -u root -proot123 mes_db > backup.sql
```

## 📊 Database Monitoring

### Performance Monitoring
```bash
# 실행 중인 쿼리 확인
docker exec -it mes-mariadb mysql -u root -proot123 -e "SHOW PROCESSLIST;"

# 데이터베이스 크기 확인
docker exec -it mes-mariadb mysql -u root -proot123 -e "
SELECT 
    table_schema AS 'Database',
    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.tables 
WHERE table_schema = 'mes_db'
GROUP BY table_schema;
"

# 테이블별 레코드 수
docker exec -it mes-mariadb mysql -u root -proot123 -e "
SELECT 
    TABLE_NAME,
    TABLE_ROWS
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'mes_db'
ORDER BY TABLE_ROWS DESC;
"
```

### Backup & Restore
```bash
# 전체 데이터베이스 백업
docker exec mes-mariadb mysqldump -u root -proot123 mes_db > mes_backup_$(date +%Y%m%d).sql

# 특정 테이블만 백업
docker exec mes-mariadb mysqldump -u root -proot123 mes_db core_ccplog > ccplog_backup.sql

# 백업에서 복원
docker exec -i mes-mariadb mysql -u root -proot123 mes_db < mes_backup_20250902.sql
```

## 🔒 Security Considerations

### Production Settings
```bash
# 프로덕션 환경변수 (.env.production)
DEBUG=False
DATABASE_PASSWORD=strong-random-password
ALLOWED_HOSTS=your-domain.com,localhost

# 데이터베이스 사용자 권한 최소화
GRANT SELECT, INSERT, UPDATE, DELETE ON mes_db.* TO 'mes_user'@'%';
REVOKE ALL PRIVILEGES ON *.* FROM 'mes_user'@'%';
```

### Data Protection
```bash
# 중요 테이블 백업 자동화 (crontab)
0 2 * * * /usr/local/bin/docker exec mes-mariadb mysqldump -u root -proot123 mes_db core_ccplog > /backup/ccplog_$(date +\%Y\%m\%d).sql

# 로그 파일 로테이션
logrotate -f /etc/logrotate.d/mysql
```

이 가이드를 따라하면 데이터베이스 설정부터 운영까지 모든 과정을 안전하게 수행할 수 있습니다.