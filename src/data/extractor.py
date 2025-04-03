#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NaverMediCollect - src/data/extractor.py
생성일: 2025-04-03

의약품 데이터 추출을 담당하는 모듈입니다.
HTML 컨텐츠에서 필요한 정보를 추출하고 구조화합니다.
"""

import logging
import re
import json
import os
from bs4 import BeautifulSoup
from collections import defaultdict

from src.api.naver_api import NaverApiHandler
from src.parsing.html_parser import HTMLParser
from src.parsing.structure_preserver import HTMLStructurePreserver
from src.data.validator import DataValidator
from src.utils.file_manager import FileManager
from conf.field_mapping import FIELD_MAPPING


class DataExtractor:
    """의약품 데이터 추출 클래스"""
    
    def __init__(self):
        """초기화"""
        self.logger = logging.getLogger(__name__)
        self.api_handler = NaverApiHandler()
        self.html_parser = HTMLParser()
        self.structure_preserver = HTMLStructurePreserver()
        self.validator = DataValidator()
        self.file_manager = FileManager()
        
        # 필드 매핑 설정
        self.field_mapping = FIELD_MAPPING
        
        # 통계 정보
        self.stats = {
            'total': 0,
            'success': 0,
            'partial': 0,
            'failed': 0
        }
        
        # 이미 처리된 의약품 ID 로드
        self._load_processed_medicine_ids()
    
    def _load_processed_medicine_ids(self):
        """처리된 의약품 ID 목록 로드"""
        self.processed_ids = set()
        medicine_ids_path = os.path.join('data', 'collected', 'medicine_ids.txt')
        
        if os.path.exists(medicine_ids_path):
            with open(medicine_ids_path, 'r', encoding='utf-8') as f:
                for line in f:
                    self.processed_ids.add(line.strip())
            
            self.logger.info(f"처리된 의약품 ID {len(self.processed_ids)}개 로드됨")
    
    def is_medicine_processed(self, medicine_id):
        """
        의약품 ID가 이미 처리되었는지 확인
        
        Args:
            medicine_id (str): 의약품 ID
            
        Returns:
            bool: 처리 여부
        """
        return medicine_id in self.processed_ids
    
    def extract_medicine_data(self, medicine_preview):
        """
        의약품 데이터 추출
        
        Args:
            medicine_preview (dict): 의약품 미리보기 데이터
            
        Returns:
            dict: 추출된 의약품 데이터 (실패 시 None)
        """
        medicine_id = medicine_preview.get('medicine_id')
        title = medicine_preview.get('title')
        
        self.logger.info(f"의약품 데이터 추출 시작: {title} (ID: {medicine_id})")
        
        # 통계 업데이트
        self.stats['total'] += 1
        
        # 상세 페이지 HTML 가져오기
        html_content = self.api_handler.get_medicine_detail(medicine_id)
        
        if not html_content:
            self.logger.error(f"HTML 콘텐츠를 가져오지 못함: {medicine_id}")
            self.stats['failed'] += 1
            return None
        
        try:
            # HTML 파싱
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 기본 데이터 추출
            basic_data = self._extract_basic_info(soup, medicine_id)
            
            # 상세 데이터 추출
            detailed_data = self._extract_detailed_info(soup, medicine_id)
            
            # 추출 상태 평가
            extraction_status = self._evaluate_extraction_status(basic_data, detailed_data)
            
            # 통계 업데이트
            if extraction_status == 'success':
                self.stats['success'] += 1
            elif extraction_status == 'partial':
                self.stats['partial'] += 1
            else:
                self.stats['failed'] += 1
            
            # 최종 데이터 구성
            medicine_data = {
                'medicine_id': medicine_id,
                'extraction_status': extraction_status,
                'basic_info': basic_data,
                'detailed_info': detailed_data
            }
            
            # 로그 기록
            log_message = (
                f"의약품 추출: {basic_data.get('name_ko', '알 수 없음')}\n"
                f"- 총 필드: {len(self.field_mapping)} / 추출 필드: {self._count_extracted_fields(medicine_data)}\n"
                f"- 상태: {'✅ 성공' if extraction_status == 'success' else '⚠️ 부분' if extraction_status == 'partial' else '❌ 실패'}"
            )
            self.logger.info(log_message)
            
            # 추출 로그 파일에 기록
            self._append_to_extraction_log(medicine_data)
            
            # 처리된 ID 목록에 추가
            self._add_to_processed_ids(medicine_id)
            
            return medicine_data
            
        except Exception as e:
            self.logger.exception(f"데이터 추출 오류: {e}")
            self.stats['failed'] += 1
            return None
    
    def _extract_basic_info(self, soup, medicine_id):
        """
        기본 정보 추출
        
        Args:
            soup (BeautifulSoup): 파싱된 HTML
            medicine_id (str): 의약품 ID
            
        Returns:
            dict: 추출된 기본 정보
        """
        basic_info = {
            'medicine_id': medicine_id
        }
        
        # 한글명 추출
        name_ko_element = soup.select_one('div.headword_title > h2.headword')
        if name_ko_element:
            basic_info['name_ko'] = name_ko_element.get_text().strip()
        
        # 영문명 추출
        name_en_element = soup.select_one('div.headword_title > p.word > span.word_txt')
        if name_en_element:
            basic_info['name_en'] = name_en_element.get_text().strip()
        
        # 이미지 URL 추출
        img_element = soup.select_one('span.img_box > a > img')
        if img_element:
            # 우선순위: origin_src > src > data-src
            basic_info['image_url'] = img_element.get('origin_src') or img_element.get('src') or img_element.get('data-src')
        
        # 프로필 테이블에서 정보 추출
        profile_table = soup.select_one('table.tmp_profile_tb')
        if profile_table:
            for row in profile_table.select('tr'):
                # 첫 번째 셀에서 필드명 추출
                field_cell = row.select_one('th')
                if not field_cell:
                    continue
                
                field_name = field_cell.get_text().strip()
                value_cell = row.select_one('td')
                
                if not value_cell:
                    continue
                
                # 맵핑된 필드명 찾기
                field_key = None
                for key, mapping in self.field_mapping.items():
                    if 'label' in mapping and mapping['label'] == field_name:
                        field_key = key
                        break
                
                if field_key:
                    basic_info[field_key] = value_cell.get_text().strip()
        
        # 성분정보 추출
        ingredient_element = soup.select_one('h3.stress#TABLE_OF_CONTENT1 + p.txt')
        if ingredient_element:
            basic_info['ingredient_info'] = ingredient_element.get_text().strip()
        
        # 저장방법 추출
        storage_element = soup.select_one('h3.stress#TABLE_OF_CONTENT4 + p.txt')
        if storage_element:
            basic_info['storage_method'] = storage_element.get_text().strip()
        
        # 사용기간 추출
        usage_period_element = soup.select_one('h3.stress#TABLE_OF_CONTENT5 + p.txt')
        if usage_period_element:
            basic_info['usage_period'] = usage_period_element.get_text().strip()
        
        return basic_info
    
    def _extract_detailed_info(self, soup, medicine_id):
        """
        상세 정보 추출
        
        Args:
            soup (BeautifulSoup): 파싱된 HTML
            medicine_id (str): 의약품 ID
            
        Returns:
            dict: 추출된 상세 정보
        """
        detailed_info = {
            'medicine_id': medicine_id
        }
        
        # 효능효과 추출
        effectiveness_element = soup.select_one('h3.stress#TABLE_OF_CONTENT2 + p.txt')
        if effectiveness_element:
            # 텍스트 버전
            detailed_info['effectiveness'] = effectiveness_element.get_text().strip()
            # HTML 구조 보존 버전
            detailed_info['effectiveness_html'] = self.structure_preserver.preserve_html_structure(effectiveness_element)
        
        # 용법용량 추출
        dosage_element = soup.select_one('h3.stress#TABLE_OF_CONTENT3 + p.txt')
        if dosage_element:
            # 텍스트 버전
            detailed_info['dosage'] = dosage_element.get_text().strip()
            # HTML 구조 보존 버전
            detailed_info['dosage_html'] = self.structure_preserver.preserve_html_structure(dosage_element)
        
        # 사용상의주의사항 추출
        precautions_element = soup.select_one('h3.stress#TABLE_OF_CONTENT6 + p.txt')
        if precautions_element:
            # 텍스트 버전
            detailed_info['precautions'] = precautions_element.get_text().strip()
            # HTML 구조 보존 버전
            detailed_info['precautions_html'] = self.structure_preserver.preserve_html_structure(precautions_element)
        
        # 사용상의주의사항(전문가) 추출
        professional_precautions_element = soup.select_one('h3.stress#TABLE_OF_CONTENT7 + p.txt')
        if professional_precautions_element:
            # 텍스트 버전
            detailed_info['professional_precautions'] = professional_precautions_element.get_text().strip()
            # HTML 구조 보존 버전
            detailed_info['professional_precautions_html'] = self.structure_preserver.preserve_html_structure(professional_precautions_element)
        
        return detailed_info
    
    def _evaluate_extraction_status(self, basic_data, detailed_data):
        """
        추출 상태 평가
        
        Args:
            basic_data (dict): 기본 정보
            detailed_data (dict): 상세 정보
            
        Returns:
            str: 추출 상태 ('success', 'partial', 'failed')
        """
        # 최소 필수 필드 체크
        required_basic_fields = ['name_ko', 'medicine_id']
        
        # 필수 필드 누락 확인
        for field in required_basic_fields:
            if field not in basic_data or not basic_data[field]:
                return 'failed'
        
        # 기본 및 상세 정보 필드 수 계산
        basic_fields_count = sum(1 for key in basic_data if key != 'medicine_id' and basic_data[key])
        detailed_fields_count = sum(1 for key in detailed_data if key != 'medicine_id' and detailed_data[key])
        
        # 최소 요구 필드 수 계산
        min_basic_fields = 5  # 최소 5개 이상의 기본 필드
        min_detailed_fields = 1  # 최소 1개 이상의 상세 필드
        
        # 모든 필드 확인
        total_expected_fields = len(self.field_mapping)
        total_extracted_fields = basic_fields_count + detailed_fields_count
        
        # 성공 임계값 (80% 이상 추출)
        success_threshold = total_expected_fields * 0.8
        
        # 부분 성공 임계값 (50% 이상 추출)
        partial_threshold = total_expected_fields * 0.5
        
        if (basic_fields_count >= min_basic_fields and 
            detailed_fields_count >= min_detailed_fields and
            total_extracted_fields >= success_threshold):
            return 'success'
        elif (basic_fields_count >= min_basic_fields and 
              total_extracted_fields >= partial_threshold):
            return 'partial'
        else:
            return 'failed'
    
    def _count_extracted_fields(self, medicine_data):
        """
        추출된 필드 수 계산
        
        Args:
            medicine_data (dict): 의약품 데이터
            
        Returns:
            int: 추출된 필드 수
        """
        count = 0
        
        # 기본 정보 필드 수
        for key, value in medicine_data['basic_info'].items():
            if key != 'medicine_id' and value:
                count += 1
        
        # 상세 정보 필드 수 (HTML 버전은 제외)
        for key, value in medicine_data['detailed_info'].items():
            if key != 'medicine_id' and not key.endswith('_html') and value:
                count += 1
        
        return count
    
    def _append_to_extraction_log(self, medicine_data):
        """
        추출 로그 파일에 결과 추가
        
        Args:
            medicine_data (dict): 의약품 데이터
        """
        log_file_path = os.path.join('data', 'collected', 'extraction_log.txt')
        
        # 로그 파일 디렉토리 확인
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        
        # 로그 데이터 생성
        basic_info = medicine_data['basic_info']
        log_entry = {
            'timestamp': self.file_manager.get_timestamp(),
            'medicine_id': basic_info.get('medicine_id'),
            'name_ko': basic_info.get('name_ko', '알 수 없음'),
            'status': medicine_data['extraction_status'],
            'fields_count': self._count_extracted_fields(medicine_data),
            'total_fields': len(self.field_mapping)
        }
        
        # 로그 파일에 추가
        with open(log_file_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def _add_to_processed_ids(self, medicine_id):
        """
        처리된 의약품 ID 목록에 추가
        
        Args:
            medicine_id (str): 의약품 ID
        """
        # 메모리 상의 세트에 추가
        self.processed_ids.add(medicine_id)
        
        # 파일에 추가
        medicine_ids_path = os.path.join('data', 'collected', 'medicine_ids.txt')
        
        # 디렉토리 확인
        os.makedirs(os.path.dirname(medicine_ids_path), exist_ok=True)
        
        # 파일에 추가
        with open(medicine_ids_path, 'a', encoding='utf-8') as f:
            f.write(medicine_id + '\n')
    
    def extract_keywords_from_data(self, medicine_data):
        """
        의약품 데이터에서 새 키워드 추출
        
        Args:
            medicine_data (dict): 의약품 데이터
            
        Returns:
            list: 추출된 키워드 리스트
        """
        keywords = set()
        basic_info = medicine_data['basic_info']
        
        # 분류에서 키워드 추출
        category = basic_info.get('category')
        if category:
            # [코드]카테고리명 형식에서 카테고리명만 추출
            match = re.search(r'\[(.*?)\](.*)', category)
            if match:
                category_name = match.group(2).strip()
                keywords.add(category_name)
        
        # 업체명에서 키워드 추출
        company = basic_info.get('company')
        if company:
            company_name = re.sub(r'\(주\)|\(유\)|주식회사|약품|제약', '', company).strip()
            if company_name:
                keywords.add(company_name)
        
        # 성분정보에서 키워드 추출
        ingredient_info = basic_info.get('ingredient_info')
        if ingredient_info:
            # 성분명 추출 (숫자와 단위 제외)
            ingredients = re.findall(r'([가-힣a-zA-Z\-]+)(?:\s*[\d\.]+\s*(?:mg|g|ml|IU|mcg))?', ingredient_info)
            for ingredient in ingredients:
                ingredient = ingredient.strip()
                if len(ingredient) > 1:  # 1글자 키워드는 제외
                    keywords.add(ingredient)
        
        return list(keywords)
    
    def get_stats(self):
        """
        추출 통계 반환
        
        Returns:
            dict: 추출 통계
        """
        return self.stats