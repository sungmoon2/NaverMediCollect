#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NaverMediCollect - src/keyword/generator.py
생성일: 2025-04-03

새로운 검색 키워드를 생성하는 모듈입니다.
의약품 데이터에서 새 키워드 추출, 키워드 확장 등의 기능을 제공합니다.
"""

import logging
import re
from typing import List, Dict, Set, Any
from collections import Counter


class KeywordGenerator:
    """키워드 생성 클래스"""
    
    def __init__(self):
        """초기화"""
        self.logger = logging.getLogger(__name__)
        
        # 무시할 키워드 패턴
        self.ignore_patterns = [
            r'^[a-zA-Z0-9]$',  # 한 글자 영숫자
            r'^[가-힣]$',       # 한 글자 한글
            r'^\d+(\.\d+)?$',  # 숫자만
            r'^[가-힣]{1,2}제$',  # '~제'로 끝나는 두 글자 단어 (예: 소화제)
        ]
        
        # 특수 키워드 필터
        self.common_words = {
            '정', '캡슐', '주', '시럽', '액', '과립', '산', '정제', 
            '필름', '코팅', '필름코팅', '연고', '크림', '로션', '주사',
            '패취', '스프레이', '당', '환', '말', '원료', '산제'
        }
    
    def extract_from_data(self, medicine_data: Dict[str, Any]) -> List[str]:
        """
        의약품 데이터에서 키워드 추출
        
        Args:
            medicine_data (dict): 의약품 데이터
            
        Returns:
            list: 추출된 키워드 목록
        """
        if not medicine_data:
            return []
        
        keywords = set()
        basic_info = medicine_data.get('basic_info', {})
        detailed_info = medicine_data.get('detailed_info', {})
        
        # 분류에서 키워드 추출
        category = basic_info.get('category')
        if category:
            category_keywords = self._extract_from_category(category)
            keywords.update(category_keywords)
        
        # 업체명에서 키워드 추출
        company = basic_info.get('company')
        if company:
            company_keywords = self._extract_from_company(company)
            keywords.update(company_keywords)
        
        # 성분정보에서 키워드 추출
        ingredient_info = basic_info.get('ingredient_info')
        if ingredient_info:
            ingredient_keywords = self._extract_from_ingredients(ingredient_info)
            keywords.update(ingredient_keywords)
        
        # 효능효과에서 키워드 추출
        effectiveness = detailed_info.get('effectiveness')
        if effectiveness:
            effectiveness_keywords = self._extract_from_effectiveness(effectiveness)
            keywords.update(effectiveness_keywords)
        
        # 필터링 및 정제
        filtered_keywords = self._filter_keywords(keywords)
        
        return list(filtered_keywords)
    
    def _extract_from_category(self, category: str) -> Set[str]:
        """
        분류 정보에서 키워드 추출
        
        Args:
            category (str): 분류 정보
            
        Returns:
            set: 추출된 키워드 집합
        """
        keywords = set()
        
        # [코드]카테고리명 형식 처리
        category_match = re.search(r'\[(.*?)\](.*)', category)
        if category_match:
            category_code = category_match.group(1).strip()
            category_name = category_match.group(2).strip()
            
            # 코드와 카테고리명 모두 추가
            if category_code:
                keywords.add(category_code)
            if category_name:
                keywords.add(category_name)
                
                # 카테고리 내 단어 분리
                words = re.findall(r'[가-힣]+', category_name)
                for word in words:
                    if len(word) >= 2:
                        keywords.add(word)
        else:
            # 패턴이 없으면 그대로 추가
            keywords.add(category.strip())
        
        return keywords
    
    def _extract_from_company(self, company: str) -> Set[str]:
        """
        업체명에서 키워드 추출
        
        Args:
            company (str): 업체명
            
        Returns:
            set: 추출된 키워드 집합
        """
        keywords = set()
        
        # 회사명 정제
        clean_company = re.sub(r'\(주\)|\(유\)|주식회사|약품|제약', '', company).strip()
        
        if clean_company:
            keywords.add(clean_company)
        
        return keywords
    
    def _extract_from_ingredients(self, ingredient_info: str) -> Set[str]:
        """
        성분 정보에서 키워드 추출
        
        Args:
            ingredient_info (str): 성분 정보
            
        Returns:
            set: 추출된 키워드 집합
        """
        keywords = set()
        
        # 성분명 추출 (숫자와 단위 제외)
        ingredients = re.findall(r'([가-힣a-zA-Z\-]+)(?:\s*[\d\.]+\s*(?:mg|g|ml|IU|mcg))?', ingredient_info)
        
        for ingredient in ingredients:
            ingredient = ingredient.strip()
            if len(ingredient) > 1:  # 1글자 키워드는 제외
                keywords.add(ingredient)
                
                # 영문 성분명인 경우 추가 처리
                if re.match(r'^[a-zA-Z\-]+$', ingredient):
                    # 긴 영문 성분명은 분리하여 추가
                    if len(ingredient) > 8:
                        parts = re.findall(r'[A-Z][a-z]+', ingredient)
                        for part in parts:
                            if len(part) > 3:  # 너무 짧은 부분은 제외
                                keywords.add(part.lower())
        
        return keywords
    
    def _extract_from_effectiveness(self, effectiveness: str) -> Set[str]:
        """
        효능효과에서 키워드 추출
        
        Args:
            effectiveness (str): 효능효과
            
        Returns:
            set: 추출된 키워드 집합
        """
        keywords = set()
        
        # 질환명 추출
        diseases = re.findall(r'[가-힣]+(병|증|염|통|열|암|궤양|장애|질환)', effectiveness)
        keywords.update(diseases)
        
        # 주요 단어 추출
        important_words = re.findall(r'[가-힣]{2,5}(?:치료|예방|완화|개선)', effectiveness)
        keywords.update(important_words)
        
        # 신체 부위 + 질환 패턴 추출
        body_parts = ['위', '장', '간', '신장', '심장', '폐', '뇌', '혈관', '근육', '관절', '피부', '눈', '귀', '코', '입', '항문']
        for part in body_parts:
            part_patterns = re.findall(f'{part}[가-힣]{{1,4}}(?:염|통|병|증|장애|질환)', effectiveness)
            keywords.update(part_patterns)
        
        return keywords
    
    def _filter_keywords(self, keywords: Set[str]) -> Set[str]:
        """
        키워드 필터링 및 정제
        
        Args:
            keywords (set): 필터링할 키워드 집합
            
        Returns:
            set: 필터링된 키워드 집합
        """
        filtered = set()
        
        for keyword in keywords:
            # 공백 제거
            keyword = keyword.strip()
            
            # 빈 키워드 무시
            if not keyword:
                continue
            
            # 패턴 기반 필터링
            if any(re.match(pattern, keyword) for pattern in self.ignore_patterns):
                continue
            
            # 흔한 단어 필터링 (단독으로 사용 시)
            if keyword in self.common_words:
                continue
            
            # 최소 길이 검사 (한글 2자 이상, 영문 3자 이상)
            if re.match(r'^[가-힣]+$', keyword) and len(keyword) < 2:
                continue
            if re.match(r'^[a-zA-Z]+$', keyword) and len(keyword) < 3:
                continue
            
            filtered.add(keyword)
        
        return filtered
    
    def generate_combination_keywords(self, base_keywords: List[str], medicine_type_keywords: List[str] = None) -> List[str]:
        """
        키워드 조합으로 새 키워드 생성
        
        Args:
            base_keywords (list): 기본 키워드 목록
            medicine_type_keywords (list, optional): 의약품 형태 키워드 목록
            
        Returns:
            list: 생성된 조합 키워드 목록
        """
        if not base_keywords:
            return []
        
        # 기본 의약품 형태 키워드
        if medicine_type_keywords is None:
            medicine_type_keywords = ['정', '캡슐', '시럽', '주사', '연고', '크림', '액', '패치']
        
        combinations = []
        
        # 키워드 조합 생성
        for base in base_keywords:
            # 형태 키워드와 조합
            for type_keyword in medicine_type_keywords:
                combinations.append(f"{base} {type_keyword}")
            
            # 효능 관련 접미사 조합
            for suffix in ['치료제', '예방제', '약', '처방', '효능']:
                combinations.append(f"{base} {suffix}")
        
        return combinations