#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NaverMediCollect - src/reporting/html_reporter.py
생성일: 2025-04-03

HTML 보고서 생성을 담당하는 모듈입니다.
수집된 의약품 데이터에 대한 HTML 보고서를 생성합니다.
"""

import os
import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader

from src.database.operations import DBOperations
from src.data.validator import DataValidator
from src.utils.file_manager import FileManager


class HTMLReporter:
    """HTML 보고서 생성 클래스"""
    
    def __init__(self):
        """초기화"""
        self.logger = logging.getLogger(__name__)
        self.db_operations = DBOperations()
        self.validator = DataValidator()
        self.file_manager = FileManager()
        
        # 템플릿 환경 설정
        template_dir = os.path.join('src', 'reporting', 'templates')
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )
        
        # 보고서 저장 디렉토리
        self.reports_dir = os.path.join('data', 'reports')
        
        # 디렉토리 생성
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate_report_for_batch(self, batch_size: int = 50, batch_num: Optional[int] = None) -> str:
        """
        배치 단위로 보고서 생성
        
        Args:
            batch_size (int, optional): 배치 크기. 기본값 50
            batch_num (int, optional): 배치 번호. 기본값 None (자동 계산)
            
        Returns:
            str: 생성된 보고서 파일 경로 (실패 시 빈 문자열)
        """
        try:
            # 전체 의약품 수 조회
            total_medicines = self.db_operations.get_medicine_count()
            
            if total_medicines == 0:
                self.logger.warning("보고서를 생성할 의약품이 없습니다.")
                return ""
            
            # 배치 번호 계산
            if batch_num is None:
                batch_num = (total_medicines // batch_size) + 1
            
            # 시작 및 종료 인덱스 계산
            start_idx = (batch_num - 1) * batch_size + 1
            end_idx = min(batch_num * batch_size, total_medicines)
            
            # 배치 데이터 조회
            medicines = self.db_operations.get_medicines_by_batch(batch_size, batch_num)
            
            if not medicines:
                self.logger.warning(f"배치 {batch_num}에 의약품이 없습니다.")
                return ""
            
            # 보고서 파일명 생성
            report_filename = f"report_{start_idx}_{end_idx}.html"
            report_path = os.path.join(self.reports_dir, report_filename)
            
            # 데이터 처리
            processed_medicines = self._process_medicines_for_report(medicines)
            
            # 통계 계산
            stats = self._calculate_statistics(processed_medicines)
            
            # 템플릿 렌더링
            template = self.jinja_env.get_template('report_template.html')
            html_content = template.render(
                generation_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                start_idx=start_idx,
                end_idx=end_idx,
                total_medicines=len(medicines),
                successful_extractions=stats['success'],
                partial_extractions=stats['partial'],
                failed_extractions=stats['failed'],
                medicines=processed_medicines,
                report_id=f"batch_{batch_num}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            
            # 파일 저장
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"HTML 보고서 생성 완료: {report_path} (의약품 {len(medicines)}개)")
            return report_path
            
        except Exception as e:
            self.logger.error(f"보고서 생성 오류: {e}")
            return ""
    
    def generate_all_reports(self) -> List[str]:
        """
        모든 배치에 대한 보고서 생성
        
        Returns:
            list: 생성된 보고서 파일 경로 목록
        """
        try:
            # 전체 의약품 수 조회
            total_medicines = self.db_operations.get_medicine_count()
            
            if total_medicines == 0:
                self.logger.warning("보고서를 생성할 의약품이 없습니다.")
                return []
            
            # 배치 크기 및 개수 계산
            batch_size = 50
            batch_count = (total_medicines + batch_size - 1) // batch_size
            
            # 모든 배치에 대한 보고서 생성
            report_paths = []
            for batch_num in range(1, batch_count + 1):
                report_path = self.generate_report_for_batch(batch_size, batch_num)
                if report_path:
                    report_paths.append(report_path)
            
            self.logger.info(f"모든 보고서 생성 완료: {len(report_paths)}개")
            return report_paths
            
        except Exception as e:
            self.logger.error(f"모든 보고서 생성 오류: {e}")
            return []
    
    def _process_medicines_for_report(self, medicines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        보고서용 의약품 데이터 처리
        
        Args:
            medicines (list): 처리할 의약품 데이터 목록
            
        Returns:
            list: 처리된 의약품 데이터 목록
        """
        processed_medicines = []
        
        for medicine in medicines:
            basic_info = medicine.get('basic_info', {})
            detailed_info = medicine.get('detailed_info', {})
            
            # 상태 평가
            if basic_info and 'name_ko' in basic_info and 'medicine_id' in basic_info:
                if detailed_info and any(key in detailed_info for key in ['effectiveness', 'dosage', 'precautions']):
                    status = 'success'
                else:
                    status = 'partial'
            else:
                status = 'failed'
            
            # 필드 목록 생성
            fields = []
            
            # 기본 정보 필드
            for key, value in basic_info.items():
                if key not in ['id', 'created_at', 'updated_at']:
                    field_status = 'success' if value else 'missing'
                    fields.append({
                        'name': key,
                        'value': value,
                        'status': field_status
                    })
            
            # 상세 정보 필드
            for key, value in detailed_info.items():
                if key not in ['id', 'created_at', 'updated_at', 'medicine_id'] and not key.endswith('_html'):
                    field_status = 'success' if value else 'missing'
                    fields.append({
                        'name': key,
                        'value': value,
                        'status': field_status
                    })
            
            # 처리된 의약품 데이터
            processed_medicine = {
                'name': basic_info.get('name_ko', '알 수 없음'),
                'medicine_id': basic_info.get('medicine_id', ''),
                'extraction_status': status,
                'fields': fields
            }
            
            processed_medicines.append(processed_medicine)
        
        return processed_medicines
    
    def _calculate_statistics(self, processed_medicines: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        통계 계산
        
        Args:
            processed_medicines (list): 처리된 의약품 데이터 목록
            
        Returns:
            dict: 통계 정보
        """
        stats = {
            'success': 0,
            'partial': 0,
            'failed': 0
        }
        
        for medicine in processed_medicines:
            status = medicine.get('extraction_status')
            if status == 'success':
                stats['success'] += 1
            elif status == 'partial':
                stats['partial'] += 1
            else:
                stats['failed'] += 1
        
        return stats