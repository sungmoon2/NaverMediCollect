#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NaverMediCollect - tests/test_api.py
생성일: 2025-04-03

네이버 API 핸들러 테스트 모듈입니다.
API 요청, 응답 처리 등의 기능을 테스트합니다.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import json
import requests

# 상위 디렉토리를 파이썬 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 환경 변수 설정 (Mock 응답을 사용하므로 실제 API에 연결되지 않음)
os.environ['NAVER_CLIENT_ID'] = 'test_client_id'
os.environ['NAVER_CLIENT_SECRET'] = 'test_client_secret'

from src.api.naver_api import NaverApiHandler


class TestNaverApiHandler(unittest.TestCase):
    """네이버 API 핸들러 테스트 클래스"""
    
    def setUp(self):
        """테스트 준비"""
        # API 핸들러 인스턴스 생성
        self.api_handler = NaverApiHandler()
    
    @patch('src.utils.safety.safe_request')
    def test_search_keyword_success(self, mock_safe_request):
        """키워드 검색 성공 테스트"""
        # Mock 응답 설정
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'items': [
                {
                    'title': '케이캡정50mg',
                    'description': '전문의약품 소화성궤양용제',
                    'link': 'https://terms.naver.com/entry.naver?docId=123456789'
                }
            ]
        }
        mock_safe_request.return_value = mock_response
        
        # 메서드 호출
        results = self.api_handler.search_keyword("소화제")
        
        # 검증
        self.assertIsNotNone(results)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['medicine_id'], '123456789')
        
        # Mock 호출 검증
        mock_safe_request.assert_called_once()
    
    @patch('src.utils.safety.safe_request')
    def test_search_keyword_empty_result(self, mock_safe_request):
        """빈 검색 결과 테스트"""
        # Mock 응답 설정
        mock_response = MagicMock()
        mock_response.json.return_value = {'items': []}
        mock_safe_request.return_value = mock_response
        
        # 메서드 호출
        results = self.api_handler.search_keyword("존재하지않는키워드")
        
        # 검증
        self.assertEqual(results, [])
    
    @patch('src.utils.safety.safe_request')
    def test_search_keyword_api_failure(self, mock_safe_request):
        """API 실패 테스트"""
        # Mock 응답 설정
        mock_safe_request.return_value = None
        
        # 메서드 호출
        results = self.api_handler.search_keyword("소화제")
        
        # 검증
        self.assertEqual(results, [])
    
    def test_is_medicine_page(self):
        """의약품 페이지 식별 테스트"""
        # 의약품 페이지인 경우
        medicine_item = {
            'title': '케이캡정50mg',
            'description': '전문의약품 소화성궤양용제'
        }
        self.assertTrue(self.api_handler._is_medicine_page(medicine_item))
        
        # 의약품 페이지가 아닌 경우
        non_medicine_item = {
            'title': '소화제 관련 정보',
            'description': '건강 정보 백과사전'
        }
        self.assertFalse(self.api_handler._is_medicine_page(non_medicine_item))
    
    def test_parse_medicine_preview(self):
        """의약품 미리보기 데이터 추출 테스트"""
        # 테스트 아이템
        item = {
            'title': '케이캡정50mg',
            'description': '전문의약품 소화성궤양용제',
            'link': 'https://terms.naver.com/entry.naver?docId=123456789'
        }
        
        # 메서드 호출
        result = self.api_handler._parse_medicine_preview(item)
        
        # 검증
        self.assertIsNotNone(result)
        self.assertEqual(result['medicine_id'], '123456789')
        self.assertEqual(result['title'], '케이캡정50mg')
        self.assertEqual(result['description'], '전문의약품 소화성궤양용제')
    
    @patch('src.utils.safety.safe_request')
    def test_get_medicine_detail(self, mock_safe_request):
        """의약품 상세 데이터 가져오기 테스트"""
        # Mock 응답 설정
        mock_response = MagicMock()
        mock_response.text = '<html><body>Medicine Detail</body></html>'
        mock_safe_request.return_value = mock_response
        
        # 메서드 호출
        result = self.api_handler.get_medicine_detail('123456789')
        
        # 검증
        self.assertEqual(result, '<html><body>Medicine Detail</body></html>')
        
        # Mock 호출 검증
        mock_safe_request.assert_called_once()


if __name__ == '__main__':
    unittest.main()