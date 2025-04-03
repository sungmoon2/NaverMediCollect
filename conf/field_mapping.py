#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NaverMediCollect - conf/field_mapping.py
생성일: 2025-04-03

의약품 페이지의 필드 매핑 정보를 제공하는 모듈입니다.
HTML 선택자, 레이블 등의 필드 매핑 정보를 정의합니다.
"""

from typing import Dict, Any


# 필드 매핑 설정
FIELD_MAPPING: Dict[str, Dict[str, Any]] = {
    # 기본 정보 필드
    'name_ko': {
        'label': '약품명(한글명)',
        'selector': 'div.headword_title > h2.headword',
        'post_processor': 'clean_medicine_name'
    },
    'name_en': {
        'label': '약품명(영문명)',
        'selector': 'div.headword_title > p.word > span.word_txt'
    },
    'image_url': {
        'label': '이미지',
        'selector': 'span.img_box > a > img',
        'attribute': 'origin_src'  # origin_src 속성 우선 사용
    },
    'category': {
        'label': '분류',
        'selector': 'table.tmp_profile_tb tr:contains("분류") > td'
    },
    'type': {
        'label': '구분',
        'selector': 'table.tmp_profile_tb tr:contains("구분") > td'
    },
    'company': {
        'label': '업체명',
        'selector': 'table.tmp_profile_tb tr:contains("업체명") > td'
    },
    'insurance_code': {
        'label': '보험코드',
        'selector': 'table.tmp_profile_tb tr:contains("보험코드") > td'
    },
    'appearance': {
        'label': '성상',
        'selector': 'table.tmp_profile_tb tr:contains("성상") > td'
    },
    'formulation': {
        'label': '제형',
        'selector': 'table.tmp_profile_tb tr:contains("제형") > td'
    },
    'shape': {
        'label': '모양',
        'selector': 'table.tmp_profile_tb tr:contains("모양") > td'
    },
    'color': {
        'label': '색깔',
        'selector': 'table.tmp_profile_tb tr:contains("색깔") > td',
        'post_processor': 'extract_color'
    },
    'size': {
        'label': '크기',
        'selector': 'table.tmp_profile_tb tr:contains("크기") > td',
        'post_processor': 'extract_size'
    },
    'identification': {
        'label': '식별표기',
        'selector': 'table.tmp_profile_tb tr:contains("식별표기") > td',
        'post_processor': 'extract_identification'
    },
    'dividing_line': {
        'label': '분할선',
        'selector': 'table.tmp_profile_tb tr:contains("분할선") > td'
    },
    'ingredient_info': {
        'label': '성분정보',
        'selector': 'h3.stress#TABLE_OF_CONTENT1 + p.txt'
    },
    'storage_method': {
        'label': '저장방법',
        'selector': 'h3.stress#TABLE_OF_CONTENT4 + p.txt'
    },
    'usage_period': {
        'label': '사용기간',
        'selector': 'h3.stress#TABLE_OF_CONTENT5 + p.txt'
    },
    
    # 상세 정보 필드
    'detailed_effectiveness': {
        'label': '효능효과',
        'selector': 'h3.stress#TABLE_OF_CONTENT2 + p.txt'
    },
    'detailed_dosage': {
        'label': '용법용량',
        'selector': 'h3.stress#TABLE_OF_CONTENT3 + p.txt'
    },
    'detailed_precautions': {
        'label': '사용상의주의사항',
        'selector': 'h3.stress#TABLE_OF_CONTENT6 + p.txt'
    },
    'detailed_professional_precautions': {
        'label': '사용상의주의사항(전문가)',
        'selector': 'h3.stress#TABLE_OF_CONTENT7 + p.txt'
    }
}


# 필드 그룹 정의
FIELD_GROUPS = {
    'basic_info': [
        'name_ko', 'name_en', 'image_url', 'category', 'type', 'company',
        'insurance_code', 'appearance', 'formulation', 'shape', 'color',
        'size', 'identification', 'dividing_line', 'ingredient_info',
        'storage_method', 'usage_period'
    ],
    'detailed_info': [
        'detailed_effectiveness', 'detailed_dosage',
        'detailed_precautions', 'detailed_professional_precautions'
    ]
}


# 필수 필드 정의
REQUIRED_FIELDS = [
    'name_ko',
    'medicine_id'
]


# 필드 색인 (레이블 → 키)
FIELD_INDEX = {mapping['label']: key for key, mapping in FIELD_MAPPING.items()}


def get_field_key_by_label(label: str) -> str:
    """
    레이블로 필드 키 조회
    
    Args:
        label (str): 필드 레이블
        
    Returns:
        str: 필드 키 (없으면 빈 문자열)
    """
    return FIELD_INDEX.get(label, '')


def get_field_label(field_key: str) -> str:
    """
    필드 키로 레이블 조회
    
    Args:
        field_key (str): 필드 키
        
    Returns:
        str: 필드 레이블 (없으면 필드 키)
    """
    field_config = FIELD_MAPPING.get(field_key)
    if field_config and 'label' in field_config:
        return field_config['label']
    return field_key


def get_selector(field_key: str) -> str:
    """
    필드 키로 선택자 조회
    
    Args:
        field_key (str): 필드 키
        
    Returns:
        str: CSS 선택자 (없으면 빈 문자열)
    """
    field_config = FIELD_MAPPING.get(field_key)
    if field_config and 'selector' in field_config:
        return field_config['selector']
    return ''