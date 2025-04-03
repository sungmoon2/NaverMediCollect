#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NaverMediCollect - src/database/connection.py
생성일: 2025-04-03

데이터베이스 연결 및 쿼리 실행을 담당하는 모듈입니다.
MySQL/MariaDB 연결, 트랜잭션 관리 등의 기능을 제공합니다.
"""

import os
import logging
import mysql.connector
from mysql.connector import Error
from src.data.processor import DataProcessor


class DBConnection:
    """데이터베이스 연결 클래스"""
    
    def __init__(self):
        """초기화 및 DB 연결"""
        self.logger = logging.getLogger(__name__)
        self.processor = DataProcessor()
        
        # DB 설정 로드
        self.host = os.environ.get('MYSQL_HOST', 'localhost')
        self.port = int(os.environ.get('MYSQL_PORT', '3306'))
        self.user = os.environ.get('MYSQL_USER', 'root')
        self.password = os.environ.get('MYSQL_PASSWORD', '')
        self.database = os.environ.get('MYSQL_DATABASE', 'medicine_db')
        self.charset = os.environ.get('MYSQL_CHARSET', 'utf8mb4')
        
        self.connection = None
        self.connect()
    
    def connect(self):
        """데이터베이스 연결"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset=self.charset
            )
            
            if self.connection.is_connected():
                self.logger.info(f"MariaDB에 연결됨 ({self.host}:{self.port}, DB: {self.database})")
                # 자동 커밋 비활성화 (명시적 트랜잭션 관리)
                self.connection.autocommit = False
                
                # 테이블 존재 여부 확인 및 생성
                self._ensure_tables_exist()
            else:
                self.logger.error("데이터베이스 연결 실패")
                
        except Error as e:
            self.logger.error(f"데이터베이스 연결 오류: {e}")
    
    def _ensure_tables_exist(self):
        """필요한 테이블이 존재하는지 확인하고 없으면 생성"""
        # 테이블 생성 SQL
        create_basic_info_table = """
        CREATE TABLE IF NOT EXISTS medicine_basic_info (
            id INT AUTO_INCREMENT PRIMARY KEY,
            medicine_id VARCHAR(20) UNIQUE NOT NULL COMMENT '의약품 고유 ID',
            name_ko VARCHAR(255) NOT NULL COMMENT '약품명(한글명)',
            name_en VARCHAR(255) COMMENT '약품명(영문명)',
            image_url VARCHAR(500) COMMENT '이미지 URL',
            category VARCHAR(100) COMMENT '분류',
            type VARCHAR(50) COMMENT '구분',
            company VARCHAR(100) COMMENT '업체명',
            insurance_code VARCHAR(20) COMMENT '보험코드',
            appearance TEXT COMMENT '성상',
            formulation VARCHAR(50) COMMENT '제형',
            shape VARCHAR(50) COMMENT '모양',
            color VARCHAR(50) COMMENT '색깔',
            size VARCHAR(100) COMMENT '크기',
            identification VARCHAR(255) COMMENT '식별표기',
            dividing_line VARCHAR(50) COMMENT '분할선',
            ingredient_info TEXT COMMENT '성분정보',
            storage_method VARCHAR(255) COMMENT '저장방법',
            usage_period VARCHAR(100) COMMENT '사용기간',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX (name_ko),
            INDEX (insurance_code),
            INDEX (company)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        create_detailed_info_table = """
        CREATE TABLE IF NOT EXISTS medicine_detailed_info (
            id INT AUTO_INCREMENT PRIMARY KEY,
            medicine_id VARCHAR(20) NOT NULL COMMENT '의약품 고유 ID',
            effectiveness LONGTEXT COMMENT '효능효과',
            dosage LONGTEXT COMMENT '용법용량',
            precautions LONGTEXT COMMENT '사용상의주의사항',
            professional_precautions LONGTEXT COMMENT '사용상의주의사항(전문가)',
            effectiveness_html LONGTEXT COMMENT '효능효과 HTML',
            dosage_html LONGTEXT COMMENT '용법용량 HTML',
            precautions_html LONGTEXT COMMENT '사용상의주의사항 HTML',
            professional_precautions_html LONGTEXT COMMENT '사용상의주의사항(전문가) HTML',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (medicine_id) REFERENCES medicine_basic_info(medicine_id) ON DELETE CASCADE,
            INDEX (medicine_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        try:
            cursor = self.connection.cursor()
            
            # 기본 정보 테이블 생성
            cursor.execute(create_basic_info_table)
            
            # 상세 정보 테이블 생성
            cursor.execute(create_detailed_info_table)
            
            self.connection.commit()
            self.logger.info("필요한 테이블이 준비되었습니다.")
            
        except Error as e:
            self.logger.error(f"테이블 생성 오류: {e}")
            self.connection.rollback()
            
        finally:
            cursor.close()
    
    def disconnect(self):
        """데이터베이스 연결 종료"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.logger.info("데이터베이스 연결 종료")
    
    def save_medicine_data(self, medicine_data):
        """
        의약품 데이터 저장
        
        Args:
            medicine_data (dict): 저장할 의약품 데이터
            
        Returns:
            bool: 저장 성공 여부
        """
        if not medicine_data or not self.connection:
            return False
        
        # 데이터 가공
        basic_info, detailed_info = self.processor.prepare_for_db(medicine_data)
        
        if not basic_info or 'medicine_id' not in basic_info:
            self.logger.error("저장할 기본 정보가 유효하지 않습니다")
            return False
        
        medicine_id = basic_info.get('medicine_id')
        
        try:
            # 트랜잭션 시작
            cursor = self.connection.cursor()
            
            # 기본 정보 저장 (INSERT 또는 UPDATE)
            self._save_basic_info(cursor, basic_info)
            
            # 상세 정보 저장 (있는 경우)
            if detailed_info:
                self._save_detailed_info(cursor, detailed_info)
            
            # 트랜잭션 커밋
            self.connection.commit()
            self.logger.info(f"의약품 데이터 저장 성공: {medicine_id}")
            return True
            
        except Error as e:
            self.connection.rollback()
            self.logger.error(f"데이터 저장 오류: {e}")
            return False
            
        finally:
            cursor.close()
    
    def _save_basic_info(self, cursor, basic_info):
        """
        기본 정보 테이블에 데이터 저장
        
        Args:
            cursor: 데이터베이스 커서
            basic_info (dict): 저장할 기본 정보
        """
        # 이미 존재하는지 확인
        medicine_id = basic_info.get('medicine_id')
        check_sql = "SELECT id FROM medicine_basic_info WHERE medicine_id = %s"
        cursor.execute(check_sql, (medicine_id,))
        exists = cursor.fetchone()
        
        if exists:
            # UPDATE
            fields = []
            values = []
            
            for key, value in basic_info.items():
                if key != 'medicine_id':  # medicine_id는 WHERE 절에서 사용
                    fields.append(f"{key} = %s")
                    values.append(value)
            
            # medicine_id는 마지막에 추가 (WHERE 절용)
            values.append(medicine_id)
            
            update_sql = f"UPDATE medicine_basic_info SET {', '.join(fields)} WHERE medicine_id = %s"
            cursor.execute(update_sql, values)
            
        else:
            # INSERT
            fields = []
            placeholders = []
            values = []
            
            for key, value in basic_info.items():
                fields.append(key)
                placeholders.append('%s')
                values.append(value)
            
            insert_sql = f"INSERT INTO medicine_basic_info ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
            cursor.execute(insert_sql, values)
    
    def _save_detailed_info(self, cursor, detailed_info):
        """
        상세 정보 테이블에 데이터 저장
        
        Args:
            cursor: 데이터베이스 커서
            detailed_info (dict): 저장할 상세 정보
        """
        # 이미 존재하는지 확인
        medicine_id = detailed_info.get('medicine_id')
        check_sql = "SELECT id FROM medicine_detailed_info WHERE medicine_id = %s"
        cursor.execute(check_sql, (medicine_id,))
        exists = cursor.fetchone()
        
        if exists:
            # UPDATE
            fields = []
            values = []
            
            for key, value in detailed_info.items():
                if key != 'medicine_id':  # medicine_id는 WHERE 절에서 사용
                    fields.append(f"{key} = %s")
                    values.append(value)
            
            # medicine_id는 마지막에 추가 (WHERE 절용)
            values.append(medicine_id)
            
            update_sql = f"UPDATE medicine_detailed_info SET {', '.join(fields)} WHERE medicine_id = %s"
            cursor.execute(update_sql, values)
            
        else:
            # INSERT
            fields = []
            placeholders = []
            values = []
            
            for key, value in detailed_info.items():
                fields.append(key)
                placeholders.append('%s')
                values.append(value)
            
            insert_sql = f"INSERT INTO medicine_detailed_info ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
            cursor.execute(insert_sql, values)
    
    def get_medicine_by_id(self, medicine_id):
        """
        ID로 의약품 데이터 조회
        
        Args:
            medicine_id (str): 조회할 의약품 ID
            
        Returns:
            dict: 의약품 데이터 (없으면 None)
        """
        if not self.connection:
            return None
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # 기본 정보 조회
            basic_sql = "SELECT * FROM medicine_basic_info WHERE medicine_id = %s"
            cursor.execute(basic_sql, (medicine_id,))
            basic_info = cursor.fetchone()
            
            if not basic_info:
                return None
            
            # 상세 정보 조회
            detailed_sql = "SELECT * FROM medicine_detailed_info WHERE medicine_id = %s"
            cursor.execute(detailed_sql, (medicine_id,))
            detailed_info = cursor.fetchone()
            
            # 결과 구성
            result = {
                'basic_info': basic_info,
                'detailed_info': detailed_info or {}
            }
            
            return result
            
        except Error as e:
            self.logger.error(f"데이터 조회 오류: {e}")
            return None
            
        finally:
            cursor.close()
    
    def __del__(self):
        """소멸자: 연결 종료"""
        self.disconnect()