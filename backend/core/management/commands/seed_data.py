from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
import uuid

from core.models import (
    User, Supplier, RawMaterial, MaterialLot,
    FinishedProduct, ProductionOrder, CCP, CCPLog
)


class Command(BaseCommand):
    help = 'HACCP MES 시스템 시드 데이터 생성'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='기존 데이터를 모두 삭제하고 새로 생성',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('기존 데이터 삭제 중...')
            self.clear_data()

        self.stdout.write('시드 데이터 생성 시작...')
        
        with transaction.atomic():
            # 1. 사용자 생성
            users = self.create_users()
            self.stdout.write(f'✓ 사용자 {len(users)}명 생성')
            
            # 2. 공급업체 생성
            suppliers = self.create_suppliers(users)
            self.stdout.write(f'✓ 공급업체 {len(suppliers)}개 생성')
            
            # 3. 원자재 생성
            raw_materials = self.create_raw_materials(suppliers, users)
            self.stdout.write(f'✓ 원자재 {len(raw_materials)}개 생성')
            
            # 4. 원자재 로트 생성
            material_lots = self.create_material_lots(raw_materials, suppliers, users)
            self.stdout.write(f'✓ 원자재 로트 {len(material_lots)}개 생성')
            
            # 5. 완제품 생성
            finished_products = self.create_finished_products(users)
            self.stdout.write(f'✓ 완제품 {len(finished_products)}개 생성')
            
            # 6. 생산 주문 생성
            production_orders = self.create_production_orders(finished_products, users)
            self.stdout.write(f'✓ 생산 주문 {len(production_orders)}개 생성')
            
            # 7. CCP 생성
            ccps = self.create_ccps(finished_products, users)
            self.stdout.write(f'✓ CCP {len(ccps)}개 생성')
            
            # 8. CCP 로그 생성
            ccp_logs = self.create_ccp_logs(ccps, production_orders, users)
            self.stdout.write(f'✓ CCP 로그 {len(ccp_logs)}개 생성')

        self.stdout.write(
            self.style.SUCCESS('시드 데이터 생성 완료! 🎉')
        )

    def clear_data(self):
        """기존 데이터 삭제"""
        CCPLog.objects.all().delete()
        CCP.objects.all().delete()
        ProductionOrder.objects.all().delete()
        MaterialLot.objects.all().delete()
        RawMaterial.objects.all().delete()
        FinishedProduct.objects.all().delete()
        Supplier.objects.all().delete()
        # admin 계정은 유지
        User.objects.exclude(username='admin').delete()

    def create_users(self):
        """테스트 사용자 생성 (admin 계정 포함)"""
        # 1. admin 계정 먼저 생성/업데이트
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@mes.com',
                'role': 'admin',
                'department': '관리팀',
                'employee_id': 'EMP000',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created or not admin_user.check_password('admin123'):
            admin_user.set_password('admin123')
            admin_user.save()
        
        users_data = [
            {'username': 'quality_manager', 'email': 'quality@mes.com', 'role': 'quality_manager', 'department': '품질관리팀'},
            {'username': 'production_manager', 'email': 'production@mes.com', 'role': 'production_manager', 'department': '생산팀'},
            {'username': 'operator1', 'email': 'operator1@mes.com', 'role': 'operator', 'department': '생산1팀'},
            {'username': 'operator2', 'email': 'operator2@mes.com', 'role': 'operator', 'department': '생산2팀'},
            {'username': 'auditor', 'email': 'auditor@mes.com', 'role': 'auditor', 'department': '감사팀'},
        ]
        
        users = [admin_user]  # admin을 첫 번째로
        for i, user_data in enumerate(users_data):
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'role': user_data['role'],
                    'department': user_data['department'],
                    'employee_id': f"EMP{i + 1:03d}",
                    'is_staff': True,
                }
            )
            if created:
                user.set_password('test123')
                user.save()
            users.append(user)
        
        return users

    def create_suppliers(self, users):
        """공급업체 생성"""
        suppliers_data = [
            {
                'name': '대한농산', 'code': 'SUP001', 'contact_person': '김농산', 
                'email': 'contact@daehannongsan.co.kr', 'phone': '02-1234-5678',
                'address': '서울시 강남구 농산로 123', 'certification': 'HACCP, ISO22000',
            },
            {
                'name': '신선포장재', 'code': 'SUP002', 'contact_person': '박포장', 
                'email': 'info@freshpack.co.kr', 'phone': '031-987-6543',
                'address': '경기도 수원시 포장동 456', 'certification': 'ISO9001, FSC',
            },
            {
                'name': '글로벌향료', 'code': 'SUP003', 'contact_person': '이향료', 
                'email': 'sales@globalflavor.com', 'phone': '02-555-7777',
                'address': '인천시 연수구 향료로 789', 'certification': 'HACCP, FDA',
            },
        ]
        
        suppliers = []
        for supplier_data in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                code=supplier_data['code'],
                defaults={
                    **supplier_data,
                    'created_by': users[0]
                }
            )
            suppliers.append(supplier)
        
        return suppliers

    def create_raw_materials(self, suppliers, users):
        """원자재 생성"""
        raw_materials_data = [
            {
                'name': '국산 쌀', 'code': 'RM001', 'category': 'ingredient',
                'description': '2024년산 국산 쌀', 'unit': 'kg',
                'storage_temp_min': Decimal('10.0'), 'storage_temp_max': Decimal('25.0'),
                'shelf_life_days': 365, 'supplier': suppliers[0]
            },
            {
                'name': '비닐 포장지', 'code': 'RM002', 'category': 'packaging',
                'description': 'PE 소재 식품용 포장지', 'unit': 'roll',
                'storage_temp_min': Decimal('5.0'), 'storage_temp_max': Decimal('30.0'),
                'shelf_life_days': 730, 'supplier': suppliers[1]
            },
            {
                'name': '천연 바닐라 향료', 'code': 'RM003', 'category': 'additive',
                'description': '천연 바닐라 추출물', 'unit': 'L',
                'storage_temp_min': Decimal('2.0'), 'storage_temp_max': Decimal('8.0'),
                'shelf_life_days': 540, 'allergens': '없음', 'supplier': suppliers[2]
            },
            {
                'name': '식용 색소 (적색)', 'code': 'RM004', 'category': 'additive',
                'description': '식품첨가물 적색 색소', 'unit': 'kg',
                'storage_temp_min': Decimal('10.0'), 'storage_temp_max': Decimal('25.0'),
                'shelf_life_days': 720, 'supplier': suppliers[2]
            },
        ]
        
        raw_materials = []
        for rm_data in raw_materials_data:
            raw_material, created = RawMaterial.objects.get_or_create(
                code=rm_data['code'],
                defaults={
                    **rm_data,
                    'created_by': users[0]
                }
            )
            raw_materials.append(raw_material)
        
        return raw_materials

    def create_material_lots(self, raw_materials, suppliers, users):
        """원자재 로트 생성"""
        material_lots = []
        
        for i, raw_material in enumerate(raw_materials):
            # 각 원자재마다 2-3개 로트 생성
            for j in range(2 + i % 2):
                lot_number = f"LOT{raw_material.code[-3:]}{j+1:02d}{timezone.now().strftime('%m%d')}"
                received_date = timezone.now() - timedelta(days=j*7)
                expiry_date = received_date.date() + timedelta(days=raw_material.shelf_life_days)
                
                material_lot = MaterialLot.objects.create(
                    lot_number=lot_number,
                    raw_material=raw_material,
                    supplier=raw_material.supplier,
                    received_date=received_date,
                    expiry_date=expiry_date,
                    quantity_received=Decimal(str(100.0 + j * 50)),
                    quantity_current=Decimal(str(80.0 + j * 30)),
                    unit_price=Decimal(str(1000 + i * 500 + j * 100)),
                    quality_test_passed=True,
                    quality_test_date=received_date + timedelta(hours=2),
                    quality_test_notes='정상 통과',
                    storage_location=f'창고-{chr(65 + i)}-{j+1:02d}',
                    temperature_at_receipt=Decimal(str(15.0 + i * 2)),
                    created_by=users[1]
                )
                material_lots.append(material_lot)
        
        return material_lots

    def create_finished_products(self, users):
        """완제품 생성"""
        finished_products_data = [
            {
                'name': '프리미엄 쌀과자', 'code': 'FP001',
                'description': '100% 국산쌀로 만든 건강한 과자',
                'shelf_life_days': 180, 'net_weight': Decimal('150.0'),
                'packaging_type': '개별 비닐포장', 'allergen_info': '없음',
                'nutrition_facts': {
                    'calories': 380, 'protein': 8.5, 'fat': 2.1, 
                    'carbs': 82.3, 'sodium': 450
                }
            },
            {
                'name': '바닐라 쿠키', 'code': 'FP002',
                'description': '천연 바닐라 향이 일품인 수제 쿠키',
                'shelf_life_days': 90, 'net_weight': Decimal('200.0'),
                'packaging_type': '플라스틱 용기', 'allergen_info': '밀, 계란, 우유',
                'nutrition_facts': {
                    'calories': 520, 'protein': 6.8, 'fat': 28.5,
                    'carbs': 62.1, 'sodium': 320
                }
            },
        ]
        
        finished_products = []
        for fp_data in finished_products_data:
            finished_product, created = FinishedProduct.objects.get_or_create(
                code=fp_data['code'],
                defaults={
                    **fp_data,
                    'created_by': users[1]
                }
            )
            finished_products.append(finished_product)
        
        return finished_products

    def create_production_orders(self, finished_products, users):
        """생산 주문 생성"""
        production_orders = []
        
        for i, finished_product in enumerate(finished_products):
            for j in range(3):  # 각 제품마다 3개 주문
                order_number = f"PO{finished_product.code[-3:]}{timezone.now().strftime('%y%m')}{j+1:02d}"
                planned_start = timezone.now() + timedelta(days=j*3)
                planned_end = planned_start + timedelta(days=2)
                
                status_choices = ['planned', 'in_progress', 'completed']
                status = status_choices[j % len(status_choices)]
                
                production_order = ProductionOrder.objects.create(
                    order_number=order_number,
                    finished_product=finished_product,
                    planned_quantity=1000 + j * 500,
                    produced_quantity=0 if status == 'planned' else (800 if status == 'in_progress' else 1000),
                    planned_start_date=planned_start,
                    planned_end_date=planned_end,
                    actual_start_date=planned_start if status != 'planned' else None,
                    actual_end_date=planned_end if status == 'completed' else None,
                    status=status,
                    priority='normal' if j % 2 == 0 else 'high',
                    notes=f'{finished_product.name} 생산 주문',
                    assigned_operator=users[2 + j % 2],  # operator1 or operator2
                    created_by=users[1]  # production_manager
                )
                production_orders.append(production_order)
        
        return production_orders

    def create_ccps(self, finished_products, users):
        """CCP 생성"""
        ccps_data = [
            {
                'name': '가열 온도 관리', 'code': 'CCP001', 'ccp_type': 'temperature',
                'description': '쌀과자 제조시 가열 온도 중요관리점',
                'process_step': '가열 공정', 'critical_limit_min': Decimal('80.0'),
                'critical_limit_max': Decimal('90.0'), 'monitoring_frequency': '매 30분',
                'corrective_action': '온도 재조정 후 재가열', 'responsible_person': '생산팀장',
                'monitoring_method': '디지털 온도계로 측정', 'verification_method': '일일 온도계 교정',
                'record_keeping': 'CCP 모니터링 일지 작성', 'finished_product': finished_products[0]
            },
            {
                'name': '금속 이물질 검출', 'code': 'CCP002', 'ccp_type': 'metal_detection',
                'description': '완제품 포장전 금속 이물질 검출',
                'process_step': '포장 공정', 'critical_limit_min': None,
                'critical_limit_max': Decimal('0.0'), 'monitoring_frequency': '전수 검사',
                'corrective_action': '해당 제품 격리 및 재검사', 'responsible_person': '품질관리자',
                'monitoring_method': '금속 검출기 통과', 'verification_method': '주간 검출기 성능 점검',
                'record_keeping': '금속 검출 로그 기록', 'finished_product': None  # 모든 제품 적용
            },
            {
                'name': '쿠키 굽기 온도', 'code': 'CCP003', 'ccp_type': 'temperature',
                'description': '바닐라 쿠키 굽기 온도 관리',
                'process_step': '굽기 공정', 'critical_limit_min': Decimal('160.0'),
                'critical_limit_max': Decimal('180.0'), 'monitoring_frequency': '매 15분',
                'corrective_action': '온도 조정 및 굽기 시간 연장', 'responsible_person': '베이킹팀장',
                'monitoring_method': '오븐 내부 온도 센서', 'verification_method': '온도 센서 일일 점검',
                'record_keeping': '굽기 온도 기록지', 'finished_product': finished_products[1]
            },
        ]
        
        ccps = []
        for ccp_data in ccps_data:
            ccp, created = CCP.objects.get_or_create(
                code=ccp_data['code'],
                defaults={
                    **ccp_data,
                    'created_by': users[0]  # quality_manager
                }
            )
            ccps.append(ccp)
        
        return ccps

    def create_ccp_logs(self, ccps, production_orders, users):
        """CCP 모니터링 로그 생성"""
        ccp_logs = []
        
        for ccp in ccps:
            # 지난 7일간 데이터 생성
            for day in range(7):
                date = timezone.now() - timedelta(days=day)
                
                # 하루에 8-12회 측정
                measurements_per_day = 8 + day % 5
                
                for hour in range(0, 24, 24 // measurements_per_day):
                    measured_at = date.replace(hour=hour, minute=0, second=0)
                    
                    # 측정값 시뮬레이션
                    if ccp.ccp_type == 'temperature':
                        # 온도 측정: 보통 정상 범위, 가끔 이탈
                        base_temp = (ccp.critical_limit_min + ccp.critical_limit_max) / 2
                        variation = Decimal(str(-5 + (hour % 11)))  # -5 ~ +5 변동
                        measured_value = base_temp + variation
                        unit = '°C'
                    elif ccp.ccp_type == 'metal_detection':
                        # 금속 검출: 99% 정상 (0), 1% 이상 (1)
                        measured_value = Decimal('1.0') if (day + hour) % 100 == 0 else Decimal('0.0')
                        unit = '개'
                    else:
                        measured_value = Decimal('50.0')
                        unit = 'unit'
                    
                    # 생산 주문 연결 (50% 확률)
                    production_order = production_orders[day % len(production_orders)] if day % 2 == 0 else None
                    
                    ccp_log = CCPLog.objects.create(
                        ccp=ccp,
                        production_order=production_order,
                        measured_value=measured_value,
                        unit=unit,
                        measured_at=measured_at,
                        status='within_limits',  # save() 메서드에서 자동 계산
                        is_within_limits=True,  # save() 메서드에서 자동 계산
                        measurement_device=f'{ccp.ccp_type.title()} Sensor #{ccp.code[-1]}',
                        environmental_conditions=f'실내온도: {20 + day}°C, 습도: {45 + hour % 10}%',
                        created_by=users[2 + day % 2]  # operator1 or operator2
                    )
                    
                    # 이상치가 발생한 경우 개선조치 기록
                    if not ccp_log.is_within_limits:
                        ccp_log.deviation_notes = '한계기준 이탈 감지'
                        ccp_log.corrective_action_taken = ccp.corrective_action
                        ccp_log.corrective_action_by = users[0]  # quality_manager
                        ccp_log.verified_by = users[4]  # auditor
                        ccp_log.verification_date = measured_at + timedelta(hours=1)
                        ccp_log.save()
                    
                    ccp_logs.append(ccp_log)
        
        return ccp_logs