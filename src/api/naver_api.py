#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NaverMediCollect - src/api/naver_api.py
생성일: 2025-04-03

네이버 검색 API를 통해 의약품 정보를 검색하고 응답을 처리하는 모듈입니다.
API 인증, 요청 생성, 응답 파싱 등의 기능을 제공합니다.
"""

import os
import requests
import json
import time
import logging
import re
from datetime import datetime
from urllib.parse import quote
from tenacity import retry, stop_after_attempt, wait_exponential

from conf.settings import SETTINGS
from src.utils.safety import safe_request
from src.parsing.html_parser import HTMLParser


class NaverApiHandler:
    """네이버 검색 API 핸들링 클래스"""
    
    def __init__(self):
        """초기화 및 API 키 로드"""
        self.logger = logging.getLogger(__name__)
        
        # API 설정 로드
        self.client_id = os.environ.get('NAVER_CLIENT_ID')
        self.client_secret = os.environ.get('NAVER_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            self.logger.error("네이버 API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")
            raise ValueError("네이버 API 키가 필요합니다.")
        
        self.api_url = "https://openapi.naver.com/v1/search/encyc.json"
        self.headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
            "User-Agent": "NaverMediCollect/1.0"
        }
        
        # API 사용량 관리
        self.request_count = 0
        self.last_request_time = datetime.now()
        
        # HTML 파서 초기화
        self.html_parser = HTMLParser()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def search_keyword(self, keyword, display=100, start=1):
        """
        키워드를 네이버 검색 API를 통해 검색하고 결과를 반환합니다.
        
        Args:
            keyword (str): 검색할 키워드
            display (int): 한 번에 표시할 검색 결과 수 (최대 100)
            start (int): 검색 시작 위치
            
        Returns:
            list: 의약품 데이터 목록 (없으면 빈 리스트)
        """
        self.logger.info(f"키워드 '{keyword}' 검색 중...")
        
        # API 요청 제한 준수 (초당 10회 이하)
        self._respect_rate_limit()
        
        # 검색어 인코딩
        encoded_keyword = quote(keyword)
        params = {
            "query": encoded_keyword,
            "display": display,
            "start": start
        }
        
        # API 요청
        response = safe_request(
            method="GET",
            url=self.api_url,
            headers=self.headers,
            params=params
        )
        
        # 요청 카운트 증가
        self.request_count += 1
        self.last_request_time = datetime.now()
        
        if not response:
            self.logger.error(f"API 요청 실패: {keyword}")
            return []
        
        try:
            result_json = response.json()
            
            if not result_json.get('items'):
                self.logger.warning(f"검색 결과 없음: {keyword}")
                return []
            
            # 의약품 데이터 필터링 및 추출
            medicines = []
            for item in result_json.get('items', []):
                # 의약품 페이지 여부 확인
                if self._is_medicine_page(item):
                    medicine_data = self._parse_medicine_preview(item)
                    if medicine_data:
                        medicines.append(medicine_data)
            
            self.logger.info(f"'{keyword}' 검색 결과 {len(medicines)}건 찾음")
            return medicines
            
        except Exception as e:
            self.logger.exception(f"검색 결과 파싱 오류: {e}")
            return []
    
    def _respect_rate_limit(self):
        """API 요청 제한을 준수하기 위한 딜레이 추가"""
        current_time = datetime.now()
        elapsed = (current_time - self.last_request_time).total_seconds()
        
        # 초당 최대 5회 요청으로 제한
        if elapsed < 0.2:
            sleep_time = 0.2 - elapsed
            time.sleep(sleep_time)
    
    def _is_medicine_page(self, item):
        """
        검색 결과 항목이 의약품 페이지인지 확인
        
        Args:
            item (dict): 검색 결과 항목
            
        Returns:
            bool: 의약품 페이지 여부
        """
        # 제목에서 의약품 페이지 패턴 확인
        title = item.get('title', '')
        
        # HTML 태그 제거
        clean_title = re.sub('<[^<]+?>', '', title).strip()
        
        # 의약품 페이지 패턴
        medicine_patterns = [
            r'정$', r'캡슐$', r'연고$', r'주사$', r'시럽$', r'액$', r'산$', 
            r'주$', r'정제$', r'과립$', r'크림$', r'로션$', r'패치$', r'스프레이$'
        ]
        
        for pattern in medicine_patterns:
            if re.search(pattern, clean_title):
                return True
        
        # 설명(description)에서 확인
        description = item.get('description', '')
        
        medicine_keywords = [
            '전문의약품', '일반의약품', '소화성궤양용제', '항생제', '진통제',
            '효능효과', '용법용량', '사용상주의사항', '분류', '성상', '제형'
        ]
        
        for keyword in medicine_keywords:
            if keyword in description:
                return True
        
        return False
    
    def _parse_medicine_preview(self, item):
        """
        검색 결과에서 의약품 미리보기 데이터 추출
        
        Args:
            item (dict): 검색 결과 항목
            
        Returns:
            dict: 의약품 미리보기 데이터
        """
        # HTML 태그 제거
        title = re.sub('<[^<]+?>', '', item.get('title', '')).strip()
        description = item.get('description', '')
        link = item.get('link', '')
        
        # 의약품 ID 추출 (URL에서)
        medicine_id = None
        id_match = re.search(r'([0-9]{9})', link)
        if id_match:
            medicine_id = id_match.group(1)
        
        if not medicine_id:
            self.logger.warning(f"의약품 ID를 찾을 수 없음: {title}")
            return None
        
        return {
            'medicine_id': medicine_id,
            'title': title,
            'description': description,
            'link': link
        }
    
    def get_medicine_detail(self, medicine_id):
        """
        의약품 ID를 통해 상세 페이지 데이터 가져오기
        
        Args:
            medicine_id (str): 의약품 ID
            
        Returns:
            str: HTML 컨텐츠 (실패 시 None)
        """
        detail_url = f"https://terms.naver.com/entry.naver?docId={medicine_id}"
        
        self.logger.info(f"의약품 상세 데이터 요청: {medicine_id}")
        
        # API 요청 제한 준수
        self._respect_rate_limit()
        
        # 상세 페이지 요청
        response = safe_request(
            method="GET",
            url=detail_url,
            headers={"User-Agent": "NaverMediCollect/1.0"}
        )
        
        # 요청 카운트 증가
        self.request_count += 1
        self.last_request_time = datetime.now()
        
        if not response:
            self.logger.error(f"상세 페이지 요청 실패: {medicine_id}")
            return None
        
        return response.text