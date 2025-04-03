#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NaverMediCollect - src/parsing/field_mapper.py
생성일: 2025-04-03

HTML 요소와 의약품 데이터 필드 간의 매핑을 담당하는 모듈입니다.
CSS 선택자, XPath 등을 사용하여 필드를 추출합니다.
"""

import logging
import re
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup, Tag

from src.parsing.html_parser import HTMLParser
from conf.field_mapping import FIELD_MAPPING


class FieldMapper:
    """필드 매핑 클래스"""
    
    def __init__(self):
        """초기화"""
        self.logger = logging.getLogger(__name__)
        self.html_parser = HTMLParser()
        self.field_mapping = FIELD_MAPPING
    
    def map_all_fields(self, soup: BeautifulSoup, medicine_id: str) -> Dict[str, Any]:
        """
        모든 필드 매핑
        
        Args:
            soup (BeautifulSoup): 파싱된 BeautifulSoup 객체
            medicine_id (str): 의약품 ID
            
        Returns:
            dict: 매핑된 필드 데이터
        """
        if not soup:
            return {}
        
        result = {
            'basic_info': {'medicine_id': medicine_id},
            'detailed_info': {'medicine_id': medicine_id}
        }
        
        # 기본 정보 필드 매핑
        basic_fields = {k: v for k, v in self.field_mapping.items() if not k.startswith('detailed_')}
        for field_name, field_config in basic_fields.items():
            value = self._extract_field(soup, field_config)
            if value:
                result['basic_info'][field_name] = value
        
        # 상세 정보 필드 매핑
        detailed_fields = {k: v for k, v in self.field_mapping.items() if k.startswith('detailed_')}
        for field_name, field_config in detailed_fields.items():
            # detailed_ 접두사 제거
            actual_field_name = field_name.replace('detailed_', '')
            
            # 일반 텍스트 버전 매핑
            value = self._extract_field(soup, field_config)
            if value:
                result['detailed_info'][actual_field_name] = value
            
            # HTML 버전 매핑 (있는 경우)
            html_value = self._extract_field_html(soup, field_config)
            if html_value:
                result['detailed_info'][f"{actual_field_name}_html"] = html_value
        
        return result
    
    def _extract_field(self, soup: BeautifulSoup, field_config: Dict[str, Any]) -> str:
        """
        필드 설정에 따라 텍스트 추출
        
        Args:
            soup (BeautifulSoup): 파싱된 BeautifulSoup 객체
            field_config (dict): 필드 설정
            
        Returns:
            str: 추출된 텍스트 (없으면 빈 문자열)
        """
        if not soup or not field_config:
            return ""
        
        try:
            selector = field_config.get('selector')
            if not selector:
                return ""
            
            # 요소 선택
            element = self.html_parser.select_element(soup, selector)
            if not element:
                return ""
            
            # 속성 지정이 있는 경우
            attribute = field_config.get('attribute')
            if attribute:
                return self.html_parser.extract_attribute(element, attribute)
            
            # 기본적으로 텍스트 추출
            text = self.html_parser.extract_text(element)
            
            # 후처리 함수가 있는 경우 적용
            post_processor = field_config.get('post_processor')
            if post_processor and hasattr(self, post_processor):
                processor_func = getattr(self, post_processor)
                text = processor_func(text)
            
            return text
            
        except Exception as e:
            self.logger.error(f"필드 추출 오류 ({field_config.get('label', '알 수 없음')}): {e}")
            return ""
    
    def _extract_field_html(self, soup: BeautifulSoup, field_config: Dict[str, Any]) -> str:
        """
        필드 설정에 따라 HTML 추출
        
        Args:
            soup (BeautifulSoup): 파싱된 BeautifulSoup 객체
            field_config (dict): 필드 설정
            
        Returns:
            str: 추출된 HTML (없으면 빈 문자열)
        """
        if not soup or not field_config:
            return ""
        
        try:
            selector = field_config.get('selector')
            if not selector:
                return ""
            
            # 요소 선택
            element = self.html_parser.select_element(soup, selector)
            if not element:
                return ""
            
            # 요소의 HTML 추출
            html = str(element)
            
            return html
            
        except Exception as e:
            self.logger.error(f"HTML 추출 오류 ({field_config.get('label', '알 수 없음')}): {e}")
            return ""
    
    # 후처리 함수들
    def clean_medicine_name(self, text: str) -> str:
        """
        의약품 이름 정리
        
        Args:
            text (str): 정리할 텍스트
            
        Returns:
            str: 정리된 텍스트
        """
        if not text:
            return ""
        
        # 불필요한 문자 제거
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_size(self, text: str) -> str:
        """
        크기 정보 추출
        
        Args:
            text (str): 정리할 텍스트
            
        Returns:
            str: 정리된 텍스트
        """
        if not text:
            return ""
        
        # 숫자와 단위를 포함한 패턴 추출
        size_pattern = re.compile(r'(?:\(장축\)|\(단축\)|\(두께\))?[0-9\.]+\s*(?:mm|cm)?')
        sizes = size_pattern.findall(text)
        
        if sizes:
            return ', '.join(sizes).strip()
        
        return text.strip()
    
    def extract_color(self, text: str) -> str:
        """
        색상 정보 추출
        
        Args:
            text (str): 정리할 텍스트
            
        Returns:
            str: 정리된 텍스트
        """
        if not text:
            return ""
        
        # 색상 목록
        colors = ['흰', '하양', '백색', '검정', '검은', '흑색', '빨강', '적색', '노랑', '황색',
                  '파랑', '청색', '초록', '녹색', '분홍', '핑크색', '보라', '자색', '갈색', '회색',
                  '투명', '반투명', '무색']
        
        found_colors = []
        for color in colors:
            if color in text:
                found_colors.append(color)
        
        if found_colors:
            return ', '.join(found_colors)
        
        return text.strip()
    
    def extract_identification(self, text: str) -> str:
        """
        식별표기 정보 추출
        
        Args:
            text (str): 정리할 텍스트
            
        Returns:
            str: 정리된 텍스트
        """
        if not text:
            return ""
        
        # 공백 및 특수 문자 처리
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()