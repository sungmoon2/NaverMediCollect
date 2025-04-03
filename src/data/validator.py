#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NaverMediCollect - src/data/validator.py
생성일: 2025-04-03

의약품 데이터의 유효성을 검증하는 모듈입니다.
필수 필드 체크, 데이터 형식 검증 등의 기능을 제공합니다.
"""

import logging
import re
from conf.field_mapping import FIELD_MAPPING


class DataValidator:
    """데이터 유효성 검증 클래스"""
    
    def __init__(self):
        """초기화"""
        self.logger = logging.getLogger(__name__)
        self.field_mapping = FIELD_MAPPING
    
    def validate_medicine_data(self, medicine_data):
        """
        의약품 데이터 유효성 검증
        
        Args:
            medicine_data (dict): 검증할 의약품 데이터
            
        Returns:
            tuple: (유효성 여부, 오류 메시지)
        """
        if not medicine_data:
            return False, "데이터가 비어 있습니다."
        
        # 기본 정보 검증
        basic_info = medicine_data.get('basic_info', {})
        basic_validation = self._validate_basic_info(basic_info)
        
        if not basic_validation[0]:
            return basic_validation
        
        # 상세 정보 검증
        detailed_info = medicine_data.get('detailed_info', {})
        detailed_validation = self._validate_detailed_info(detailed_info)
        
        if not detailed_validation[0]:
            return detailed_validation
        
        return True, "유효한 데이터입니다."
    
    def _validate_basic_info(self, basic_info):
        """
        기본 정보 유효성 검증
        
        Args:
            basic_info (dict): 검증할 기본 정보
            
        Returns:
            tuple: (유효성 여부, 오류 메시지)
        """
        # 필수 필드 체크
        required_fields = ['medicine_id', 'name_ko']
        for field in required_fields:
            if field not in basic_info or not basic_info[field]:
                return False, f"필수 필드가 누락되었습니다: {field}"
        
        # 의약품 ID 형식 검증
        medicine_id = basic_info.get('medicine_id', '')
        if not re.match(r'^\d{9}$', medicine_id):
            return False, f"의약품 ID 형식이 잘못되었습니다: {medicine_id}"
        
        # 보험코드 형식 검증 (있는 경우)
        insurance_code = basic_info.get('insurance_code', '')
        if insurance_code and not re.match(r'^\d{9}$', insurance_code):
            return False, f"보험코드 형식이 잘못되었습니다: {insurance_code}"
        
        # 이미지 URL 검증 (있는 경우)
        image_url = basic_info.get('image_url', '')
        if image_url and not image_url.startswith(('http://', 'https://')):
            return False, f"이미지 URL 형식이 잘못되었습니다: {image_url}"
        
        return True, "기본 정보가 유효합니다."
    
    def _validate_detailed_info(self, detailed_info):
        """
        상세 정보 유효성 검증
        
        Args:
            detailed_info (dict): 검증할 상세 정보
            
        Returns:
            tuple: (유효성 여부, 오류 메시지)
        """
        # medicine_id 일치 여부 체크 (있는 경우)
        if 'medicine_id' in detailed_info:
            # 기본적인 형식 검증
            medicine_id = detailed_info.get('medicine_id', '')
            if not re.match(r'^\d{9}$', medicine_id):
                return False, f"상세 정보의 의약품 ID 형식이 잘못되었습니다: {medicine_id}"
        
        # HTML 컨텐츠 검증 (있는 경우)
        html_fields = [
            'effectiveness_html', 
            'dosage_html', 
            'precautions_html', 
            'professional_precautions_html'
        ]
        
        for field in html_fields:
            if field in detailed_info and detailed_info[field]:
                html_content = detailed_info[field]
                # 기본적인 HTML 검증
                if not html_content.strip().startswith('<'):
                    return False, f"HTML 컨텐츠 형식이 잘못되었습니다: {field}"
        
        return True, "상세 정보가 유효합니다."
    
    def check_missing_fields(self, medicine_data):
        """
        누락된 필드 확인
        
        Args:
            medicine_data (dict): 확인할 의약품 데이터
            
        Returns:
            list: 누락된 필드 목록
        """
        missing_fields = []
        
        # 기본 정보 필드 확인
        basic_info = medicine_data.get('basic_info', {})
        for field_key in self.field_mapping:
            # 기본 정보에 해당하는 필드만 확인
            if not field_key.startswith('detailed_'):
                if field_key not in basic_info or not basic_info[field_key]:
                    field_name = self.field_mapping[field_key].get('label', field_key)
                    missing_fields.append(field_name)
        
        # 상세 정보 필드 확인
        detailed_info = medicine_data.get('detailed_info', {})
        for field_key in self.field_mapping:
            # 상세 정보에 해당하는 필드만 확인
            if field_key.startswith('detailed_'):
                actual_key = field_key.replace('detailed_', '')
                if actual_key not in detailed_info or not detailed_info[actual_key]:
                    field_name = self.field_mapping[field_key].get('label', field_key)
                    missing_fields.append(field_name)
        
        return missing_fields
    
    def calculate_completion_percentage(self, medicine_data):
        """
        데이터 완성도 백분율 계산
        
        Args:
            medicine_data (dict): 계산할 의약품 데이터
            
        Returns:
            float: 완성도 백분율 (0-100)
        """
        total_fields = len(self.field_mapping)
        filled_fields = 0
        
        # 기본 정보 필드 계산
        basic_info = medicine_data.get('basic_info', {})
        for field_key in self.field_mapping:
            # 기본 정보에 해당하는 필드만 확인
            if not field_key.startswith('detailed_'):
                if field_key in basic_info and basic_info[field_key]:
                    filled_fields += 1
        
        # 상세 정보 필드 계산
        detailed_info = medicine_data.get('detailed_info', {})
        for field_key in self.field_mapping:
            # 상세 정보에 해당하는 필드만 확인
            if field_key.startswith('detailed_'):
                actual_key = field_key.replace('detailed_', '')
                if actual_key in detailed_info and detailed_info[actual_key]:
                    filled_fields += 1
        
        # 백분율 계산
        completion_percentage = (filled_fields / total_fields) * 100
        
        return round(completion_percentage, 2)