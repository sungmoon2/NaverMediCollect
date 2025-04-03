#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NaverMediCollect - src/database/operations.py
생성일: 2025-04-03

데이터베이스 작업을 수행하는 유틸리티 모듈입니다.
데이터 검색, 통계 조회 등의 고급 데이터베이스 작업을 제공합니다.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from mysql.connector import Error

from src.database.connection import DBConnection
from src.database.models import Medicine, MedicineBasicInfo, MedicineDetailedInfo


class DBOperations:
    """데이터베이스 작업 클래스"""
    
    def __init__(self, db_connection: DBConnection = None):
        """
        초기화
        
        Args:
            db_connection (DBConnection, optional): 데이터베이스 연결 객체
        """
        self.logger = logging.getLogger(__name__)
        self.connection = db_connection or DBConnection()
    
    def search_medicines(self, keyword: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        키워드로 의약품 검색
        
        Args:
            keyword (str): 검색 키워드
            limit (int, optional): 결과 제한 수. 기본값 100
            offset (int, optional): 결과 시작 위치. 기본값 0
            
        Returns:
            list: 검색된 의약품 목록
        """
        if not self.connection.connection:
            return []
        
        try:
            cursor = self.connection.connection.cursor(dictionary=True)
            
            # 검색 쿼리
            search_sql = """
            SELECT b.* FROM medicine_basic_info b
            WHERE 
                b.name_ko LIKE %s OR 
                b.name_en LIKE %s OR
                b.company LIKE %s OR
                b.ingredient_info LIKE %s
            ORDER BY b.id DESC
            LIMIT %s OFFSET %s
            """
            
            # 검색 파라미터
            search_param = f'%{keyword}%'
            cursor.execute(search_sql, (search_param, search_param, search_param, search_param, limit, offset))
            
            results = cursor.fetchall()
            return results
            
        except Error as e:
            self.logger.error(f"의약품 검색 오류: {e}")
            return []
            
        finally:
            cursor.close()
    
    def get_medicine_count(self) -> int:
        """
        총 의약품 수 조회
        
        Returns:
            int: 의약품 수
        """
        if not self.connection.connection:
            return 0
        
        try:
            cursor = self.connection.connection.cursor()
            
            # 카운트 쿼리
            count_sql = "SELECT COUNT(*) FROM medicine_basic_info"
            cursor.execute(count_sql)
            
            result = cursor.fetchone()
            return result[0] if result else 0
            
        except Error as e:
            self.logger.error(f"의약품 수 조회 오류: {e}")
            return 0
            
        finally:
            cursor.close()
    
    def get_medicines_by_batch(self, batch_size: int = 50, batch_num: int = 1) -> List[Dict[str, Any]]:
        """
        배치 번호로 의약품 목록 조회
        
        Args:
            batch_size (int, optional): 배치 크기. 기본값 50
            batch_num (int, optional): 배치 번호(1부터 시작). 기본값 1
            
        Returns:
            list: 의약품 목록
        """
        if not self.connection.connection or batch_num < 1:
            return []
        
        offset = (batch_num - 1) * batch_size
        
        try:
            cursor = self.connection.connection.cursor(dictionary=True)
            
            # 의약품 기본 정보 조회
            basic_sql = """
            SELECT * FROM medicine_basic_info
            ORDER BY id
            LIMIT %s OFFSET %s
            """
            
            cursor.execute(basic_sql, (batch_size, offset))
            basic_results = cursor.fetchall()
            
            if not basic_results:
                return []
            
            # 조회된 medicine_id 목록
            medicine_ids = [item['medicine_id'] for item in basic_results]
            
            # 의약품 상세 정보 조회
            placeholders = ', '.join(['%s'] * len(medicine_ids))
            detailed_sql = f"""
            SELECT * FROM medicine_detailed_info
            WHERE medicine_id IN ({placeholders})
            """
            
            cursor.execute(detailed_sql, medicine_ids)
            detailed_results = cursor.fetchall()
            
            # medicine_id를 키로 하는 상세 정보 딕셔너리 생성
            detailed_dict = {item['medicine_id']: item for item in detailed_results}
            
            # 결과 통합
            medicines = []
            for basic in basic_results:
                medicine_id = basic['medicine_id']
                detailed = detailed_dict.get(medicine_id, {})
                
                medicines.append({
                    'basic_info': basic,
                    'detailed_info': detailed
                })
            
            return medicines
            
        except Error as e:
            self.logger.error(f"배치 의약품 조회 오류: {e}")
            return []
            
        finally:
            cursor.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        의약품 데이터 통계 조회
        
        Returns:
            dict: 통계 정보
        """
        if not self.connection.connection:
            return {}
        
        try:
            cursor = self.connection.connection.cursor()
            
            stats = {}
            
            # 총 의약품 수
            cursor.execute("SELECT COUNT(*) FROM medicine_basic_info")
            stats['total_medicines'] = cursor.fetchone()[0]
            
            # 상세 정보가 있는 의약품 수
            cursor.execute("SELECT COUNT(*) FROM medicine_detailed_info")
            stats['medicines_with_details'] = cursor.fetchone()[0]
            
            # 업체별 의약품 수
            cursor.execute("""
                SELECT company, COUNT(*) as count 
                FROM medicine_basic_info 
                GROUP BY company 
                ORDER BY count DESC 
                LIMIT 10
            """)
            stats['top_companies'] = [{'company': row[0], 'count': row[1]} for row in cursor.fetchall()]
            
            # 분류별 의약품 수
            cursor.execute("""
                SELECT category, COUNT(*) as count 
                FROM medicine_basic_info 
                GROUP BY category 
                ORDER BY count DESC 
                LIMIT 10
            """)
            stats['top_categories'] = [{'category': row[0], 'count': row[1]} for row in cursor.fetchall()]
            
            return stats
            
        except Error as e:
            self.logger.error(f"통계 조회 오류: {e}")
            return {}
            
        finally:
            cursor.close()
    
    def export_to_csv(self, file_path: str, fields: List[str] = None) -> bool:
        """
        데이터를 CSV 파일로 내보내기
        
        Args:
            file_path (str): CSV 파일 경로
            fields (list, optional): 내보낼 필드 목록. 기본값 None (모든 필드)
            
        Returns:
            bool: 성공 여부
        """
        if not self.connection.connection:
            return False
        
        try:
            import csv
            
            # 필드 목록이 없으면 기본 필드 사용
            if not fields:
                fields = [
                    'medicine_id', 'name_ko', 'name_en', 'company', 'category',
                    'type', 'insurance_code', 'appearance', 'formulation',
                    'ingredient_info', 'storage_method', 'usage_period'
                ]
            
            # 모든 의약품 조회
            cursor = self.connection.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM medicine_basic_info")
            medicines = cursor.fetchall()
            
            # CSV 파일 작성
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fields)
                writer.writeheader()
                
                for medicine in medicines:
                    # 필드 목록에 있는 필드만 선택
                    row = {field: medicine.get(field, '') for field in fields}
                    writer.writerow(row)
            
            self.logger.info(f"CSV 내보내기 완료: {file_path} ({len(medicines)}개 의약품)")
            return True
            
        except Exception as e:
            self.logger.error(f"CSV 내보내기 오류: {e}")
            return False
            
        finally:
            cursor.close()