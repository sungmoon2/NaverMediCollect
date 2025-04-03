#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NaverMediCollect - tests/test_extractor.py
생성일: 2025-04-03

데이터 추출기 테스트 모듈입니다.
HTML에서 의약품 데이터 추출 기능을 테스트합니다.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import json
from bs4 import BeautifulSoup

# 상위 디렉토리를 파이썬 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.extractor import DataExtractor


class TestDataExtractor(unittest.TestCase):
    """데이터 추출기 테스트 클래스"""
    
    def setUp(self):
        """테스트 준비"""
        # 추출기 인스턴스 생성
        self.extractor = DataExtractor()
        
        # 테스트 데이터 로드
        self.test_html = self._load_test_html()
        self.test_medicine_preview = {
            'medicine_id': '123456789',
            'title': '케이캡정50mg',
            'description': '전문의약품 소화성궤양용제',
            'link': 'https://terms.naver.com/entry.naver?docId=123456789'
        }
    
    def _load_test_html(self):
        """테스트 HTML 로드"""
        # 테스트 HTML 파일 경로
        fixture_path = os.path.join(
            os.path.dirname(__file__), 
            'fixtures', 
            'sample_responses', 
            'medicine_detail.html'
        )
        
        # 테스트 HTML 파일이 없으면 간단한 HTML 반환
        if not os.path.exists(fixture_path):
            return """
            <html>
                <head><title>테스트 의약품 페이지</title></head>
                <body>
                    <div class="headword_title">
                        <h2 class="headword">케이캡정50mg(테고프라잔)</h2>
                        <p class="word"><span class="word_txt">K-CAB Tab. 50mg</span></p>
                    </div>
                    <span class="img_box">
                        <a href="#"><img src="medicine.jpg" origin_src="medicine_large.jpg" alt="약품이미지" /></a>
                    </span>
                    <table class="tmp_profile_tb">
                        <tbody>
                            <tr><th>분류</th><td>[02320]소화성궤양용제</td></tr>
                            <tr><th>구분</th><td>전문의약품</td></tr>
                            <tr><th>업체명</th><td>에이치케이이노엔(주)</td></tr>
                            <tr><th>성상</th><td>연한 분홍색의 장방형 필름코팅정</td></tr>
                        </tbody>
                    </table>
                    <h3 class="stress" id="TABLE_OF_CONTENT1">성분정보</h3>
                    <p class="txt">테고프라잔 50.0mg</p>
                    <h3 class="stress" id="TABLE_OF_CONTENT2">효능효과</h3>
                    <p class="txt">위식도역류질환의 치료</p>
                    <h3 class="stress" id="TABLE_OF_CONTENT3">용법용량</h3>
                    <p class="txt">1일 1회, 1회 50mg을 경구투여</p>
                    <h3 class="stress" id="TABLE_OF_CONTENT4">저장방법</h3>
                    <p class="txt">기밀용기, 실온(1~30℃)보관</p>
                    <h3 class="stress" id="TABLE_OF_CONTENT5">사용기간</h3>
                    <p class="txt">제조일로부터 36 개월</p>
                    <h3 class="stress" id="TABLE_OF_CONTENT6">사용상의주의사항</h3>
                    <p class="txt">이 약을 투여하기 전 충분한 문진을 통해 과거 병력을 확인한다.</p>
                </body>
            </html>
            """
        
        # 테스트 HTML 파일 로드
        try:
            with open(fixture_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            # 파일 로드 실패 시 간단한 HTML 반환
            return """<html><body>테스트 의약품 페이지</body></html>"""
    
    @patch('src.api.naver_api.NaverApiHandler.get_medicine_detail')
    def test_extract_medicine_data(self, mock_get_medicine_detail):
        """의약품 데이터 추출 테스트"""
        # Mock 응답 설정
        mock_get_medicine_detail.return_value = self.test_html
        
        # 메서드 호출
        result = self.extractor.extract_medicine_data(self.test_medicine_preview)
        
        # 검증
        self.assertIsNotNone(result)
        self.assertEqual(result['medicine_id'], '123456789')
        self.assertIn('basic_info', result)
        self.assertIn('detailed_info', result)
        
        # 기본 정보 검증
        basic_info = result['basic_info']
        self.assertEqual(basic_info.get('medicine_id'), '123456789')
        self.assertIn('name_ko', basic_info)
        
        # 상세 정보 검증
        detailed_info = result['detailed_info']
        self.assertEqual(detailed_info.get('medicine_id'), '123456789')
    
    def test_extract_basic_info(self):
        """기본 정보 추출 테스트"""
        # HTML 파싱
        soup = BeautifulSoup(self.test_html, 'html.parser')
        
        # 메서드 호출
        basic_info = self.extractor._extract_basic_info(soup, '123456789')
        
        # 검증
        self.assertIsNotNone(basic_info)
        self.assertEqual(basic_info.get('medicine_id'), '123456789')
        self.assertIn('name_ko', basic_info)
        self.assertIn('name_en', basic_info)
        if 'image_url' in basic_info:
            self.assertTrue(basic_info.get('image_url').endswith('.jpg'))
    
    def test_extract_detailed_info(self):
        """상세 정보 추출 테스트"""
        # HTML 파싱
        soup = BeautifulSoup(self.test_html, 'html.parser')
        
        # 메서드 호출
        detailed_info = self.extractor._extract_detailed_info(soup, '123456789')
        
        # 검증
        self.assertIsNotNone(detailed_info)
        self.assertEqual(detailed_info.get('medicine_id'), '123456789')
        self.assertIn('effectiveness', detailed_info)
        self.assertIn('dosage', detailed_info)
        self.assertIn('precautions', detailed_info)
    
    def test_evaluate_extraction_status(self):
        """추출 상태 평가 테스트"""
        # 성공 케이스
        basic_info_success = {
            'medicine_id': '123456789',
            'name_ko': '케이캡정50mg',
            'name_en': 'K-CAB Tab. 50mg',
            'category': '[02320]소화성궤양용제',
            'type': '전문의약품',
            'company': '에이치케이이노엔(주)',
            'ingredient_info': '테고프라잔 50.0mg'
        }
        
        detailed_info_success = {
            'medicine_id': '123456789',
            'effectiveness': '위식도역류질환의 치료',
            'dosage': '1일 1회, 1회 50mg을 경구투여',
            'precautions': '이 약을 투여하기 전 충분한 문진을 통해 과거 병력을 확인한다.'
        }
        
        status_success = self.extractor._evaluate_extraction_status(
            basic_info_success, detailed_info_success
        )
        self.assertEqual(status_success, 'success')
        
        # 부분 성공 케이스
        basic_info_partial = {
            'medicine_id': '123456789',
            'name_ko': '케이캡정50mg',
            'category': '[02320]소화성궤양용제',
            'type': '전문의약품'
        }
        
        detailed_info_partial = {
            'medicine_id': '123456789',
            'effectiveness': '위식도역류질환의 치료'
        }
        
        status_partial = self.extractor._evaluate_extraction_status(
            basic_info_partial, detailed_info_partial
        )
        self.assertEqual(status_partial, 'partial')
        
        # 실패 케이스
        basic_info_failed = {
            'medicine_id': '123456789'
        }
        
        detailed_info_failed = {
            'medicine_id': '123456789'
        }
        
        status_failed = self.extractor._evaluate_extraction_status(
            basic_info_failed, detailed_info_failed
        )
        self.assertEqual(status_failed, 'failed')
    
    def test_count_extracted_fields(self):
        """추출된 필드 수 계산 테스트"""
        # 테스트 데이터
        medicine_data = {
            'medicine_id': '123456789',
            'basic_info': {
                'medicine_id': '123456789',
                'name_ko': '케이캡정50mg',
                'name_en': 'K-CAB Tab. 50mg',
                'category': '[02320]소화성궤양용제',
                'type': '전문의약품',
                'empty_field': ''
            },
            'detailed_info': {
                'medicine_id': '123456789',
                'effectiveness': '위식도역류질환의 치료',
                'dosage': '1일 1회, 1회 50mg을 경구투여',
                'effectiveness_html': '<p>위식도역류질환의 치료</p>',
                'empty_field': ''
            }
        }
        
        # 메서드 호출
        field_count = self.extractor._count_extracted_fields(medicine_data)
        
        # 검증 (비어있지 않은 필드만 카운트, medicine_id와 _html 필드 제외)
        self.assertEqual(field_count, 5)
    
    def test_extract_keywords_from_data(self):
        """데이터에서 키워드 추출 테스트"""
        # 테스트 데이터
        medicine_data = {
            'basic_info': {
                'medicine_id': '123456789',
                'name_ko': '케이캡정50mg',
                'category': '[02320]소화성궤양용제',
                'company': '에이치케이이노엔(주)',
                'ingredient_info': '테고프라잔 50.0mg'
            },
            'detailed_info': {
                'medicine_id': '123456789',
                'effectiveness': '위식도역류질환의 치료'
            }
        }
        
        # 메서드 호출
        keywords = self.extractor.extract_keywords_from_data(medicine_data)
        
        # 검증
        self.assertIsInstance(keywords, list)
        self.assertTrue(len(keywords) > 0)
        
        # 예상 키워드가 포함되어 있는지 확인
        expected_keywords = ['소화성궤양용제', '에이치케이이노엔', '테고프라잔']
        for keyword in expected_keywords:
            found = False
            for extracted_keyword in keywords:
                if keyword in extracted_keyword:
                    found = True
                    break
            self.assertTrue(found, f"키워드 '{keyword}'가 추출 결과에 없습니다.")


if __name__ == '__main__':
    unittest.main()