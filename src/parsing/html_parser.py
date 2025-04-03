#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NaverMediCollect - src/parsing/html_parser.py
생성일: 2025-04-03

HTML 파싱 기능을 제공하는 모듈입니다.
BeautifulSoup을 활용한 기본 HTML 파싱 기능을 제공합니다.
"""

import logging
import re
from bs4 import BeautifulSoup
from typing import Optional, List, Dict, Any, Union


class HTMLParser:
    """HTML 파싱 클래스"""
    
    def __init__(self):
        """초기화"""
        self.logger = logging.getLogger(__name__)
    
    def parse_html(self, html_content: str) -> Optional[BeautifulSoup]:
        """
        HTML 파싱
        
        Args:
            html_content (str): 파싱할 HTML 콘텐츠
            
        Returns:
            BeautifulSoup: 파싱된 BeautifulSoup 객체 (실패 시 None)
        """
        if not html_content:
            return None
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup
        except Exception as e:
            self.logger.error(f"HTML 파싱 오류: {e}")
            return None
    
    def select_element(self, soup: BeautifulSoup, selector: str) -> Optional[Any]:
        """
        CSS 선택자로 요소 선택
        
        Args:
            soup (BeautifulSoup): 파싱된 BeautifulSoup 객체
            selector (str): CSS 선택자
            
        Returns:
            element: 선택된 요소 (없으면 None)
        """
        if not soup:
            return None
        
        try:
            element = soup.select_one(selector)
            return element
        except Exception as e:
            self.logger.error(f"요소 선택 오류 ({selector}): {e}")
            return None
    
    def select_elements(self, soup: BeautifulSoup, selector: str) -> List[Any]:
        """
        CSS 선택자로 여러 요소 선택
        
        Args:
            soup (BeautifulSoup): 파싱된 BeautifulSoup 객체
            selector (str): CSS 선택자
            
        Returns:
            list: 선택된 요소 목록 (없으면 빈 리스트)
        """
        if not soup:
            return []
        
        try:
            elements = soup.select(selector)
            return elements
        except Exception as e:
            self.logger.error(f"요소 선택 오류 ({selector}): {e}")
            return []
    
    def extract_text(self, element: Any) -> str:
        """
        요소에서 텍스트 추출
        
        Args:
            element: 텍스트를 추출할 요소
            
        Returns:
            str: 추출된 텍스트 (없으면 빈 문자열)
        """
        if not element:
            return ""
        
        try:
            text = element.get_text().strip()
            # 여러 공백 제거
            text = re.sub(r'\s+', ' ', text)
            return text
        except Exception as e:
            self.logger.error(f"텍스트 추출 오류: {e}")
            return ""
    
    def extract_attribute(self, element: Any, attribute: str) -> str:
        """
        요소에서 속성 추출
        
        Args:
            element: 속성을 추출할 요소
            attribute (str): 추출할 속성 이름
            
        Returns:
            str: 추출된 속성 값 (없으면 빈 문자열)
        """
        if not element:
            return ""
        
        try:
            value = element.get(attribute, "")
            return value.strip()
        except Exception as e:
            self.logger.error(f"속성 추출 오류 ({attribute}): {e}")
            return ""
    
    def extract_table_data(self, table_element: Any) -> List[Dict[str, str]]:
        """
        테이블 요소에서 데이터 추출
        
        Args:
            table_element: 테이블 요소
            
        Returns:
            list: 추출된 테이블 데이터 (행별 딕셔너리 목록)
        """
        if not table_element:
            return []
        
        try:
            rows = []
            
            # 헤더 행 추출
            header_cells = table_element.select('thead th') or table_element.select('tr th')
            headers = [self.extract_text(cell) for cell in header_cells]
            
            # 헤더가 없으면 빈 목록 반환
            if not headers:
                self.logger.warning("테이블 헤더가 없습니다.")
                return []
            
            # 데이터 행 추출
            data_rows = table_element.select('tbody tr') or table_element.select('tr')[1:]
            
            for row in data_rows:
                cells = row.select('td')
                
                # 셀이 없으면 건너뛰기
                if not cells:
                    continue
                
                # 행 데이터 추출
                row_data = {}
                for i, cell in enumerate(cells):
                    header = headers[i] if i < len(headers) else f"column_{i}"
                    row_data[header] = self.extract_text(cell)
                
                rows.append(row_data)
            
            return rows
            
        except Exception as e:
            self.logger.error(f"테이블 데이터 추출 오류: {e}")
            return []
    
    def find_section(self, soup: BeautifulSoup, section_title: str, title_tag: str = 'h3') -> Dict[str, Any]:
        """
        제목으로 섹션 찾기
        
        Args:
            soup (BeautifulSoup): 파싱된 BeautifulSoup 객체
            section_title (str): 찾을 섹션 제목
            title_tag (str, optional): 제목 태그. 기본값 'h3'
            
        Returns:
            dict: 섹션 정보 (제목 요소, 내용 요소, 텍스트)
        """
        if not soup:
            return {'title_element': None, 'content_element': None, 'text': ""}
        
        try:
            # 제목 요소 찾기
            title_elements = soup.find_all(title_tag)
            title_element = None
            
            for element in title_elements:
                if section_title in self.extract_text(element):
                    title_element = element
                    break
            
            if not title_element:
                self.logger.warning(f"'{section_title}' 섹션을 찾을 수 없습니다.")
                return {'title_element': None, 'content_element': None, 'text': ""}
            
            # 내용 요소 찾기 (다음 형제 요소)
            content_element = title_element.find_next_sibling()
            
            # 내용 요소가 없으면 빈 정보 반환
            if not content_element:
                self.logger.warning(f"'{section_title}' 섹션의 내용을 찾을 수 없습니다.")
                return {'title_element': title_element, 'content_element': None, 'text': ""}
            
            # 섹션 텍스트 추출
            text = self.extract_text(content_element)
            
            return {
                'title_element': title_element,
                'content_element': content_element,
                'text': text
            }
            
        except Exception as e:
            self.logger.error(f"섹션 찾기 오류 ({section_title}): {e}")
            return {'title_element': None, 'content_element': None, 'text': ""}
    
    def extract_profile_table_data(self, soup: BeautifulSoup, table_selector: str = 'table.tmp_profile_tb') -> Dict[str, str]:
        """
        프로필 테이블에서 데이터 추출
        
        Args:
            soup (BeautifulSoup): 파싱된 BeautifulSoup 객체
            table_selector (str, optional): 테이블 선택자
            
        Returns:
            dict: 추출된 프로필 데이터 (필드명: 값)
        """
        if not soup:
            return {}
        
        try:
            profile_data = {}
            table = self.select_element(soup, table_selector)
            
            if not table:
                self.logger.warning(f"프로필 테이블을 찾을 수 없습니다: {table_selector}")
                return {}
            
            # 행 순회
            for row in table.select('tr'):
                # 필드명 셀과 값 셀 찾기
                field_cell = row.select_one('th')
                value_cell = row.select_one('td')
                
                if not field_cell or not value_cell:
                    continue
                
                # 필드명과 값 추출
                field_name = self.extract_text(field_cell)
                field_value = self.extract_text(value_cell)
                
                # 프로필 데이터에 추가
                if field_name:
                    profile_data[field_name] = field_value
            
            return profile_data
            
        except Exception as e:
            self.logger.error(f"프로필 데이터 추출 오류: {e}")
            return {}