#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NaverMediCollect - tests/test_parser.py
생성일: 2025-04-03

HTML 파서 및 구조 보존 테스트 모듈입니다.
HTML 파싱, 선택자 처리, 구조 보존 등의 기능을 테스트합니다.
"""

import os
import sys
import unittest
from bs4 import BeautifulSoup

# 상위 디렉토리를 파이썬 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.parsing.html_parser import HTMLParser
from src.parsing.structure_preserver import HTMLStructurePreserver
from src.parsing.field_mapper import FieldMapper


class TestHTMLParser(unittest.TestCase):
    """HTML 파서 테스트 클래스"""
    
    def setUp(self):
        """테스트 준비"""
        # 파서 인스턴스 생성
        self.parser = HTMLParser()
        
        # 테스트 HTML
        self.test_html = """
        <html>
            <head><title>테스트 의약품 페이지</title></head>
            <body>
                <div class="headword_title">
                    <h2 class="headword">케이캡정50mg(테고프라잔)</h2>
                    <p class="word"><span class="word_txt">K-CAB Tab. 50mg</span></p>
                </div>
                <table class="tmp_profile_tb">
                    <tbody>
                        <tr><th>분류</th><td>[02320]소화성궤양용제</td></tr>
                        <tr><th>구분</th><td>전문의약품</td></tr>
                        <tr><th>업체명</th><td>에이치케이이노엔(주)</td></tr>
                    </tbody>
                </table>
                <h3 class="stress" id="TABLE_OF_CONTENT1">성분정보</h3>
                <p class="txt">테고프라잔 50.0mg</p>
            </body>
        </html>
        """
        
        # HTML 파싱
        self.soup = self.parser.parse_html(self.test_html)
    
    def test_parse_html(self):
        """HTML 파싱 테스트"""
        # 검증
        self.assertIsNotNone(self.soup)
        self.assertIsInstance(self.soup, BeautifulSoup)
        self.assertEqual(self.soup.title.string, "테스트 의약품 페이지")
    
    def test_select_element(self):
        """요소 선택 테스트"""
        # 케이스 1: 존재하는 요소
        element = self.parser.select_element(self.soup, 'h2.headword')
        self.assertIsNotNone(element)
        self.assertEqual(element.string, "케이캡정50mg(테고프라잔)")
        
        # 케이스 2: 존재하지 않는 요소
        element = self.parser.select_element(self.soup, 'h2.nonexistent')
        self.assertIsNone(element)
    
    def test_select_elements(self):
        """여러 요소 선택 테스트"""
        # 케이스 1: 존재하는 요소들
        elements = self.parser.select_elements(self.soup, 'tr')
        self.assertEqual(len(elements), 3)
        
        # 케이스 2: 존재하지 않는 요소들
        elements = self.parser.select_elements(self.soup, 'table.nonexistent')
        self.assertEqual(len(elements), 0)
    
    def test_extract_text(self):
        """텍스트 추출 테스트"""
        # 케이스 1: 텍스트가 있는 요소
        element = self.parser.select_element(self.soup, 'h2.headword')
        text = self.parser.extract_text(element)
        self.assertEqual(text, "케이캡정50mg(테고프라잔)")
        
        # 케이스 2: None 요소
        text = self.parser.extract_text(None)
        self.assertEqual(text, "")
    
    def test_extract_attribute(self):
        """속성 추출 테스트"""
        # 케이스 1: 속성이 있는 요소
        element = self.parser.select_element(self.soup, 'h3.stress')
        attr = self.parser.extract_attribute(element, 'id')
        self.assertEqual(attr, "TABLE_OF_CONTENT1")
        
        # 케이스 2: 속성이 없는 요소
        element = self.parser.select_element(self.soup, 'h2.headword')
        attr = self.parser.extract_attribute(element, 'data-nonexistent')
        self.assertEqual(attr, "")
    
    def test_extract_profile_table_data(self):
        """프로필 테이블 데이터 추출 테스트"""
        # 메서드 호출
        profile_data = self.parser.extract_profile_table_data(self.soup)
        
        # 검증
        self.assertIsNotNone(profile_data)
        self.assertEqual(profile_data.get('분류'), '[02320]소화성궤양용제')
        self.assertEqual(profile_data.get('구분'), '전문의약품')
        self.assertEqual(profile_data.get('업체명'), '에이치케이이노엔(주)')
    
    def test_find_section(self):
        """섹션 찾기 테스트"""
        # 메서드 호출
        section = self.parser.find_section(self.soup, '성분정보')
        
        # 검증
        self.assertIsNotNone(section)
        self.assertIn('title_element', section)
        self.assertIn('content_element', section)
        self.assertIn('text', section)
        self.assertEqual(section['text'], '테고프라잔 50.0mg')


class TestHTMLStructurePreserver(unittest.TestCase):
    """HTML 구조 보존 테스트 클래스"""
    
    def setUp(self):
        """테스트 준비"""
        # 구조 보존기 인스턴스 생성
        self.preserver = HTMLStructurePreserver()
        
        # HTML 파서 인스턴스
        self.parser = HTMLParser()
        
        # 테스트 HTML
        self.test_html = """
        <div>
            <h3>사용상의주의사항</h3>
            <p class="txt">
                <b>경고</b>
                <ol>
                    <li>이 약은 어린이의 손이 닿지 않는 곳에 보관한다.</li>
                    <li>다음 환자에는 투여하지 말 것:
                        <ul>
                            <li>이 약의 성분에 과민증이 있는 환자</li>
                            <li>중증 간장애 환자</li>
                        </ul>
                    </li>
                </ol>
                <table border="1">
                    <tr>
                        <th>분류</th>
                        <th>주의사항</th>
                    </tr>
                    <tr>
                        <td>임부</td>
                        <td>안전성이 확립되어 있지 않으므로 투여하지 않는다.</td>
                    </tr>
                </table>
            </p>
        </div>
        """
        
        # HTML 파싱
        self.soup = self.parser.parse_html(self.test_html)
        self.content_element = self.parser.select_element(self.soup, 'p.txt')
    
    def test_preserve_html_structure(self):
        """HTML 구조 보존 테스트"""
        # 메서드 호출
        preserved_html = self.preserver.preserve_html_structure(self.content_element)
        
        # 검증
        self.assertIsNotNone(preserved_html)
        self.assertIn('<b>경고</b>', preserved_html)
        self.assertIn('<ol>', preserved_html)
        self.assertIn('<li>', preserved_html)
        self.assertIn('<table', preserved_html)
        self.assertIn('<tr>', preserved_html)
        self.assertIn('<th>', preserved_html)
        self.assertIn('<td>', preserved_html)
    
    def test_preserve_table_structure(self):
        """테이블 구조 보존 테스트"""
        # 테이블 요소 선택
        table_element = self.parser.select_element(self.content_element, 'table')
        
        # 메서드 호출
        preserved_table = self.preserver.preserve_table_structure(table_element)
        
        # 검증
        self.assertIsNotNone(preserved_table)
        self.assertIn('<tr>', preserved_table)
        self.assertIn('<th>', preserved_table)
        self.assertIn('<td>', preserved_table)
    
    def test_preserve_list_structure(self):
        """목록 구조 보존 테스트"""
        # 목록 요소 선택
        list_element = self.parser.select_element(self.content_element, 'ol')
        
        # 메서드 호출
        preserved_list = self.preserver.preserve_list_structure(list_element)
        
        # 검증
        self.assertIsNotNone(preserved_list)
        self.assertIn('<ol>', preserved_list)
        self.assertIn('<li>', preserved_list)
        self.assertIn('<ul>', preserved_list)
    
    def test_sanitize_html(self):
        """HTML 살균 테스트"""
        # 위험한 HTML
        unsafe_html = """
        <div>
            <p>안전한 내용</p>
            <script>alert('위험!');</script>
            <iframe src="http://example.com"></iframe>
            <a href="javascript:alert('위험!');">위험한 링크</a>
            <img src="data:image/svg+xml,%3Csvg onload='alert(1)'%3E" />
        </div>
        """
        
        # 메서드 호출
        sanitized_html = self.preserver._sanitize_html(unsafe_html)
        
        # 검증
        self.assertIsNotNone(sanitized_html)
        self.assertIn('<p>안전한 내용</p>', sanitized_html)
        self.assertNotIn('<script>', sanitized_html)
        self.assertNotIn('alert', sanitized_html)
        self.assertNotIn('<iframe', sanitized_html)
        self.assertNotIn('javascript:', sanitized_html)


class TestFieldMapper(unittest.TestCase):
    """필드 매퍼 테스트 클래스"""
    
    def setUp(self):
        """테스트 준비"""
        # 매퍼 인스턴스 생성
        self.mapper = FieldMapper()
        
        # HTML 파서 인스턴스
        self.parser = HTMLParser()
        
        # 테스트 HTML
        self.test_html = """
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
                        <tr><th>크기</th><td>(장축)11.4, (단축)5.2, (두께)3.5</td></tr>
                        <tr><th>색깔</th><td>분홍</td></tr>
                        <tr><th>식별표기</th><td>K분할선50</td></tr>
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
            </body>
        </html>
        """
        
        # HTML 파싱
        self.soup = self.parser.parse_html(self.test_html)
    
    def test_map_all_fields(self):
        """모든 필드 매핑 테스트"""
        # 메서드 호출
        mapped_data = self.mapper.map_all_fields(self.soup, '123456789')
        
        # 검증
        self.assertIsNotNone(mapped_data)
        self.assertIn('basic_info', mapped_data)
        self.assertIn('detailed_info', mapped_data)
        
        # 기본 정보 검증
        basic_info = mapped_data['basic_info']
        self.assertEqual(basic_info.get('medicine_id'), '123456789')
        self.assertEqual(basic_info.get('name_ko'), '케이캡정50mg(테고프라잔)')
        self.assertEqual(basic_info.get('name_en'), 'K-CAB Tab. 50mg')
        self.assertEqual(basic_info.get('image_url'), 'medicine_large.jpg')
        self.assertEqual(basic_info.get('category'), '[02320]소화성궤양용제')
        self.assertEqual(basic_info.get('type'), '전문의약품')
        
        # 상세 정보 검증
        detailed_info = mapped_data['detailed_info']
        self.assertEqual(detailed_info.get('medicine_id'), '123456789')
        self.assertEqual(detailed_info.get('effectiveness'), '위식도역류질환의 치료')
        self.assertEqual(detailed_info.get('dosage'), '1일 1회, 1회 50mg을 경구투여')
    
    def test_extract_field(self):
        """필드 추출 테스트"""
        # 필드 설정
        field_config = {
            'label': '약품명(한글명)',
            'selector': 'div.headword_title > h2.headword'
        }
        
        # 메서드 호출
        field_value = self.mapper._extract_field(self.soup, field_config)
        
        # 검증
        self.assertEqual(field_value, '케이캡정50mg(테고프라잔)')
    
    def test_extract_field_with_attribute(self):
        """속성이 있는 필드 추출 테스트"""
        # 필드 설정
        field_config = {
            'label': '이미지',
            'selector': 'span.img_box > a > img',
            'attribute': 'origin_src'
        }
        
        # 메서드 호출
        field_value = self.mapper._extract_field(self.soup, field_config)
        
        # 검증
        self.assertEqual(field_value, 'medicine_large.jpg')
    
    def test_extract_field_with_post_processor(self):
        """후처리가 있는 필드 추출 테스트"""
        # 필드 설정
        field_config = {
            'label': '크기',
            'selector': 'table.tmp_profile_tb tr:contains("크기") > td',
            'post_processor': 'extract_size'
        }
        
        # 메서드 호출
        field_value = self.mapper._extract_field(self.soup, field_config)
        
        # 검증
        self.assertTrue('장축' in field_value)
        self.assertTrue('단축' in field_value)
        self.assertTrue('두께' in field_value)
    
    def test_extract_field_html(self):
        """HTML 필드 추출 테스트"""
        # 필드 설정
        field_config = {
            'label': '효능효과',
            'selector': 'h3.stress#TABLE_OF_CONTENT2 + p.txt'
        }
        
        # 메서드 호출
        html_value = self.mapper._extract_field_html(self.soup, field_config)
        
        # 검증
        self.assertIsNotNone(html_value)
        self.assertIn('<p class="txt">위식도역류질환의 치료</p>', html_value)


if __name__ == '__main__':
    unittest.main()