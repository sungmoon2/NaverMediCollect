#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NaverMediCollect - src/data/processor.py
생성일: 2025-04-03

추출된 데이터를 가공하고 정제하는 모듈입니다.
데이터 정규화, 텍스트 클리닝, 데이터 변환 등의 기능을 제공합니다.
"""

import logging
import re
import bleach
from bs4 import BeautifulSoup


class DataProcessor:
    """데이터 가공 클래스"""
    
    def __init__(self):
        """초기화"""
        self.logger = logging.getLogger(__name__)
        
        # HTML 살균 설정
        self.allowed_tags = [
            'table', 'tr', 'td', 'th', 'thead', 'tbody', 
            'p', 'b', 'strong', 'i', 'em', 'u', 
            'div', 'span', 'br', 'hr',
            'sup', 'sub', 
            'ul', 'ol', 'li',
            'pre', 'code',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
        ]
        
        self.allowed_attributes = {
            '*': ['class', 'style', 'id', 'data-type', 'data-lang'],
            'table': ['border', 'cellspacing', 'cellpadding', 'width', 'height'],
            'img': ['src', 'alt', 'width', 'height'],
            'a': ['href', 'target']
        }
    
    def process_medicine_data(self, medicine_data):
        """
        의약품 데이터 처리
        
        Args:
            medicine_data (dict): 처리할 의약품 데이터
            
        Returns:
            dict: 처리된 의약품 데이터
        """
        if not medicine_data:
            return None
        
        # 기본 정보 처리
        if 'basic_info' in medicine_data:
            medicine_data['basic_info'] = self._process_basic_info(medicine_data['basic_info'])
        
        # 상세 정보 처리
        if 'detailed_info' in medicine_data:
            medicine_data['detailed_info'] = self._process_detailed_info(medicine_data['detailed_info'])
        
        return medicine_data
    
    def _process_basic_info(self, basic_info):
        """
        기본 정보 처리
        
        Args:
            basic_info (dict): 처리할 기본 정보
            
        Returns:
            dict: 처리된 기본 정보
        """
        if not basic_info:
            return {}
        
        processed_info = basic_info.copy()
        
        # 의약품 이름 정규화
        if 'name_ko' in processed_info:
            processed_info['name_ko'] = self._normalize_medicine_name(processed_info['name_ko'])
        
        # 업체명 정규화
        if 'company' in processed_info:
            processed_info['company'] = self._normalize_company_name(processed_info['company'])
        
        # 분류 정보 정규화
        if 'category' in processed_info:
            # 분류 코드와 이름 분리
            category_parts = self._split_category(processed_info['category'])
            processed_info['category_code'] = category_parts[0]
            processed_info['category_name'] = category_parts[1]
        
        # 특수 문자 및 공백 처리
        for key, value in processed_info.items():
            if isinstance(value, str):
                processed_info[key] = self._clean_text(value)
        
        return processed_info
    
    def _process_detailed_info(self, detailed_info):
        """
        상세 정보 처리
        
        Args:
            detailed_info (dict): 처리할 상세 정보
            
        Returns:
            dict: 처리된 상세 정보
        """
        if not detailed_info:
            return {}
        
        processed_info = detailed_info.copy()
        
        # 텍스트 필드 정리
        text_fields = ['effectiveness', 'dosage', 'precautions', 'professional_precautions']
        for field in text_fields:
            if field in processed_info:
                processed_info[field] = self._clean_text(processed_info[field])
        
        # HTML 필드 살균
        html_fields = ['effectiveness_html', 'dosage_html', 'precautions_html', 'professional_precautions_html']
        for field in html_fields:
            if field in processed_info:
                processed_info[field] = self._sanitize_html(processed_info[field])
        
        return processed_info
    
    def _normalize_medicine_name(self, name):
        """
        의약품 이름 정규화
        
        Args:
            name (str): 정규화할 의약품 이름
            
        Returns:
            str: 정규화된 이름
        """
        if not name:
            return ""
        
        # 괄호 안의 성분명 분리 (필요 시 별도 필드로 저장 가능)
        # 예: "케이캡정50mg(테고프라잔)" -> "케이캡정50mg"
        name_parts = re.split(r'\s*\([^)]*\)\s*', name)
        normalized_name = name_parts[0].strip()
        
        return normalized_name
    
    def _normalize_company_name(self, company):
        """
        업체명 정규화
        
        Args:
            company (str): 정규화할 업체명
            
        Returns:
            str: 정규화된 업체명
        """
        if not company:
            return ""
        
        # 회사 접미사 정규화
        company = re.sub(r'주식회사\s*', '', company)
        company = re.sub(r'\(주\)', '㈜', company)  # (주) -> ㈜
        company = re.sub(r'\(유\)', '㈜', company)  # (유) -> ㈜
        
        return company.strip()
    
    def _split_category(self, category):
        """
        분류 정보 분리
        
        Args:
            category (str): 분류 정보 (예: "[02320]소화성궤양용제")
            
        Returns:
            tuple: (분류 코드, 분류명)
        """
        if not category:
            return ("", "")
        
        # 분류 코드 추출 (대괄호 안의 내용)
        code_match = re.search(r'\[(.*?)\]', category)
        code = code_match.group(1) if code_match else ""
        
        # 분류명 추출 (대괄호 이후의 내용)
        name = re.sub(r'\[.*?\]', '', category).strip()
        
        return (code, name)
    
    def _clean_text(self, text):
        """
        텍스트 정리 (특수 문자, 중복 공백 등 처리)
        
        Args:
            text (str): 정리할 텍스트
            
        Returns:
            str: 정리된 텍스트
        """
        if not text:
            return ""
        
        # 제어 문자 제거
        text = re.sub(r'[\x00-\x1F\x7F]', '', text)
        
        # 중복 공백 제거
        text = re.sub(r'\s+', ' ', text)
        
        # 불필요한 특수 문자 처리
        text = text.replace('&nbsp;', ' ')
        
        return text.strip()
    
    def _sanitize_html(self, html):
        """
        HTML 살균 (보안을 위한 처리)
        
        Args:
            html (str): 살균할 HTML
            
        Returns:
            str: 살균된 HTML
        """
        if not html:
            return ""
        
        # 불필요한 공백 태그 제거
        soup = BeautifulSoup(html, 'html.parser')
        for element in soup.find_all(string=lambda text: isinstance(text, str) and text.strip() == ''):
            if element.parent.name not in ['style', 'script', 'pre', 'code']:
                element.replace_with('')
        
        # 정리된 HTML
        clean_html = str(soup)
        
        # 허용된 태그 및 속성만 남김
        sanitized_html = bleach.clean(
            clean_html, 
            tags=self.allowed_tags, 
            attributes=self.allowed_attributes,
            strip=False  # 허용되지 않은 태그 제거
        )
        
        return sanitized_html
    
    def prepare_for_db(self, medicine_data):
        """
        데이터베이스 저장을 위한 데이터 준비
        
        Args:
            medicine_data (dict): 준비할 의약품 데이터
            
        Returns:
            tuple: (basic_info_dict, detailed_info_dict)
        """
        if not medicine_data:
            return None, None
        
        # 기본 정보 추출 및 가공
        basic_info = medicine_data.get('basic_info', {}).copy()
        if 'basic_info' in medicine_data:
            for key in list(basic_info.keys()):
                # 데이터베이스 컬럼에 맞게 필드 이름 변환
                if key in ['image_url', 'name_ko', 'name_en', 'medicine_id']:
                    continue  # 이미 맞는 이름이므로 변환 불필요
                
                # 필드명 변환 예시
                if key == 'company':
                    basic_info['company'] = basic_info.pop(key)
                elif key == 'ingredient_info':
                    basic_info['ingredient_info'] = basic_info.pop(key)
                elif key == 'storage_method':
                    basic_info['storage_method'] = basic_info.pop(key)
                elif key == 'usage_period':
                    basic_info['usage_period'] = basic_info.pop(key)
                # 나머지 필드에 대한 매핑은 필요에 따라 추가
        
        # 상세 정보 추출 및 가공
        detailed_info = {}
        if 'detailed_info' in medicine_data:
            detailed_info = medicine_data.get('detailed_info', {}).copy()
            
            # medicine_id 필드 유지
            detailed_info['medicine_id'] = basic_info.get('medicine_id')
            
            # 필요 시 여기에서 필드명 변환 또는 추가 가공 수행
        
        return basic_info, detailed_info