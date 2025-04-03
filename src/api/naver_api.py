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
        """
        self.logger.info(f"키워드 '{keyword}' 검색 중...")
        
        # API 요청 제한 준수
        self._respect_rate_limit()
        
        # 검색어 인코딩
        encoded_keyword = quote(keyword)
        params = {
            "query": encoded_keyword,
            "display": display,
            "start": start,
            "sort": "sim"  # 유사도순 정렬
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
            
            # 전체 검색 결과 로깅
            total_items = len(result_json.get('items', []))
            self.logger.info(f"검색 결과 전체 항목 수: {total_items}")
            
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
            
            self.logger.info(f"'{keyword}' 검색 결과 중 의약품 {len(medicines)}건 찾음")
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
        """
        # 제목에서 의약품 페이지 패턴 확인
        title = item.get('title', '')
        description = item.get('description', '')
        link = item.get('link', '')

        # HTML 태그 및 특수 문자 제거
        clean_title = re.sub('<[^<]+?>', '', title).strip()
        clean_description = re.sub('<[^<]+?>', '', description).strip()

        # 디버깅을 위한 로깅
        self.logger.debug(f"검색 항목 분석:")
        self.logger.debug(f"제목: {clean_title}")
        self.logger.debug(f"설명: {clean_description}")
        self.logger.debug(f"링크: {link}")
        
        # 의약품 관련 키워드 및 패턴 확장 (정규식 사용)
        medicine_name_patterns = [
            r'\b(타이레놀|아세트아미노펜|이부프로펜|아스피린)\b',  # 특정 약 이름
            r'\b(캡슐|정|주사|연고|시럽|액|패치|크림|스프레이)\b',  # 약 형태
            r'\b(제약|의약품|처방약|치료제)\b'  # 제약 관련 용어
        ]
        
        medicine_keywords = [
            '의약품', '약', '처방', '복용', '용법', '용량', 
            '효능', '효과', '부작용', '성분', '투여', '치료'
        ]

        # 제목 및 설명에서 의약품 관련 패턴 검색
        for pattern in medicine_name_patterns:
            if re.search(pattern, clean_title, re.IGNORECASE) or \
            re.search(pattern, clean_description, re.IGNORECASE):
                self.logger.debug(f"패턴 매칭 성공: {pattern}")
                return True
        
        # 키워드 확인
        for keyword in medicine_keywords:
            if keyword in clean_title or keyword in clean_description:
                self.logger.debug(f"키워드 매칭 성공: {keyword}")
                return True
        
        # 링크 패턴 확인
        if re.search(r'terms\.naver\.com', link):
            self.logger.debug("terms.naver.com 링크 매칭")
            return True
        
        # 디버깅을 위해 로깅
        self.logger.debug("의약품 페이지로 판단되지 않음")
        
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