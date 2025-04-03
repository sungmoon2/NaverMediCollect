#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NaverMediCollect - src/parsing/structure_preserver.py
생성일: 2025-04-03

HTML 구조 보존을 담당하는 모듈입니다.
표, 서식, 특수 포맷 등을 포함한 HTML 구조를 보존합니다.
"""

import logging
import bleach
from typing import Optional, Any, List
from bs4 import BeautifulSoup, Tag


class HTMLStructurePreserver:
    """HTML 구조 보존 클래스"""
    
    def __init__(self):
        """초기화"""
        self.logger = logging.getLogger(__name__)
        
        # 포괄적인 허용 태그
        self.allowed_tags = [
            'table', 'tr', 'td', 'th', 'thead', 'tbody', 
            'p', 'b', 'strong', 'i', 'em', 'u', 
            'div', 'span', 'br', 'hr',
            'sup', 'sub', 
            'ul', 'ol', 'li',  # 리스트 요소
            'pre', 'code',     # 코드/포맷팅 요소
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6'  # 제목 요소
        ]
        
        # 확장된 속성 허용
        self.allowed_attributes = {
            '*': [
                'class', 'style', 'id', 
                'data-type', 'data-lang'
            ],
            'table': ['border', 'cellspacing', 'cellpadding', 'width', 'height'],
            'img': ['src', 'alt', 'width', 'height'],
            'a': ['href', 'target']
        }
    
    def preserve_html_structure(self, element: Any) -> str:
        """
        HTML 구조 보존
        
        Args:
            element: HTML 구조를 보존할 요소
            
        Returns:
            str: 보존된 HTML 구조 (실패 시 빈 문자열)
        """
        if not element:
            return ""
        
        try:
            # 요소 타입에 따라 처리
            if isinstance(element, str):
                # 문자열인 경우 BeautifulSoup으로 파싱
                soup = BeautifulSoup(element, 'html.parser')
                html_structure = self._extract_full_section(soup)
            elif isinstance(element, Tag):
                # 이미 BS4 태그인 경우 직접 사용
                html_structure = self._extract_full_section(element)
            else:
                self.logger.error(f"지원되지 않는 요소 타입: {type(element)}")
                return ""
            
            # HTML 살균 처리
            sanitized_html = self._sanitize_html(html_structure)
            
            return sanitized_html
            
        except Exception as e:
            self.logger.error(f"HTML 구조 보존 오류: {e}")
            return ""
    
    def _extract_full_section(self, element: Any) -> str:
        """
        재귀적으로 HTML 구조 추출
        
        Args:
            element: 추출할 요소
            
        Returns:
            str: 추출된 HTML 구조
        """
        if not element:
            return ""
        
        try:
            # 보존할 속성 목록
            preserved_attributes = [
                'class', 'id', 'style', 
                'data-type', 'data-lang',
                'cellspacing', 'cellpadding',
                'border', 'width', 'height'
            ]
            
            # 요소의 복사본 생성
            if isinstance(element, Tag):
                # 요소 자체의 HTML 반환
                return str(element)
            elif hasattr(element, 'select_one'):
                # BeautifulSoup 객체인 경우 body 내용 추출
                body = element.select_one('body')
                if body:
                    return ''.join(str(child) for child in body.children)
                else:
                    return ''.join(str(child) for child in element.children)
            else:
                # 그 외의 경우 문자열로 변환
                return str(element)
            
        except Exception as e:
            self.logger.error(f"HTML 구조 추출 오류: {e}")
            return ""
    
    def _sanitize_html(self, html_content: str) -> str:
        """
        HTML 콘텐츠 살균
        
        Args:
            html_content (str): 살균할 HTML 콘텐츠
            
        Returns:
            str: 살균된 HTML 콘텐츠
        """
        if not html_content:
            return ""
        
        try:
            # Bleach를 사용한 HTML 살균
            sanitized_html = bleach.clean(
                html_content, 
                tags=self.allowed_tags, 
                attributes=self.allowed_attributes,
                strip=False  # 허용되지 않은 태그 내용은 유지
            )
            
            return sanitized_html
            
        except Exception as e:
            self.logger.error(f"HTML 살균 오류: {e}")
            return ""
    
    def preserve_table_structure(self, table_element: Any) -> str:
        """
        테이블 구조 보존
        
        Args:
            table_element: 보존할 테이블 요소
            
        Returns:
            str: 보존된 테이블 HTML (실패 시 빈 문자열)
        """
        if not table_element:
            return ""
        
        try:
            # 테이블 태그인지 확인
            if isinstance(table_element, Tag) and table_element.name == 'table':
                # 테이블 구조 보존
                table_html = str(table_element)
                
                # 살균 처리
                sanitized_table = self._sanitize_html(table_html)
                
                return sanitized_table
            else:
                self.logger.warning("테이블 요소가 아닙니다.")
                return ""
            
        except Exception as e:
            self.logger.error(f"테이블 구조 보존 오류: {e}")
            return ""
    
    def preserve_list_structure(self, list_element: Any) -> str:
        """
        목록 구조 보존
        
        Args:
            list_element: 보존할 목록 요소
            
        Returns:
            str: 보존된 목록 HTML (실패 시 빈 문자열)
        """
        if not list_element:
            return ""
        
        try:
            # 목록 태그인지 확인
            if isinstance(list_element, Tag) and list_element.name in ['ul', 'ol']:
                # 목록 구조 보존
                list_html = str(list_element)
                
                # 살균 처리
                sanitized_list = self._sanitize_html(list_html)
                
                return sanitized_list
            else:
                self.logger.warning("목록 요소가 아닙니다.")
                return ""
            
        except Exception as e:
            self.logger.error(f"목록 구조 보존 오류: {e}")
            return ""
    
    def extract_section_html(self, soup: BeautifulSoup, section_selector: str) -> str:
        """
        특정 섹션의 HTML 구조 추출
        
        Args:
            soup (BeautifulSoup): 파싱된 BeautifulSoup 객체
            section_selector (str): 섹션 선택자
            
        Returns:
            str: 추출된 섹션 HTML (실패 시 빈 문자열)
        """
        if not soup:
            return ""
        
        try:
            # 섹션 선택
            section = soup.select_one(section_selector)
            if not section:
                self.logger.warning(f"섹션을 찾을 수 없습니다: {section_selector}")
                return ""
            
            # 현재 요소부터 다음 주요 섹션 전까지의 HTML 추출
            full_html = ""
            current = section
            
            while current:
                # 다음 주요 섹션을 만나면 중단
                if current.name == 'h3' and current.get('class') and 'stress' in current.get('class'):
                    break
                
                # HTML 구조 추가
                full_html += str(current)
                current = current.next_sibling
            
            # 살균 처리
            sanitized_html = self._sanitize_html(full_html)
            
            return sanitized_html.strip()
            
        except Exception as e:
            self.logger.error(f"섹션 HTML 추출 오류: {e}")
            return ""